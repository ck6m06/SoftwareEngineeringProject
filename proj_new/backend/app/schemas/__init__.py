"""
Schemas for request/response validation
"""
from marshmallow import Schema, fields, EXCLUDE


class AnimalCreateSchema(Schema):
    """動物創建資料驗證"""
    name = fields.String(required=True, validate=fields.validate.Length(min=1, max=100))
    species = fields.String(required=True, validate=fields.validate.OneOf(['CAT', 'DOG']))
    sex = fields.String(required=True, validate=fields.validate.OneOf(['MALE', 'FEMALE', 'UNKNOWN']))
    breed = fields.String(allow_none=True, validate=fields.validate.Length(max=100))
    age_months = fields.Integer(allow_none=True, validate=fields.validate.Range(min=0, max=360))
    description = fields.String(allow_none=True, validate=fields.validate.Length(max=2000))
    shelter_id = fields.Integer(allow_none=True)


class AnimalUpdateSchema(Schema):
    """動物更新資料驗證"""
    name = fields.String(validate=fields.validate.Length(min=1, max=100))
    species = fields.String(validate=fields.validate.OneOf(['CAT', 'DOG']))
    sex = fields.String(validate=fields.validate.OneOf(['MALE', 'FEMALE', 'UNKNOWN']))
    breed = fields.String(allow_none=True, validate=fields.validate.Length(max=100))
    age_months = fields.Integer(allow_none=True, validate=fields.validate.Range(min=0, max=360))
    description = fields.String(allow_none=True, validate=fields.validate.Length(max=2000))
    status = fields.String(validate=fields.validate.OneOf(['DRAFT', 'SUBMITTED', 'PUBLISHED', 'RETIRED']))


class ApplicationCreateSchema(Schema):
    """申請創建資料驗證"""
    class Meta:
        unknown = EXCLUDE  # 忽略未知字段
        
    animal_id = fields.Integer(required=True)
    type = fields.String(allow_none=True, validate=fields.validate.OneOf(['ADOPTION', 'REHOME']))
    attachments = fields.Raw(allow_none=True)
    
    # 申請人詳細資料
    contact_phone = fields.String(allow_none=True, validate=fields.validate.Length(max=32))
    contact_address = fields.String(allow_none=True, validate=fields.validate.Length(max=500))
    occupation = fields.String(allow_none=True, validate=fields.validate.Length(max=100))
    housing_type = fields.String(allow_none=True, validate=fields.validate.Length(max=50))
    has_experience = fields.Boolean(allow_none=True)
    reason = fields.String(allow_none=True, validate=fields.validate.Length(max=2000))
    notes = fields.String(allow_none=True, validate=fields.validate.Length(max=2000))


class ApplicationUpdateSchema(Schema):
    """申請更新資料驗證"""
    message = fields.String(allow_none=True, validate=fields.validate.Length(max=2000))
    contact_info = fields.String(allow_none=True, validate=fields.validate.Length(max=500))
    status = fields.String(validate=fields.validate.OneOf(['PENDING', 'APPROVED', 'REJECTED', 'CANCELED']))