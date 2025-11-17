"""
Medical Record Service - 醫療記錄相關業務邏輯
"""
from datetime import datetime, date, timedelta
from flask import current_app
from app import db
from app.models.medical_record import MedicalRecord, RecordType
from app.models.animal import Animal, AnimalStatus
from app.models.user import User, UserRole
from sqlalchemy import or_, and_, func
from sqlalchemy.sql import exists


class MedicalRecordService:
    """醫療記錄業務邏輯服務"""

    @staticmethod
    def check_animal_permission(user_id, animal, operation='view'):
        """
        檢查用戶對動物的權限
        
        Args:
            user_id: 用戶ID
            animal: 動物對象
            operation: 操作類型 ('view', 'create', 'update', 'verify')
        
        Returns:
            User: 用戶對象
            
        Raises:
            ValueError: 無權限或用戶不存在
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('用戶不存在')
        
        # 管理員有完全權限，但不能直接編輯醫療記錄
        if user.role == UserRole.ADMIN:
            if operation == 'update':
                raise ValueError('管理員無法直接編輯醫療記錄，請使用"標記需要修正"功能通知相關人員')
            return user
        
        # 一般用戶和收容所成員的權限檢查
        if user.role == UserRole.SHELTER_MEMBER:
            # 收容所成員可以存取：
            # 1. 自己擁有的動物
            # 2. 所屬收容所的動物
            if (animal.owner_id == user_id or 
                (animal.shelter_id and user.primary_shelter_id == animal.shelter_id)):
                return user
        else:
            # 一般用戶只能存取自己的動物
            if animal.owner_id == user_id:
                return user
        
        # 檢視是公開端點
        if operation == 'view':
            return user  # 公開端點允許所有用戶查看
        
        raise ValueError(f'無權限執行{operation}操作')

    @staticmethod
    def check_record_permission(user_id, record, operation='view'):
        """
        檢查用戶對醫療記錄的權限
        
        Args:
            user_id: 用戶ID
            record: 醫療記錄對象
            operation: 操作類型 ('view', 'update', 'verify')
        
        Returns:
            User: 用戶對象
            
        Raises:
            ValueError: 無權限或用戶不存在
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('用戶不存在')
            
        # 管理員可以驗證但不能編輯
        if user.role == UserRole.ADMIN:
            if operation == 'verify':
                return user
            elif operation == 'update':
                raise ValueError('管理員無法直接編輯醫療記錄')
            return user
            
        # 獲取動物資料
        animal = Animal.query.get(record.animal_id)
        if not animal:
            raise ValueError('相關動物不存在')
            
        # 更新權限檢查
        if operation == 'update':
            # 醫療記錄創建者（24小時內）
            if record.created_by == user_id:
                if record.created_at and datetime.utcnow() - record.created_at <= timedelta(hours=24):
                    return user
                else:
                    raise ValueError('醫療記錄創建者只能在24小時內修改')
            
            # 動物擁有者
            if animal.owner_id == user_id:
                return user
                
            # 收容所成員（該收容所的動物）
            if (user.role == UserRole.SHELTER_MEMBER and 
                animal.shelter_id and 
                user.primary_shelter_id == animal.shelter_id):
                return user
                
            raise ValueError('僅創建者(24小時內)、動物擁有者或收容所成員可更新醫療記錄')
        
        # 查看權限（公開端點）
        return user

    @staticmethod
    def list_animals_for_medical_records(user_id, filters=None):
        """
        獲取當前用戶有權限管理醫療記錄的動物列表
        
        Args:
            user_id: 用戶ID
            filters: 篩選條件
        
        Returns:
            dict: 動物列表數據
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('用戶不存在')
                
            filters = filters or {}
            
            # 基本查詢：排除已刪除的動物
            query = Animal.query.filter_by(deleted_at=None)
            
            # 權限篩選
            if user.role == UserRole.ADMIN:
                # 管理員可以看到所有動物
                pass
            elif user.role == UserRole.SHELTER_MEMBER:
                # 收容所成員可以看到：
                # 1. 自己擁有的動物
                # 2. 所屬收容所的動物
                conditions = [Animal.owner_id == user_id]
                if user.primary_shelter_id:
                    conditions.append(Animal.shelter_id == user.primary_shelter_id)
                query = query.filter(or_(*conditions))
            else:
                # 一般用戶只能看到自己的動物
                query = query.filter_by(owner_id=user_id)
            
            # 篩選條件
            name_q = filters.get('name')
            if name_q:
                query = query.filter(Animal.name.ilike(f"%{name_q}%"))
            
            species_q = filters.get('species')
            if species_q:
                try:
                    query = query.filter(Animal.species == species_q.upper())
                except Exception:
                    pass
            
            breed_q = filters.get('breed')
            if breed_q:
                query = query.filter(Animal.breed.ilike(f"%{breed_q}%"))
            
            # 年齡範圍篩選
            try:
                min_age = filters.get('min_age')
                max_age = filters.get('max_age')
                
                if min_age is not None and str(min_age).strip() != '':
                    min_age_val = int(min_age)
                    age_in_months = func.timestampdiff(db.text('MONTH'), Animal.dob, func.curdate())
                    query = query.filter(age_in_months >= min_age_val)
                
                if max_age is not None and str(max_age).strip() != '':
                    max_age_val = int(max_age)
                    if 'age_in_months' not in locals():
                        age_in_months = func.timestampdiff(db.text('MONTH'), Animal.dob, func.curdate())
                    query = query.filter(age_in_months <= max_age_val)
            except ValueError:
                pass  # 忽略年齡解析錯誤
            
            # 是否已領養篩選
            adopted = filters.get('adopted')
            if adopted is not None:
                adopted_val = str(adopted).lower()
                from app.models.application import Application, ApplicationStatus
                
                pending_app_exists = db.session.query(Application).filter(
                    Application.animal_id == Animal.animal_id,
                    Application.deleted_at == None,
                    Application.status.in_([ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW])
                ).exists()
                
                if adopted_val in ('1', 'true', 'yes'):
                    # 已領養
                    query = query.filter(or_(
                        Animal.status == AnimalStatus.ADOPTED,
                        and_(Animal.owner_id.isnot(None), ~pending_app_exists)
                    ))
                elif adopted_val in ('0', 'false', 'no'):
                    # 未領養
                    query = query.filter(and_(
                        Animal.status != AnimalStatus.ADOPTED,
                        or_(Animal.owner_id.is_(None), pending_app_exists)
                    ))
            
            # 執行查詢
            animals = query.all()
            animals_data = []
            
            for animal in animals:
                animal_dict = animal.to_dict()
                # 添加圖片信息
                if hasattr(animal, 'images') and animal.images:
                    animal_dict['images'] = [img.to_dict() for img in animal.images]
                animals_data.append(animal_dict)
            
            return {
                'animals': animals_data,
                'total': len(animals_data)
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"List animals for medical records error: {str(e)}")
            raise RuntimeError(f"獲取動物列表失敗: {str(e)}")

    @staticmethod
    def create_medical_record(user_id, animal_id, data):
        """
        為動物創建醫療記錄
        
        Args:
            user_id: 用戶ID
            animal_id: 動物ID
            data: 醫療記錄數據
        
        Returns:
            dict: 創建結果
        """
        try:
            # 檢查動物是否存在
            animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
            if not animal:
                raise ValueError('動物不存在')
            
            # 檢查權限
            MedicalRecordService.check_animal_permission(user_id, animal, 'create')
            
            # 驗證 record_type
            record_type = None
            if 'record_type' in data:
                try:
                    record_type = RecordType(data['record_type'])
                except ValueError:
                    raise ValueError(f'無效的記錄類型: {data["record_type"]}')
            
            # 驗證日期格式
            record_date = None
            if 'date' in data:
                record_date = MedicalRecordService._parse_date(data['date'])
            
            # 創建醫療記錄
            medical_record = MedicalRecord(
                animal_id=animal_id,
                record_type=record_type,
                date=record_date,
                provider=data.get('provider'),
                details=data.get('details'),
                attachments=data.get('attachments', []),
                verified=False,
                created_by=user_id
            )
            
            db.session.add(medical_record)
            db.session.flush()  # 獲取醫療記錄 ID
            
            # 處理附件
            attachments_data = data.get('attachments', [])
            if attachments_data and isinstance(attachments_data, list):
                MedicalRecordService._create_attachments(
                    medical_record.medical_record_id, 
                    attachments_data, 
                    user_id
                )
            
            db.session.commit()
            
            return {
                'message': '醫療記錄創建成功',
                'medical_record': medical_record.to_dict()
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Create medical record error: {str(e)}")
            raise RuntimeError(f"創建醫療記錄失敗: {str(e)}")

    @staticmethod
    def list_medical_records(animal_id):
        """
        取得動物的醫療記錄列表
        
        Args:
            animal_id: 動物ID
        
        Returns:
            dict: 醫療記錄列表
        """
        try:
            # 檢查動物是否存在
            animal = Animal.query.filter_by(animal_id=animal_id, deleted_at=None).first()
            if not animal:
                raise ValueError('動物不存在')
            
            # 查詢醫療記錄
            records = MedicalRecord.query.filter_by(
                animal_id=animal_id,
                deleted_at=None
            ).order_by(MedicalRecord.date.desc()).all()
            
            return {
                'total': len(records),
                'medical_records': [record.to_dict() for record in records]
            }
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"List medical records error: {str(e)}")
            raise RuntimeError(f"獲取醫療記錄列表失敗: {str(e)}")

    @staticmethod
    def update_medical_record(user_id, record_id, data):
        """
        更新醫療記錄
        
        Args:
            user_id: 用戶ID
            record_id: 醫療記錄ID
            data: 更新數據
        
        Returns:
            dict: 更新結果
        """
        try:
            record = MedicalRecord.query.filter_by(
                medical_record_id=record_id,
                deleted_at=None
            ).first()
            
            if not record:
                raise ValueError('醫療記錄不存在')
            
            # 檢查權限
            MedicalRecordService.check_record_permission(user_id, record, 'update')
            
            # 更新欄位
            if 'record_type' in data:
                try:
                    record.record_type = RecordType(data['record_type'])
                except ValueError:
                    raise ValueError(f'無效的記錄類型: {data["record_type"]}')
            
            if 'date' in data:
                record.date = MedicalRecordService._parse_date(data['date'])
            
            if 'provider' in data:
                record.provider = data['provider']
            
            if 'details' in data:
                record.details = data['details']
            
            if 'attachments' in data:
                # 處理附件更新
                new_attachments = data['attachments']
                
                if new_attachments and isinstance(new_attachments, list):
                    # 檢查哪些是新附件
                    for attachment_info in new_attachments:
                        if (isinstance(attachment_info, dict) and 
                            'storage_key' in attachment_info and 
                            not attachment_info.get('attachment_id')):
                            
                            # 創建新附件記錄
                            MedicalRecordService._create_single_attachment(
                                record.medical_record_id, 
                                attachment_info, 
                                user_id,
                                'medical_record_form_update'
                            )
                
                # 更新 JSON 欄位（向後相容）
                record.attachments = new_attachments
            
            record.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'message': '醫療記錄更新成功',
                'medical_record': record.to_dict()
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Update medical record error: {str(e)}")
            raise RuntimeError(f"更新醫療記錄失敗: {str(e)}")

    @staticmethod
    def verify_medical_record(admin_id, record_id, verified=True):
        """
        驗證醫療記錄
        
        Args:
            admin_id: 管理員ID
            record_id: 醫療記錄ID
            verified: 是否驗證
        
        Returns:
            dict: 驗證結果
        """
        try:
            record = MedicalRecord.query.filter_by(
                medical_record_id=record_id,
                deleted_at=None
            ).first()
            
            if not record:
                raise ValueError('醫療記錄不存在')
            
            # 檢查管理員權限
            MedicalRecordService.check_record_permission(admin_id, record, 'verify')
            
            record.verified = verified
            record.verified_by = admin_id if verified else None
            record.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'message': f'醫療記錄已{"驗證" if verified else "取消驗證"}',
                'medical_record': record.to_dict()
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Verify medical record error: {str(e)}")
            raise RuntimeError(f"驗證醫療記錄失敗: {str(e)}")

    @staticmethod
    def _parse_date(date_str):
        """
        解析日期字串為日期對象
        
        Args:
            date_str: 日期字串
        
        Returns:
            date: 日期對象
        
        Raises:
            ValueError: 日期格式錯誤
        """
        try:
            date_str = date_str.strip()
            # 嘗試多種日期格式
            date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%d-%m-%Y']
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            raise ValueError('日期格式錯誤,支援格式: YYYY-MM-DD, YYYY/MM/DD, DD/MM/YYYY, DD-MM-YYYY')
            
        except Exception:
            raise ValueError('日期格式錯誤,支援格式: YYYY-MM-DD, YYYY/MM/DD, DD/MM/YYYY, DD-MM-YYYY')

    @staticmethod
    def _create_attachments(medical_record_id, attachments_data, user_id):
        """創建附件記錄"""
        for attachment_info in attachments_data:
            if isinstance(attachment_info, dict) and 'storage_key' in attachment_info:
                MedicalRecordService._create_single_attachment(
                    medical_record_id, 
                    attachment_info, 
                    user_id,
                    'medical_record_form'
                )

    @staticmethod
    def _create_single_attachment(medical_record_id, attachment_info, user_id, upload_via):
        """創建單一附件記錄"""
        from app.models.others import Attachment
        
        # 確保必要字段存在
        storage_key = attachment_info.get('storage_key')
        if not storage_key:
            current_app.logger.warning(f"Attachment missing storage_key: {attachment_info}")
            return
        
        # 生成 URL（如果沒有提供）
        url = attachment_info.get('url')
        if not url:
            # 使用簡單的 URL 格式
            url = f"/api/uploads/files/{storage_key}"
        
        attachment = Attachment(
            owner_type='medical_record',
            owner_id=medical_record_id,
            storage_key=storage_key,
            url=url,
            filename=attachment_info.get('filename', '未知檔案'),
            mime_type=attachment_info.get('mime_type'),
            size=attachment_info.get('size'),
            meta_data={
                'type': 'medical_proof',
                'uploaded_via': upload_via
            },
            created_by=user_id
        )
        
        try:
            db.session.add(attachment)
            current_app.logger.info(f"Created attachment for medical record {medical_record_id}: {attachment_info.get('filename')}")
        except Exception as e:
            current_app.logger.error(f"Error creating attachment: {e}")
            raise
