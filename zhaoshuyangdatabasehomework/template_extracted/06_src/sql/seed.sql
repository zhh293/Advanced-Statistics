-- ============================================
-- 医院预约系统测试数据
-- 使用前请先执行 init.sql
-- 管理员密码 Admin1234!，患者/医生密码 Test1234!
-- password_hash 需通过以下命令生成：
--   python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('Admin1234!'))"
-- 以下 hash 仅作占位，请替换为真实 bcrypt hash 后再导入
-- ============================================

-- 用户（admin / patient1 / doctor1 / doctor2）
INSERT INTO Users (username, password_hash, role, email, phone) VALUES
    ('admin',   '$2b$12$REPLACE_WITH_REAL_HASH', 'admin',   'admin@hospital.com',   '10000000000'),
    ('patient1','$2b$12$REPLACE_WITH_REAL_HASH', 'patient', 'patient1@example.com', '13800000001'),
    ('doctor1', '$2b$12$REPLACE_WITH_REAL_HASH', 'doctor',  'doctor1@hospital.com', '13900000001'),
    ('doctor2', '$2b$12$REPLACE_WITH_REAL_HASH', 'doctor',  'doctor2@hospital.com', '13900000002');

-- 科室
INSERT INTO Department (dept_name, description, floor_no) VALUES
    ('内科', '负责内科常见病、多发病诊治', 3),
    ('外科', '负责外科手术及常见外科疾病', 4);

-- 诊室
INSERT INTO Room (dept_id, room_name, room_no, floor_no) VALUES
    (1, '内科诊室1', 'A301', 3),
    (1, '内科诊室2', 'A302', 3),
    (2, '外科诊室1', 'B401', 4);

-- 医生档案（关联 user_id=3,4）
INSERT INTO Doctor (user_id, real_name, dept_id, title, specialty, intro) VALUES
    (3, '王建国', 1, '主任医师',   '冠心病、高血压、心律失常', '从事内科临床工作30余年'),
    (4, '李明华', 2, '副主任医师', '普外科手术、腹腔镜微创',   '擅长腹腔镜手术');

-- 患者档案（关联 user_id=2）
INSERT INTO Patient (user_id, real_name, id_card, gender, birth_date, address) VALUES
    (2, '张三', '110101199001011234', '男', '1990-01-01', '北京市朝阳区XX路1号');

-- 排班（近期日期，请按实际情况调整）
INSERT INTO Schedule (doctor_id, room_id, work_date, time_period, max_patients) VALUES
    (1, 1, CURRENT_DATE + 1, '上午', 20),
    (1, 1, CURRENT_DATE + 1, '下午', 15),
    (2, 3, CURRENT_DATE + 1, '上午', 10),
    (1, 2, CURRENT_DATE + 2, '上午', 20);

-- 药品
INSERT INTO Medicine (medicine_name, specification, unit, price, stock, category) VALUES
    ('阿莫西林胶囊', '0.5g×24粒', '盒',  12.50, 200, '抗生素'),
    ('布洛芬片',     '0.2g×100片','瓶',   8.00, 300, '解热镇痛'),
    ('藿香正气水',   '10ml×10支', '盒',  15.00, 150, '中成药'),
    ('氯化钠注射液', '500ml×1袋', '袋',   5.00, 100, '输液'),
    ('维生素C片',    '100mg×100片','瓶',   6.00, 500, '维生素');
