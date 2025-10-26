# 智慧医疗管理系统

基于 Vue 3 + Vite + Element Plus 的智慧医疗管理系统前端项目。

## 功能特性

- 🏥 **多角色支持**：患者、医生、药房、管理员四种角色
- 📱 **响应式设计**：适配桌面端和移动端
- 🎨 **现代化UI**：基于 Element Plus 组件库
- 🔐 **权限管理**：基于角色的路由守卫
- 📊 **数据可视化**：使用 ECharts 展示统计数据
- 💾 **状态管理**：使用 Pinia 进行状态管理

## 技术栈

- Vue 3.4
- Vite 5.0
- Vue Router 4.2
- Pinia 2.1
- Element Plus 2.5
- ECharts 5.4
- Axios 1.6

## 快速开始

### 安装依赖

\`\`\`bash
npm install
\`\`\`

### 开发模式

\`\`\`bash
npm run dev
\`\`\`

访问 http://localhost:3000

### 构建生产版本

\`\`\`bash
npm run build
\`\`\`

### 预览生产版本

\`\`\`bash
npm run preview
\`\`\`

## 项目结构

\`\`\`
src/
├── api/              # API 接口
├── assets/           # 静态资源
├── components/       # 公共组件
├── router/           # 路由配置
├── store/            # 状态管理
├── styles/           # 全局样式
├── utils/            # 工具函数
├── views/            # 页面组件
│   ├── Login.vue           # 登录页
│   ├── PatientDashboard.vue    # 患者端
│   ├── DoctorDashboard.vue     # 医生端
│   ├── PharmacyDashboard.vue   # 药房端
│   └── AdminDashboard.vue      # 管理端
├── App.vue           # 根组件
└── main.js           # 入口文件
\`\`\`

## 演示账号

- 患者：patient / 123456
- 医生：doctor / 123456
- 药房：pharmacy / 123456
- 管理员：admin / 123456

## 主要功能模块

### 患者端
- 预约挂号
- 查看就诊记录
- 检查报告查询
- 处方记录
- 健康管理
- 远程问诊

### 医生端
- 患者列表管理
- 电子病历录入
- 处方开具
- AI辅助诊断
- 会诊申请
- 排班管理

### 药房端
- 处方管理
- 药品配发
- 库存管理
- 预警中心
- 统计报表

### 管理端
- 数据概览
- 科室管理
- 人员管理
- 财务报表
- 设备管理
- 统计分析

## 开发说明

### 环境变量

创建 `.env` 文件配置环境变量：

\`\`\`
VITE_API_BASE_URL=http://localhost:8080/api
\`\`\`

### API 接口

所有 API 接口定义在 `src/api/index.js` 中，目前使用模拟数据。

### 路由守卫

路由守卫在 `src/router/index.js` 中配置，根据用户角色控制页面访问权限。

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## License

MIT
\`\`\`

```text file=".gitignore"
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# Environment variables
.env
.env.local
.env.*.local
