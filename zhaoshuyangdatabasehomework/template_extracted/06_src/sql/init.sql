-- ============================================
-- 医院预约系统数据库DDL脚本
-- 目标数据库：PostgreSQL 15+
-- 字符集：UTF-8
-- ============================================

-- DROP TABLE IF EXISTS PrescriptionDetail, Prescription, Medicine,
--     MedicalRecord, Appointment, Schedule, Room,
--     Doctor, Patient, Department, Users CASCADE;


-- 1. 用户表
CREATE TABLE Users (
    user_id       SERIAL PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role          VARCHAR(10)  NOT NULL DEFAULT 'patient'
                  CHECK (role IN ('admin', 'patient', 'doctor')),
    email         VARCHAR(100),
    phone         VARCHAR(20),
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_user_username UNIQUE (username),
    CONSTRAINT uk_user_email    UNIQUE (email)
);


-- 2. 患者表
CREATE TABLE Patient (
    patient_id        SERIAL PRIMARY KEY,
    user_id           INT         NOT NULL,
    real_name         VARCHAR(50) NOT NULL,
    id_card           VARCHAR(18) NOT NULL,
    gender            VARCHAR(4)  NOT NULL
                      CHECK (gender IN ('男', '女')),
    birth_date        DATE,
    address           VARCHAR(200),
    emergency_contact VARCHAR(50),
    emergency_phone   VARCHAR(20),
    CONSTRAINT fk_patient_user FOREIGN KEY (user_id)
        REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT uk_patient_id_card UNIQUE (id_card),
    CONSTRAINT uk_patient_user   UNIQUE (user_id)
);


-- 3. 科室表
CREATE TABLE Department (
    dept_id     SERIAL PRIMARY KEY,
    dept_name   VARCHAR(50) NOT NULL,
    description TEXT,
    floor_no    INT,
    CONSTRAINT uk_dept_name UNIQUE (dept_name)
);


-- 4. 医生表
CREATE TABLE Doctor (
    doctor_id SERIAL PRIMARY KEY,
    user_id   INT         NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    dept_id   INT         NOT NULL,
    title     VARCHAR(20) NOT NULL
              CHECK (title IN ('主任医师', '副主任医师', '主治医师', '住院医师')),
    specialty VARCHAR(100),
    intro     TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_doctor_user FOREIGN KEY (user_id)
        REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_doctor_dept FOREIGN KEY (dept_id)
        REFERENCES Department(dept_id),
    CONSTRAINT uk_doctor_user UNIQUE (user_id)
);


-- 5. 诊室表
CREATE TABLE Room (
    room_id   SERIAL PRIMARY KEY,
    dept_id   INT         NOT NULL,
    room_name VARCHAR(50) NOT NULL,
    room_no   VARCHAR(20) NOT NULL,
    floor_no  INT,
    CONSTRAINT fk_room_dept FOREIGN KEY (dept_id)
        REFERENCES Department(dept_id),
    CONSTRAINT uk_room_no UNIQUE (room_no)
);


-- 6. 排班表
CREATE TABLE Schedule (
    schedule_id      SERIAL PRIMARY KEY,
    doctor_id        INT         NOT NULL,
    room_id          INT         NOT NULL,
    work_date        DATE        NOT NULL,
    time_period      VARCHAR(10) NOT NULL
                     CHECK (time_period IN ('上午', '下午', '晚上')),
    max_patients     INT NOT NULL DEFAULT 20
                     CHECK (max_patients > 0),
    registered_count INT NOT NULL DEFAULT 0
                     CHECK (registered_count >= 0),
    status           VARCHAR(10) NOT NULL DEFAULT '正常'
                     CHECK (status IN ('正常', '停诊', '约满')),
    CONSTRAINT fk_schedule_doctor FOREIGN KEY (doctor_id)
        REFERENCES Doctor(doctor_id),
    CONSTRAINT fk_schedule_room FOREIGN KEY (room_id)
        REFERENCES Room(room_id),
    CONSTRAINT uk_schedule UNIQUE (doctor_id, work_date, time_period),
    CONSTRAINT chk_registered_le_max
        CHECK (registered_count <= max_patients)
);


-- 7. 预约表
CREATE TABLE Appointment (
    appointment_id SERIAL PRIMARY KEY,
    patient_id     INT         NOT NULL,
    schedule_id    INT         NOT NULL,
    queue_no       INT         NOT NULL CHECK (queue_no > 0),
    status         VARCHAR(10) NOT NULL DEFAULT '待就诊'
                   CHECK (status IN ('待就诊', '已就诊', '已取消', '爽约')),
    created_at     TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cancel_reason  VARCHAR(200),
    CONSTRAINT fk_appt_patient FOREIGN KEY (patient_id)
        REFERENCES Patient(patient_id),
    CONSTRAINT fk_appt_schedule FOREIGN KEY (schedule_id)
        REFERENCES Schedule(schedule_id),
    CONSTRAINT uk_appt_queue UNIQUE (schedule_id, queue_no),
    CONSTRAINT uk_appt_patient_schedule UNIQUE (patient_id, schedule_id)
);


-- 8. 病历表
CREATE TABLE MedicalRecord (
    record_id       SERIAL PRIMARY KEY,
    appointment_id  INT       NOT NULL,
    doctor_id       INT       NOT NULL,
    patient_id      INT       NOT NULL,
    visit_time      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    chief_complaint TEXT,
    diagnosis       TEXT,
    treatment_plan  TEXT,
    notes           TEXT,
    CONSTRAINT fk_record_appointment FOREIGN KEY (appointment_id)
        REFERENCES Appointment(appointment_id),
    CONSTRAINT fk_record_doctor FOREIGN KEY (doctor_id)
        REFERENCES Doctor(doctor_id),
    CONSTRAINT fk_record_patient FOREIGN KEY (patient_id)
        REFERENCES Patient(patient_id),
    CONSTRAINT uk_record_appointment UNIQUE (appointment_id)
);


-- 9. 处方表
CREATE TABLE Prescription (
    prescription_id SERIAL PRIMARY KEY,
    record_id       INT       NOT NULL,
    doctor_id       INT       NOT NULL,
    issued_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_price     NUMERIC(10, 2)
                    CHECK (total_price >= 0),
    notes           TEXT,
    CONSTRAINT fk_prescription_record FOREIGN KEY (record_id)
        REFERENCES MedicalRecord(record_id),
    CONSTRAINT fk_prescription_doctor FOREIGN KEY (doctor_id)
        REFERENCES Doctor(doctor_id),
    CONSTRAINT uk_prescription_record UNIQUE (record_id)
);


-- 10. 药品表
CREATE TABLE Medicine (
    medicine_id   SERIAL PRIMARY KEY,
    medicine_name VARCHAR(100) NOT NULL,
    specification VARCHAR(100) NOT NULL DEFAULT '',
    unit          VARCHAR(20)  NOT NULL,
    price         NUMERIC(10, 2) NOT NULL
                  CHECK (price >= 0),
    stock         INT NOT NULL DEFAULT 0
                  CHECK (stock >= 0),
    category      VARCHAR(50),
    CONSTRAINT uk_medicine_name_spec UNIQUE (medicine_name, specification)
);


-- 11. 处方明细表（多对多中间表）
CREATE TABLE PrescriptionDetail (
    detail_id       SERIAL PRIMARY KEY,
    prescription_id INT NOT NULL,
    medicine_id     INT NOT NULL,
    quantity        INT NOT NULL CHECK (quantity > 0),
    dosage          VARCHAR(100),
    days            INT CHECK (days > 0),
    subtotal        NUMERIC(10, 2) CHECK (subtotal >= 0),
    CONSTRAINT fk_detail_prescription FOREIGN KEY (prescription_id)
        REFERENCES Prescription(prescription_id) ON DELETE CASCADE,
    CONSTRAINT fk_detail_medicine FOREIGN KEY (medicine_id)
        REFERENCES Medicine(medicine_id),
    CONSTRAINT uk_detail_prescription_medicine UNIQUE (prescription_id, medicine_id)
);
