# 医院预约系统

基于 **FastAPI + SQLAlchemy + PostgreSQL** 的医院预约系统后端，严格对齐接口文档中定义的 40 个 REST API 接口。

## 运行环境

- Python 3.10+
- PostgreSQL 15+
- pip / venv

## 安装步骤

```bash
# 1. 进入项目目录
cd 06_src

# 2. 创建虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp config/.env.example .env
# 编辑 .env，填写真实数据库连接信息：
#   DATABASE_URL=postgresql://用户名:密码@localhost:5432/hospital_db
#   JWT_SECRET=你的随机密钥

# 5. 创建数据库（PostgreSQL）
createdb hospital_db   # 或在 psql 中执行 CREATE DATABASE hospital_db;

# 6. 初始化表结构
psql -U postgres -d hospital_db -f sql/init.sql

# 7. （可选）导入测试数据
#    注意：seed.sql 中的 password_hash 需替换为真实 bcrypt hash
#    生成方法：python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('Admin1234!'))"
psql -U postgres -d hospital_db -f sql/seed.sql
```

## 启动方式

```bash
cd 06_src
uvicorn src.main:app --reload --port 8080
```

启动后访问：
- **Swagger 文档**：http://localhost:8080/docs
- **ReDoc 文档**：http://localhost:8080/redoc
- **健康检查**：http://localhost:8080/

## API 接口概览

| 模块 | 前缀 | 主要接口 |
|------|------|---------|
| 认证 | `/api/v1/auth` | 注册、登录、登出、获取当前用户 |
| 患者 | `/api/v1/patients` | 档案管理、就诊历史 |
| 科室 | `/api/v1/departments` | 列表、详情 |
| 医生 | `/api/v1/doctors` | 列表、详情、医生自查 |
| 排班 | `/api/v1/schedules` | 列表、详情 |
| 预约 | `/api/v1/appointments` | 发起、查询、取消、今日列表 |
| 病历 | `/api/v1/medical-records` | 创建、查看、更新 |
| 处方 | `/api/v1/prescriptions` | 开具、查看 |
| 药品 | `/api/v1/medicines` | 列表、详情 |
| 管理员 | `/api/v1/admin` | 科室/排班/药品管理、统计、用户管理 |

## 项目结构

```
06_src/
├── requirements.txt         # Python 依赖
├── src/
│   ├── main.py              # FastAPI 应用入口，注册所有路由
│   ├── config.py            # 环境变量读取（pydantic-settings）
│   ├── database.py          # SQLAlchemy engine + SessionLocal
│   ├── models.py            # 11 张表的 ORM 模型
│   ├── auth.py              # JWT 生成/验证、bcrypt 密码哈希
│   ├── exceptions.py        # AppError 自定义异常 + 全局 handler
│   ├── dependencies.py      # get_current_user / require_role 依赖注入
│   ├── schemas/             # Pydantic 请求/响应模型（10 个文件）
│   │   ├── common.py        # Resp 统一响应包装、PagedData
│   │   ├── auth.py
│   │   ├── patient.py
│   │   ├── department.py
│   │   ├── doctor.py
│   │   ├── schedule.py
│   │   ├── appointment.py
│   │   ├── medical_record.py
│   │   ├── prescription.py
│   │   └── medicine.py
│   └── routers/             # 10 个业务路由模块
│       ├── auth.py
│       ├── patients.py
│       ├── departments.py
│       ├── doctors.py
│       ├── schedules.py
│       ├── appointments.py
│       ├── medical_records.py
│       ├── prescriptions.py
│       ├── medicines.py
│       └── admin.py
├── config/
│   └── .env.example         # 环境变量模板
└── sql/
    ├── init.sql             # 建表 DDL（与数据库设计文档一致）
    └── seed.sql             # 测试数据（管理员/医生/患者/排班/药品）
```

## 认证说明

所有需要登录的接口请在 HTTP 请求头中携带：

```
Authorization: Bearer <access_token>
```

`access_token` 通过 `POST /api/v1/auth/login` 获取，有效期 24 小时。

## 角色权限

| 角色 | 说明 |
|------|------|
| `admin` | 系统管理员，可访问全部接口 |
| `doctor` | 医生，可管理排班内的就诊、病历、处方 |
| `patient` | 患者，可查询/预约/取消，查看自己的病历处方 |
