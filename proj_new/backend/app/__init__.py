"""
Flask Application Factory
"""
from flask import Flask
from flask_cors import CORS
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from redis import Redis
import logging

# 初始化擴展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
redis_client = None


def create_app(config_name='development'):
    """
    應用工廠函數
    
    Args:
        config_name: 配置名稱 ('development', 'production', 'testing')
    
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    
    # 載入配置
    app.config.from_object(f'config.{config_name.capitalize()}Config')
    
    # 初始化 CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Idempotency-Key"]
        }
    })
    
    # 初始化擴展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # If SQLALCHEMY_ECHO is enabled, ensure SQLAlchemy engine logs are visible
    try:
        if app.config.get('SQLALCHEMY_ECHO'):
            logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    except Exception:
        pass
    
    # 初始化 Redis
    global redis_client
    redis_client = Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB'],
        decode_responses=True
    )
    
    # 初始化 Flask-SMOREST (OpenAPI)
    api = Api(app)
    
    # 註冊藍圖
    from app.blueprints.auth import auth_bp
    from app.blueprints.users import users_bp
    from app.blueprints.animals import animals_bp
    from app.blueprints.applications import applications_bp
    from app.blueprints.shelters import shelters_bp
    from app.blueprints.medical_records import medical_records_bp
    from app.blueprints.notifications import notifications_bp
    from app.blueprints.uploads import uploads_bp
    from app.blueprints.jobs import jobs_bp
    from app.blueprints.admin import admin_bp
    
    api.register_blueprint(auth_bp, url_prefix='/api/auth')
    api.register_blueprint(users_bp, url_prefix='/api/users')
    api.register_blueprint(animals_bp, url_prefix='/api/animals')
    api.register_blueprint(applications_bp, url_prefix='/api/applications')
    api.register_blueprint(shelters_bp, url_prefix='/api/shelters')
    api.register_blueprint(medical_records_bp, url_prefix='/api/medical-records')
    api.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    api.register_blueprint(uploads_bp, url_prefix='/api/uploads')
    api.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    api.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # 健康檢查端點
    @app.route('/healthz')
    def health_check():
        return {'status': 'healthy'}, 200
    
    @app.route('/readyz')
    def readiness_check():
        try:
            # 檢查資料庫連接 (SQLAlchemy 2.0 語法)
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            return {'status': 'ready'}, 200
        except Exception as e:
            return {'status': 'not ready', 'error': str(e)}, 503
    
    @app.route('/metrics')
    def metrics():
        """
        Prometheus格式的監控指標端點
        """
        from app.models.user import User
        from app.models.animal import Animal
        from app.models.application import Application
        from app.models.others import Job, JobStatus
        
        # 收集基本統計
        user_count = User.query.filter_by(deleted_at=None).count()
        animal_count = Animal.query.filter_by(deleted_at=None).count()
        application_count = Application.query.filter_by(deleted_at=None).count()
        
        job_pending = Job.query.filter_by(status=JobStatus.PENDING).count()
        job_running = Job.query.filter_by(status=JobStatus.RUNNING).count()
        job_failed = Job.query.filter_by(status=JobStatus.FAILED).count()
        job_succeeded = Job.query.filter_by(status=JobStatus.SUCCEEDED).count()
        
        # Prometheus格式輸出
        metrics_text = f"""# HELP pet_adoption_users_total Total number of users
# TYPE pet_adoption_users_total gauge
pet_adoption_users_total {user_count}

# HELP pet_adoption_animals_total Total number of animals
# TYPE pet_adoption_animals_total gauge
pet_adoption_animals_total {animal_count}

# HELP pet_adoption_applications_total Total number of applications
# TYPE pet_adoption_applications_total gauge
pet_adoption_applications_total {application_count}

# HELP pet_adoption_jobs_total Jobs by status
# TYPE pet_adoption_jobs_total gauge
pet_adoption_jobs_total{{status="pending"}} {job_pending}
pet_adoption_jobs_total{{status="running"}} {job_running}
pet_adoption_jobs_total{{status="failed"}} {job_failed}
pet_adoption_jobs_total{{status="succeeded"}} {job_succeeded}
"""
        
        return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    
    # JWT 錯誤處理 - 添加詳細日誌
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        app.logger.warning(f'Expired token: header={jwt_header}, payload={jwt_payload}')
        return {'error': 'Token has expired', 'code': 'token_expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        app.logger.error(f'Invalid token error: {error}')
        return {'error': 'Invalid token', 'code': 'token_invalid', 'detail': str(error)}, 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        app.logger.warning(f'Unauthorized access: {error}')
        return {'error': 'Missing authorization header', 'code': 'token_missing'}, 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        app.logger.warning(f'Revoked token: header={jwt_header}, payload={jwt_payload}')
        return {'error': 'Token has been revoked', 'code': 'token_revoked'}, 401
    
    return app
