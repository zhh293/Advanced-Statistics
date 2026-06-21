# 医院预约系统 · 前后端接口文档与功能设计说明

---

## 目录

1. [功能模块概述](#1-功能模块概述)
2. [接口规范](#2-接口规范)
3. [认证模块（Auth）](#3-认证模块)
4. [患者模块（Patient）](#4-患者模块)
5. [科室模块（Department）](#5-科室模块)
6. [医生模块（Doctor）](#6-医生模块)
7. [排班模块（Schedule）](#7-排班模块)
8. [预约模块（Appointment）](#8-预约模块)
9. [病历模块（MedicalRecord）](#9-病历模块)
10. [处方模块（Prescription）](#10-处方模块)
11. [药品模块（Medicine）](#11-药品模块)
12. [管理员模块（Admin）](#12-管理员模块)
13. [错误码一览](#13-错误码一览)

---

## 1. 功能模块概述

| 模块 | 面向角色 | 核心功能 |
|------|---------|---------|
| 认证 | 全部 | 注册、登录、登出、Token刷新 |
| 患者 | 患者 | 管理个人档案、查看就诊历史 |
| 科室 | 全部 | 浏览科室列表与介绍 |
| 医生 | 全部 | 浏览医生信息、按科室/职称筛选 |
| 排班 | 全部/管理员 | 查询可预约排班；管理员维护排班 |
| 预约 | 患者 | 发起预约、查看预约状态、取消预约 |
| 病历 | 医生 | 就诊后填写病历（主诉、诊断、治疗方案） |
| 处方 | 医生 | 开具处方、关联药品明细 |
| 药品 | 医生/管理员 | 查询药品目录；管理员维护库存 |
| 管理员 | 管理员 | 管理科室、医生、排班、用户；查看统计 |

---

## 2. 接口规范

### 2.1 基础信息

| 项目 | 值 |
|------|----|
| Base URL | `http://localhost:8080/api/v1` |
| 数据格式 | JSON（Content-Type: application/json） |
| 字符编码 | UTF-8 |
| 认证方式 | JWT Bearer Token |

### 2.2 认证方式

需要登录的接口，请求头中携带：

```
Authorization: Bearer <access_token>
```

### 2.3 角色权限

| 角色值 | 说明 | 标记 |
|--------|------|------|
| `admin` | 系统管理员 | 🔑 Admin |
| `doctor` | 医生 | 🩺 Doctor |
| `patient` | 患者 | 👤 Patient |
| 无 | 公开接口，无需登录 | 🌐 Public |

### 2.4 统一响应格式

**成功响应：**

```json
{
  "code": 200,
  "message": "success",
  "data": { }
}
```

**分页响应：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [ ],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

**失败响应：**

```json
{
  "code": 40001,
  "message": "用户名或密码错误",
  "data": null
}
```

### 2.5 公共请求参数（分页接口）

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | int | 否 | 1 | 页码，从1开始 |
| page_size | int | 否 | 20 | 每页条数，最大100 |

---

## 3. 认证模块

### 3.1 用户注册

- **接口**：`POST /auth/register`
- **权限**：🌐 Public

**请求体：**

```json
{
  "username": "zhang_san",
  "password": "Abc12345!",
  "role": "patient",
  "email": "zhangsan@example.com",
  "phone": "13800138000"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 3-50位，字母/数字/下划线 |
| password | string | 是 | 8-32位，含字母和数字 |
| role | string | 是 | 枚举：`patient` / `doctor`（管理员由超管创建） |
| email | string | 否 | 有效邮箱格式 |
| phone | string | 否 | 11位手机号 |

**成功响应（201）：**

```json
{
  "code": 201,
  "message": "注册成功",
  "data": {
    "user_id": 1,
    "username": "zhang_san",
    "role": "patient"
  }
}
```

**失败场景：**

| code | message |
|------|---------|
| 40901 | 用户名已存在 |
| 40902 | 邮箱已被注册 |
| 40001 | 参数校验失败 |

---

### 3.2 用户登录

- **接口**：`POST /auth/login`
- **权限**：🌐 Public

**请求体：**

```json
{
  "username": "zhang_san",
  "password": "Abc12345!"
}
```

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "user": {
      "user_id": 1,
      "username": "zhang_san",
      "role": "patient"
    }
  }
}
```

**失败场景：**

| code | message |
|------|---------|
| 40101 | 用户名或密码错误 |
| 40301 | 账号已被禁用 |

---

### 3.3 用户登出

- **接口**：`POST /auth/logout`
- **权限**：👤 Patient / 🩺 Doctor / 🔑 Admin

**请求头：** `Authorization: Bearer <access_token>`

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "已登出",
  "data": null
}
```

---

### 3.4 获取当前登录用户信息

- **接口**：`GET /auth/me`
- **权限**：👤 Patient / 🩺 Doctor / 🔑 Admin

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "user_id": 1,
    "username": "zhang_san",
    "role": "patient",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
    "created_at": "2026-05-01T10:00:00Z"
  }
}
```

---

## 4. 患者模块

### 4.1 创建/完善患者档案

- **接口**：`POST /patients/profile`
- **权限**：👤 Patient
- **说明**：患者注册后首次完善档案，每个用户只能创建一次

**请求体：**

```json
{
  "real_name": "张三",
  "id_card": "110101199001011234",
  "gender": "男",
  "birth_date": "1990-01-01",
  "address": "北京市朝阳区...",
  "emergency_contact": "李四",
  "emergency_phone": "13900000001"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| real_name | string | 是 | 真实姓名 |
| id_card | string | 是 | 18位身份证号 |
| gender | string | 是 | 枚举：`男` / `女` |
| birth_date | string | 否 | 格式：YYYY-MM-DD |
| address | string | 否 | 家庭住址 |
| emergency_contact | string | 否 | 紧急联系人姓名 |
| emergency_phone | string | 否 | 紧急联系人电话 |

**成功响应（201）：**

```json
{
  "code": 201,
  "message": "档案创建成功",
  "data": {
    "patient_id": 10,
    "user_id": 1,
    "real_name": "张三",
    "id_card": "110101199001011234",
    "gender": "男",
    "birth_date": "1990-01-01"
  }
}
```

---

### 4.2 获取当前患者档案

- **接口**：`GET /patients/profile`
- **权限**：👤 Patient

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "patient_id": 10,
    "real_name": "张三",
    "id_card": "110101199001011234",
    "gender": "男",
    "birth_date": "1990-01-01",
    "address": "北京市朝阳区...",
    "emergency_contact": "李四",
    "emergency_phone": "13900000001"
  }
}
```

---

### 4.3 更新患者档案

- **接口**：`PUT /patients/profile`
- **权限**：👤 Patient
- **说明**：身份证号不可修改

**请求体（仅传需要修改的字段）：**

```json
{
  "address": "北京市海淀区...",
  "phone": "13800138001",
  "emergency_contact": "王五",
  "emergency_phone": "13700000001"
}
```

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "档案更新成功",
  "data": { }
}
```

---

### 4.4 获取患者就诊历史

- **接口**：`GET /patients/records`
- **权限**：👤 Patient

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页条数 |

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "record_id": 5,
        "visit_time": "2026-05-10T09:30:00Z",
        "doctor_name": "王医生",
        "dept_name": "内科",
        "diagnosis": "急性上呼吸道感染",
        "has_prescription": true
      }
    ],
    "total": 3,
    "page": 1,
    "page_size": 20
  }
}
```

---

## 5. 科室模块

### 5.1 获取科室列表

- **接口**：`GET /departments`
- **权限**：🌐 Public

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "dept_id": 1,
      "dept_name": "内科",
      "description": "负责内科常见病、多发病的诊治",
      "floor_no": 3,
      "doctor_count": 12
    },
    {
      "dept_id": 2,
      "dept_name": "外科",
      "description": "负责外科手术及常见外科疾病",
      "floor_no": 4,
      "doctor_count": 8
    }
  ]
}
```

---

### 5.2 获取科室详情

- **接口**：`GET /departments/{dept_id}`
- **权限**：🌐 Public

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| dept_id | int | 科室ID |

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "dept_id": 1,
    "dept_name": "内科",
    "description": "负责内科常见病、多发病的诊治",
    "floor_no": 3,
    "rooms": [
      { "room_id": 1, "room_name": "内科诊室1", "room_no": "A301" },
      { "room_id": 2, "room_name": "内科诊室2", "room_no": "A302" }
    ],
    "doctors": [
      {
        "doctor_id": 3,
        "real_name": "王建国",
        "title": "主任医师",
        "specialty": "冠心病、高血压"
      }
    ]
  }
}
```

---

## 6. 医生模块

### 6.1 获取医生列表

- **接口**：`GET /doctors`
- **权限**：🌐 Public

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| dept_id | int | 否 | 按科室筛选 |
| title | string | 否 | 按职称筛选（主任医师/副主任医师/主治医师/住院医师） |
| keyword | string | 否 | 按姓名/擅长领域模糊搜索 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页条数 |

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "doctor_id": 3,
        "real_name": "王建国",
        "dept_name": "内科",
        "title": "主任医师",
        "specialty": "冠心病、高血压",
        "is_active": true
      }
    ],
    "total": 20,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 6.2 获取医生详情

- **接口**：`GET /doctors/{doctor_id}`
- **权限**：🌐 Public

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| doctor_id | int | 医生ID |

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "doctor_id": 3,
    "real_name": "王建国",
    "dept_id": 1,
    "dept_name": "内科",
    "title": "主任医师",
    "specialty": "冠心病、高血压、心律失常",
    "intro": "从事内科临床工作30余年...",
    "is_active": true
  }
}
```

---

### 6.3 获取医生本人信息（医生自查）

- **接口**：`GET /doctors/me`
- **权限**：🩺 Doctor

**成功响应（200）：** 同 6.2，额外包含：

```json
{
  "data": {
    "...": "...",
    "today_appointments": 8,
    "schedules_this_week": [
      {
        "schedule_id": 20,
        "work_date": "2026-06-20",
        "time_period": "上午",
        "registered_count": 8,
        "max_patients": 20,
        "status": "正常"
      }
    ]
  }
}
```

---

## 7. 排班模块

### 7.1 查询可预约排班

- **接口**：`GET /schedules`
- **权限**：🌐 Public

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| dept_id | int | 否 | 按科室筛选 |
| doctor_id | int | 否 | 按医生筛选 |
| date | string | 否 | 指定日期（YYYY-MM-DD），默认查近7天 |
| time_period | string | 否 | 上午/下午/晚上 |

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "schedule_id": 20,
      "doctor_id": 3,
      "doctor_name": "王建国",
      "title": "主任医师",
      "dept_name": "内科",
      "room_no": "A301",
      "work_date": "2026-06-21",
      "time_period": "上午",
      "max_patients": 20,
      "registered_count": 8,
      "remaining": 12,
      "status": "正常"
    }
  ]
}
```

---

### 7.2 获取排班详情

- **接口**：`GET /schedules/{schedule_id}`
- **权限**：🌐 Public

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| schedule_id | int | 排班ID |

**成功响应（200）：** 内容同7.1单条，额外含医生简介信息。

---

## 8. 预约模块

### 8.1 发起预约

- **接口**：`POST /appointments`
- **权限**：👤 Patient

**请求体：**

```json
{
  "schedule_id": 20
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| schedule_id | int | 是 | 目标排班ID |

**成功响应（201）：**

```json
{
  "code": 201,
  "message": "预约成功",
  "data": {
    "appointment_id": 55,
    "schedule_id": 20,
    "doctor_name": "王建国",
    "dept_name": "内科",
    "work_date": "2026-06-21",
    "time_period": "上午",
    "room_no": "A301",
    "queue_no": 9,
    "status": "待就诊",
    "created_at": "2026-06-20T14:22:00Z"
  }
}
```

**失败场景：**

| code | message |
|------|---------|
| 40901 | 该排班已约满 |
| 40902 | 您已预约过该排班 |
| 40903 | 排班已停诊 |
| 40001 | 患者档案不存在，请先完善个人信息 |

---

### 8.2 获取我的预约列表

- **接口**：`GET /appointments`
- **权限**：👤 Patient

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 否 | 筛选状态：待就诊/已就诊/已取消/爽约 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页条数 |

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "appointment_id": 55,
        "doctor_name": "王建国",
        "dept_name": "内科",
        "work_date": "2026-06-21",
        "time_period": "上午",
        "queue_no": 9,
        "status": "待就诊",
        "created_at": "2026-06-20T14:22:00Z"
      }
    ],
    "total": 5,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 8.3 获取预约详情

- **接口**：`GET /appointments/{appointment_id}`
- **权限**：👤 Patient（只能查自己的）/ 🔑 Admin

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| appointment_id | int | 预约ID |

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "appointment_id": 55,
    "patient_name": "张三",
    "doctor_name": "王建国",
    "dept_name": "内科",
    "room_no": "A301",
    "work_date": "2026-06-21",
    "time_period": "上午",
    "queue_no": 9,
    "status": "待就诊",
    "created_at": "2026-06-20T14:22:00Z",
    "cancel_reason": null
  }
}
```

---

### 8.4 取消预约

- **接口**：`PUT /appointments/{appointment_id}/cancel`
- **权限**：👤 Patient（只能取消自己的）

**请求体：**

```json
{
  "cancel_reason": "个人原因无法就诊"
}
```

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "预约已取消",
  "data": null
}
```

**失败场景：**

| code | message |
|------|---------|
| 40301 | 无权操作他人预约 |
| 40001 | 该预约已就诊，无法取消 |
| 40002 | 该预约已取消 |

---

### 8.5 医生查看当日就诊列表

- **接口**：`GET /appointments/today`
- **权限**：🩺 Doctor

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | 否 | 日期（YYYY-MM-DD），默认今天 |
| time_period | string | 否 | 上午/下午/晚上 |

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "appointment_id": 55,
        "queue_no": 1,
        "patient_name": "张三",
        "gender": "男",
        "age": 36,
        "status": "待就诊",
        "has_record": false
      }
    ],
    "total": 8
  }
}
```

---

## 9. 病历模块

### 9.1 创建病历

- **接口**：`POST /medical-records`
- **权限**：🩺 Doctor

**请求体：**

```json
{
  "appointment_id": 55,
  "chief_complaint": "反复咳嗽、发热3天",
  "diagnosis": "急性上呼吸道感染",
  "treatment_plan": "休息、多饮水，口服抗病毒药物",
  "notes": "建议3天后复诊"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| appointment_id | int | 是 | 关联预约ID（必须为自己的排班下的预约） |
| chief_complaint | string | 否 | 主诉 |
| diagnosis | string | 否 | 诊断结果 |
| treatment_plan | string | 否 | 治疗方案 |
| notes | string | 否 | 医生备注 |

**成功响应（201）：**

```json
{
  "code": 201,
  "message": "病历创建成功",
  "data": {
    "record_id": 30,
    "appointment_id": 55,
    "patient_name": "张三",
    "visit_time": "2026-06-21T09:35:00Z"
  }
}
```

**失败场景：**

| code | message |
|------|---------|
| 40001 | 该预约不属于您的排班 |
| 40901 | 该预约已存在病历 |

---

### 9.2 获取病历详情

- **接口**：`GET /medical-records/{record_id}`
- **权限**：👤 Patient（只能查自己）/ 🩺 Doctor（只能查自己诊治的）/ 🔑 Admin

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| record_id | int | 病历ID |

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "record_id": 30,
    "patient_name": "张三",
    "gender": "男",
    "doctor_name": "王建国",
    "dept_name": "内科",
    "visit_time": "2026-06-21T09:35:00Z",
    "chief_complaint": "反复咳嗽、发热3天",
    "diagnosis": "急性上呼吸道感染",
    "treatment_plan": "休息、多饮水，口服抗病毒药物",
    "notes": "建议3天后复诊",
    "prescription": {
      "prescription_id": 18,
      "total_price": 45.50,
      "details": [
        {
          "medicine_name": "阿莫西林胶囊",
          "specification": "0.5g×24粒",
          "quantity": 2,
          "dosage": "每日三次，每次一粒",
          "days": 5,
          "subtotal": 25.00
        }
      ]
    }
  }
}
```

---

### 9.3 更新病历

- **接口**：`PUT /medical-records/{record_id}`
- **权限**：🩺 Doctor（只能更新自己创建的）

**请求体（仅传需要更新的字段）：**

```json
{
  "diagnosis": "急性支气管炎",
  "treatment_plan": "抗感染治疗，口服阿莫西林",
  "notes": "1周后复查"
}
```

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "病历更新成功",
  "data": null
}
```

---

## 10. 处方模块

### 10.1 开具处方

- **接口**：`POST /prescriptions`
- **权限**：🩺 Doctor

**请求体：**

```json
{
  "record_id": 30,
  "notes": "饭后服用，避免空腹",
  "details": [
    {
      "medicine_id": 5,
      "quantity": 2,
      "dosage": "每日三次，每次一粒",
      "days": 5
    },
    {
      "medicine_id": 12,
      "quantity": 1,
      "dosage": "每日一次，每次一片",
      "days": 3
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| record_id | int | 是 | 关联病历ID |
| notes | string | 否 | 处方备注 |
| details | array | 是 | 处方明细列表，至少1项 |
| details[].medicine_id | int | 是 | 药品ID |
| details[].quantity | int | 是 | 数量（正整数） |
| details[].dosage | string | 否 | 用法用量说明 |
| details[].days | int | 否 | 用药天数 |

**成功响应（201）：**

```json
{
  "code": 201,
  "message": "处方开具成功",
  "data": {
    "prescription_id": 18,
    "record_id": 30,
    "total_price": 45.50,
    "issued_at": "2026-06-21T09:40:00Z",
    "details": [
      {
        "detail_id": 101,
        "medicine_name": "阿莫西林胶囊",
        "quantity": 2,
        "subtotal": 25.00
      }
    ]
  }
}
```

**失败场景：**

| code | message |
|------|---------|
| 40901 | 该病历已存在处方 |
| 40001 | 药品库存不足：阿莫西林胶囊 |
| 40301 | 无权为他人病历开具处方 |

---

### 10.2 获取处方详情

- **接口**：`GET /prescriptions/{prescription_id}`
- **权限**：👤 Patient（自己的）/ 🩺 Doctor（自己开的）/ 🔑 Admin

**成功响应（200）：** 同 9.2 中 prescription 对象的完整版。

---

## 11. 药品模块

### 11.1 查询药品列表

- **接口**：`GET /medicines`
- **权限**：🩺 Doctor / 🔑 Admin

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 药品名称模糊搜索 |
| category | string | 否 | 按分类筛选 |
| in_stock | bool | 否 | true=仅显示有库存的 |
| page | int | 否 | 页码 |

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "medicine_id": 5,
        "medicine_name": "阿莫西林胶囊",
        "specification": "0.5g×24粒",
        "unit": "盒",
        "price": 12.50,
        "stock": 200,
        "category": "抗生素"
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 11.2 获取药品详情

- **接口**：`GET /medicines/{medicine_id}`
- **权限**：🩺 Doctor / 🔑 Admin

**成功响应（200）：** 单条药品完整信息。

---

## 12. 管理员模块

### 12.1 创建科室

- **接口**：`POST /admin/departments`
- **权限**：🔑 Admin

**请求体：**

```json
{
  "dept_name": "神经内科",
  "description": "诊治神经系统疾病",
  "floor_no": 5
}
```

**成功响应（201）：**

```json
{
  "code": 201,
  "message": "科室创建成功",
  "data": { "dept_id": 10 }
}
```

---

### 12.2 更新科室

- **接口**：`PUT /admin/departments/{dept_id}`
- **权限**：🔑 Admin

**请求体：** 同创建，字段均可选。

---

### 12.3 创建排班

- **接口**：`POST /admin/schedules`
- **权限**：🔑 Admin

**请求体：**

```json
{
  "doctor_id": 3,
  "room_id": 1,
  "work_date": "2026-06-25",
  "time_period": "上午",
  "max_patients": 20
}
```

**成功响应（201）：**

```json
{
  "code": 201,
  "message": "排班创建成功",
  "data": { "schedule_id": 25 }
}
```

---

### 12.4 停诊/恢复排班

- **接口**：`PUT /admin/schedules/{schedule_id}/status`
- **权限**：🔑 Admin

**请求体：**

```json
{
  "status": "停诊"
}
```

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "排班状态已更新",
  "data": null
}
```

---

### 12.5 添加药品

- **接口**：`POST /admin/medicines`
- **权限**：🔑 Admin

**请求体：**

```json
{
  "medicine_name": "布洛芬片",
  "specification": "0.2g×100片",
  "unit": "瓶",
  "price": 8.00,
  "stock": 500,
  "category": "解热镇痛"
}
```

**成功响应（201）：**

```json
{
  "code": 201,
  "message": "药品添加成功",
  "data": { "medicine_id": 20 }
}
```

---

### 12.6 更新药品库存

- **接口**：`PUT /admin/medicines/{medicine_id}/stock`
- **权限**：🔑 Admin

**请求体：**

```json
{
  "stock": 800
}
```

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "库存更新成功",
  "data": null
}
```

---

### 12.7 系统统计数据

- **接口**：`GET /admin/statistics`
- **权限**：🔑 Admin

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date_from | string | 否 | 开始日期（YYYY-MM-DD） |
| date_to | string | 否 | 结束日期（YYYY-MM-DD） |

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_patients": 1200,
    "total_doctors": 45,
    "total_departments": 10,
    "appointments": {
      "total": 5300,
      "completed": 4800,
      "cancelled": 320,
      "absent": 180
    },
    "today": {
      "appointments": 85,
      "completed": 60
    },
    "top_departments": [
      { "dept_name": "内科", "appointment_count": 1500 },
      { "dept_name": "外科", "appointment_count": 900 }
    ]
  }
}
```

---

### 12.8 用户管理（禁用/启用）

- **接口**：`PUT /admin/users/{user_id}/status`
- **权限**：🔑 Admin

**请求体：**

```json
{
  "is_active": false
}
```

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "用户状态已更新",
  "data": null
}
```

---

## 13. 错误码一览

| HTTP状态码 | 业务code | message | 说明 |
|-----------|---------|---------|------|
| 400 | 40001 | 请求参数错误 | 字段格式/必填项校验失败 |
| 401 | 40101 | 用户名或密码错误 | 登录失败 |
| 401 | 40102 | Token已过期，请重新登录 | JWT过期 |
| 401 | 40103 | 未提供认证信息 | 缺少Authorization头 |
| 403 | 40301 | 权限不足 | 角色无权访问该接口 |
| 403 | 40302 | 无权操作他人数据 | 越权访问 |
| 404 | 40401 | 资源不存在 | ID对应记录不存在 |
| 409 | 40901 | 资源冲突 | 唯一约束冲突（如用户名重复） |
| 409 | 40902 | 重复操作 | 如重复预约同一排班 |
| 422 | 42201 | 业务规则校验失败 | 如排班已约满、库存不足 |
| 500 | 50001 | 服务器内部错误 | 未预期异常 |
