# Python-100天学习平台

基于Django + Vue 3的Python学习平台,提供系统化的Python课程、在线练习和学习进度追踪。

## 🎯 项目特性

- ✅ **完整课程体系**: 100天从基础到进阶的系统化学习路径
- ✅ **在线练习系统**: 支持在线编写和运行Python代码
- ✅ **学习进度追踪**: 可视化学习进度和统计数据
- ✅ **笔记分享**: 记录和分享学习笔记
- ✅ **前后端分离**: Django REST Framework + Vue 3
- ✅ **容器化部署**: Docker + Docker Compose一键启动

## 🏗️ 技术栈

### 后端
- Django 4.2 + Django REST Framework
- MySQL 8.0 (数据库)
- Redis 7.0 (缓存)
- Celery (异步任务)
- JWT认证

### 前端
- Vue 3 + Vite
- Element Plus (UI组件库)
- Pinia (状态管理)
- Axios (HTTP客户端)
- ECharts (数据可视化)

## 📦 快速开始

### 使用Docker Compose(推荐)

1. 克隆项目
```bash
git clone https://github.com/marvel1203/Python-100-Days.git
cd Python-100-Days
```

2. 配置环境变量
```bash
cd backend
cp .env.example .env
# 编辑.env文件,配置数据库密码等
```

3. 启动所有服务
```bash
docker-compose up -d
```

4. 访问应用
- 前端: http://localhost:9540
- 后端API: http://localhost:8020
- API文档: http://localhost:8020/swagger/

### 本地开发

#### 后端开发

1. 创建虚拟环境
```bash
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件
```

4. 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

5. 创建超级用户
```bash
python manage.py createsuperuser
```

6. 启动开发服务器
```bash
python manage.py runserver 8020
```

#### 前端开发

1. 安装依赖
```bash
cd frontend
npm install
```

2. 启动开发服务器
```bash
npm run dev
```

访问 http://localhost:9540

## 📁 项目结构

```
Python-100-Days/
├── backend/                 # Django后端
│   ├── apps/
│   │   ├── courses/        # 课程管理
│   │   ├── exercises/      # 练习系统
│   │   ├── users/          # 用户系统
│   │   ├── community/      # 社区功能
│   │   └── analytics/      # 数据分析
│   ├── config/             # 配置文件
│   ├── common/             # 公共模块
│   └── requirements.txt
├── frontend/               # Vue 3前端
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 公共组件
│   │   ├── api/           # API接口
│   │   ├── stores/        # Pinia状态
│   │   └── router/        # 路由配置
│   └── package.json
├── nginx/                  # Nginx配置
├── docker-compose.yml      # Docker编排
└── docs/                   # 文档
```

## 🔧 核心功能

### 1. 课程管理
- 课程分类和列表
- 课程详情展示
- Markdown内容渲染
- 代码高亮显示
- 学习资源下载

### 2. 练习系统
- 在线代码编辑器
- 代码提交和执行
- 测试用例验证
- 提交历史记录

### 3. 学习追踪
- 学习进度记录
- 统计数据可视化
- 打卡签到功能
- 学习时长统计

### 4. 用户系统
- JWT认证
- 用户注册/登录
- 个人中心
- 权限管理

## 📊 API文档

启动后端服务后,访问以下地址查看API文档:
- Swagger UI: http://localhost:8020/swagger/
- ReDoc: http://localhost:8020/redoc/

## 🚀 部署

### 生产环境部署

1. 修改环境变量
```bash
# backend/.env
DEBUG=False
ALLOWED_HOSTS=your-domain.com
SECRET_KEY=your-production-secret-key
```

2. 构建和启动
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. 收集静态文件
```bash
docker-compose exec backend python manage.py collectstatic
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request!

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证

## 👨‍💻 作者

骆昊 - [@jackfrued](https://github.com/jackfrued)

## 🙏 致谢

- 感谢所有贡献者
- 感谢开源社区的支持
