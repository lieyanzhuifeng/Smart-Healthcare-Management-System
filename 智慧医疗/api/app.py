# app.py
from flask import Flask

# 直接导入同一目录下的模块
from auth import bp as auth_bp
from patient import bp as patient_bp
from doctor import bp as doctor_bp
from pharmacy import bp as pharmacy_bp
from admin import bp as admin_bp

app = Flask(__name__)

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(patient_bp, url_prefix='/patient')
app.register_blueprint(doctor_bp, url_prefix='/doctor')
app.register_blueprint(pharmacy_bp, url_prefix='/pharmacy')
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.route('/')
def hello():
    return "API服务运行正常！"

if __name__ == '__main__':
    print("启动服务器...")
    app.run(debug=True, port=5000)