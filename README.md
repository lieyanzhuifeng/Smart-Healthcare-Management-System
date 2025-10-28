结合提供的Vue组件（患者端、医生端、药房端、管理端、登录页）及现有API结构，以下是需要补充或完善的API接口说明，涵盖各角色核心功能及所需数据：


### 一、通用基础接口（`authAPI`）
#### 1. 登录接口（已在`index.js`中定义，需完善）
- **作用**：验证用户身份，获取登录凭证（token）和用户信息  
- **请求方式**：`POST /auth/login`  
- **所需数据**：  
  ```json
  {
    "username": "用户名（字符串）",
    "password": "密码（字符串）",
    "role": "角色（patient/doctor/pharmacy/admin，字符串）"
  }
  ```
- **返回数据**：  
  ```json
  {
    "code": 200,
    "message": "登录成功",
    "data": {
      "token": "身份令牌（字符串）",
      "user": {
        "id": "用户ID（数字/字符串）",
        "name": "用户名（字符串）",
        "role": "角色（字符串）",
        // 角色扩展信息（如医生的科室、患者的病历号等）
        "extInfo": {} 
      }
    }
  }
  ```

#### 2. 退出登录接口（已在`index.js`中定义）
- **作用**：清除用户登录状态，失效token  
- **请求方式**：`POST /auth/logout`  
- **所需数据**：无（通过请求头`Authorization`携带token）  
- **返回数据**：  
  ```json
  { "code": 200, "message": "退出成功" }
  ```

#### 3. 获取个人信息接口（新增）
- **作用**：获取当前登录用户的详细信息（用于“个人信息”功能）  
- **请求方式**：`GET /auth/profile`  
- **所需数据**：无（通过token识别用户）  
- **返回数据**：  
  ```json
  {
    "code": 200,
    "data": {
      "id": "用户ID",
      "name": "姓名",
      "role": "角色",
      "avatar": "头像URL（可选）",
      "phone": "手机号（可选）",
      // 角色特有信息（如患者的性别/年龄，医生的职称等）
    }
  }
  ```


### 二、患者端接口（`patientAPI`）
#### 1. 获取预约列表（已在`index.js`中定义，需完善）
- **作用**：获取当前患者的所有预约记录（对应`PatientDashboard`的“我的预约”表格）  
- **请求方式**：`GET /patient/appointments`  
- **所需数据**：无（通过token识别患者）  
- **返回数据**：  
  ```json
  {
    "code": 200,
    "data": [
      {
        "id": "预约ID",
        "date": "就诊日期（YYYY-MM-DD）",
        "time": "就诊时间（HH:MM）",
        "department": "科室名称",
        "doctor": "医生姓名",
        "status": "状态（待就诊/已完成）"
      }
    ]
  }
  ```

#### 2. 创建预约（已在`index.js`中定义，需完善）
- **作用**：提交新的预约挂号（对应“预约挂号”功能）  
- **请求方式**：`POST /patient/appointments`  
- **所需数据**：  
  ```json
  {
    "departmentId": "科室ID",
    "doctorId": "医生ID",
    "date": "预约日期（YYYY-MM-DD）",
    "time": "预约时间段（如09:00-10:00）"
  }
  ```
- **返回数据**：  
  ```json
  { "code": 200, "message": "预约成功", "data": { "appointmentId": "新预约ID" } }
  ```

#### 3. 取消预约（新增）
- **作用**：取消“待就诊”状态的预约（对应预约表格的“取消预约”按钮）  
- **请求方式**：`DELETE /patient/appointments/{appointmentId}`  
- **所需数据**：路径参数`appointmentId`（预约ID）  
- **返回数据**：  
  ```json
  { "code": 200, "message": "取消成功" }
  ```

#### 4. 获取检查报告（已在`index.js`中定义，需完善）
- **作用**：获取患者的检查报告列表（对应“检查报告”菜单）  
- **请求方式**：`GET /patient/reports`  
- **所需数据**：无（通过token识别患者）  
- **返回数据**：  
  ```json
  {
    "code": 200,
    "data": [
      {
        "id": "报告ID",
        "name": "报告名称（如血常规）",
        "date": "检查日期",
        "status": "状态（已完成/待审核）",
        "url": "报告详情URL（可选）"
      }
    ]
  }
  ```

#### 5. 获取健康提醒（新增）
- **作用**：获取患者的健康提醒/日程（对应`PatientDashboard`的“健康提醒”时间线）  
- **请求方式**：`GET /patient/reminders`  
- **所需数据**：无  
- **返回数据**：  
  ```json
  {
    "code": 200,
    "data": [
      {
        "id": "提醒ID",
        "time": "提醒时间（如今天 09:00）",
        "content": "提醒内容（如“您有一个预约：内科 - 李医生”）",
        "type": "类型（预约/复诊/体检，用于图标颜色）"
      }
    ]
  }
  ```


### 三、医生端接口（`doctorAPI`）
#### 1. 获取今日患者列表（新增）
- **作用**：获取医生今日接诊的患者（对应`DoctorDashboard`的“今日患者列表”表格）  
- **请求方式**：`GET /doctor/patients/today`  
- **所需数据**：无（通过token识别医生）  
- **返回数据**：  
  ```json
  {
    "code": 200,
    "data": [
      {
        "id": "患者ID",
        "name": "姓名",
        "age": "年龄",
        "gender": "性别",
        "time": "预约时间",
        "complaint": "主诉",
        "status": "状态（待接诊/诊断中/已完成）"
      }
    ]
  }
  ```

#### 2. 获取医生统计数据（新增）
- **作用**：获取医生的今日接诊、待接诊等统计数据（对应医生端“统计卡片”）  
- **请求方式**：`GET /doctor/statistics`  
- **所需数据**：无  
- **返回数据**：  
  ```json
  {
    "code": 200,
    "data": {
      "todayPatients": 28, // 今日接诊
      "pendingPatients": 15, // 待接诊
      "pendingRecords": 42, // 待审核病历
      "consultRequests": 3 // 会诊请求
    }
  }
  ```

#### 3. 获取AI诊断建议（新增）
- **作用**：根据患者信息获取AI辅助诊断建议（对应“AI辅助诊断”卡片）  
- **请求方式**：`GET /doctor/ai-diagnose/{patientId}`  
- **所需数据**：路径参数`patientId`（患者ID）  
- **返回数据**：  
  ```json
  {
    "code": 200,
    "data": {
      "possibleDiagnosis": "上呼吸道感染（置信度：85%）",
      "suggestedTests": "血常规、C反应蛋白",
      "medicationSuggestions": "阿莫西林胶囊、布洛芬缓释片",
      "notes": "注意休息，多饮水"
    }
  }
  ```

#### 4. 创建电子处方（已在`index.js`中定义，需完善）
- **作用**：为患者开具处方（对应“开处方”按钮）  
- **请求方式**：`POST /doctor/prescriptions`  
- **所需数据**：  
  ```json
  {
    "patientId": "患者ID",
    "medicines": [
      { "name": "药品名称", "spec": "规格", "dosage": "剂量", "frequency": "频次" }
    ],
    "notes": "用药说明（可选）"
  }
  ```
- **返回数据**：  
  ```json
  { "code": 200, "message": "处方创建成功", "data": { "prescriptionId": "处方ID" } }
  ```


### 四、药房端接口（`pharmacyAPI`）
#### 1. 获取待配药处方（已在`index.js`中定义，需完善）
- **作用**：获取药房需要处理的处方（对应`PharmacyDashboard`的“待配药处方”表格）  
- **请求方式**：`GET /pharmacy/prescriptions`  
- **所需数据**：查询参数`filter`（可选，all/urgent/normal，用于筛选）  
- **返回数据**：  
  ```json
  {
    "code": 200,
    "data": [
      {
        "id": "处方号",
        "patientName": "患者姓名",
        "doctorName": "开方医生",
        "time": "开方时间",
        "priority": "优先级（急诊/普通）",
        "medicines": "药品列表（字符串拼接）"
      }
    ]
  }
  ```

#### 2. 配药操作（已在`index.js`中定义，需完善）
- **作用**：标记处方为“已配药”（对应“配药”按钮）  
- **请求方式**：`POST /pharmacy/prescriptions/{id}/dispense`  
- **所需数据**：路径参数`id`（处方号）  
- **返回数据**：  
  ```json
  { "code": 200, "message": "配药成功" }
  ```

#### 3. 获取库存预警（新增）
- **作用**：获取库存不足或即将过期的药品（对应“库存预警”表格）  
- **请求方式**：`GET /pharmacy/inventory/alerts`  
- **所需数据**：无  
- **返回数据**：  
  ```json
  {
    "code": 200,
    "data": [
      {
        "id": "药品ID",
        "name": "药品名称",
        "spec": "规格",
        "stock": "当前库存",
        "threshold": "预警阈值",
        "expiry": "最近效期",
        "alertType": "预警类型（库存不足/即将过期）"
      }
    ]
  }
  ```

#### 4. 获取药房统计数据（新增）
- **作用**：获取待配药处方数、库存种类等统计（对应药房端“统计卡片”）  
- **请求方式**：`GET /pharmacy/statistics`  
- **所需数据**：无  
- **返回数据**：  
  ```json
  {
    "code": 200,
    "data": {
      "pendingPrescriptions": 45, // 待配药处方
      "medicineTypes": 1258, // 库存药品种类
      "stockAlerts": 12, // 库存预警
      "expiringSoon": 5 // 即将过期
    }
  }
  ```


### 五、管理端接口（`adminAPI`）
#### 1. 获取管理统计数据（已在`index.js`中定义，需完善）
- **作用**：获取医院运营数据（对应`AdminDashboard`的“统计卡片”）  
- **请求方式**：`GET /admin/statistics`  
- **所需数据**：无  
- **返回数据**：  
  ```json
  {
    "code": 200,
    "data": {
      "outpatientVolume": 1245, // 今日门诊量
      "revenue": 328000, // 今日收入（分/元，需约定单位）
      "bedUsageRate": 85, // 床位使用率（%）
      "patientSatisfaction": 4.8 // 患者满意度
    }
  }
  ```

#### 2. 获取门诊量趋势数据（新增）
- **作用**：获取近期门诊量趋势（用于折线图）  
- **请求方式**：`GET /admin/statistics/outpatient-trend`  
- **所需数据**：查询参数`days`（如7，获取近7天数据）  
- **返回数据**：  
  ```json
  {
    "code": 200,
    "data": {
      "labels": ["周一", "周二", ...], // 日期标签
      "values": [1120, 1320, ...] // 对应日期的门诊量
    }
  }
  ```

#### 3. 获取科室分布数据（新增）
- **作用**：获取各科室接诊量分布（用于饼图）  
- **请求方式**：`GET /admin/statistics/department-distribution`  
- **所需数据**：无  
- **返回数据**：  
  ```json
  {
    "code": 200,
    "data": [
      { "name": "内科", "value": 156 },
      { "name": "外科", "value": 98 },
      ...
    ]
  }
  ```

#### 4. 获取科室列表（已在`index.js`中定义，需完善）
- **作用**：获取医院科室信息（对应“科室概览”表格）  
- **请求方式**：`GET /admin/departments`  
- **所需数据**：无  
- **返回数据**：  
  ```json
  {
    "code": 200,
    "data": [
      {
        "id": "科室ID",
        "name": "科室名称",
        "director": "科室主任",
        "doctors": 15, // 医生数
        "beds": 50, // 床位数
        "occupancy": 85, // 床位使用率（%）
        "todayPatients": 156, // 今日接诊
        "revenue": 125000 // 本月收入
      }
    ]
  }
  ```

#### 5. 获取系统通知（新增）
- **作用**：获取管理员的系统通知（对应“系统通知”时间线）  
- **请求方式**：`GET /admin/notifications`  
- **所需数据**：无  
- **返回数据**：  
  ```json
  {
    "code": 200,
    "data": [
      {
        "id": "通知ID",
        "time": "通知时间",
        "title": "通知标题（如设备维护提醒）",
        "content": "通知内容"
      }
    ]
  }
  ```


### 总结
以上接口覆盖了各角色页面的核心功能（数据展示、操作交互），实际开发中可根据业务复杂度补充细节（如分页、筛选条件、权限校验等）。接口设计遵循“角色隔离”原则（如`/patient/`、`/doctor/`前缀），便于维护和权限控制。
