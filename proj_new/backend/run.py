from app import create_app
import os

# 創建 Flask 應用
env = os.getenv('FLASK_ENV', 'production')
app = create_app(env)

if __name__ == '__main__':
    # 開發模式
    debug = env == 'development'
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug
    )
