# 🎓 Python-100天学习平台 - 开发版

> 基于Django + Vue 3的Python系统化学习平台

## ✨ 项目已完成

- ✅ 后端Django项目完整搭建(Django 4.2 + DRF)
- ✅ 前端Vue 3项目初始化(Vite + Element Plus)
- ✅ Docker容器化部署配置
- ✅ 核心数据模型设计(课程、练习、进度等)
- ✅ RESTful API接口开发
- ✅ 前端核心页面和组件
- ✅ JWT认证配置
- ✅ Redis缓存和Celery异步任务

## 🚀 快速启动

### 方式一: Docker Compose(推荐)

```bash
# 1. 配置后端环境变量
cd backend
cp .env.example .env
# 编辑.env,设置数据库密码等

# 2. 启动所有服务(MySQL, Redis, Django, Celery, Vue, Nginx)
cd ..
chmod +x dev-start.sh
./dev-start.sh
```

访问:
- 前端: http://localhost:9540
- 后端API: http://localhost:8020
- API文档: http://localhost:8020/swagger/
- 管理后台: http://localhost:8020/admin/

### 方式二: 本地开发

**后端:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8020
```

**前端:**
```bash
cd frontend
npm install
npm run dev  # 访问 http://localhost:9540
```

## 📁 项目结构

```
Python-100-Days/
├── backend/                 # Django后端
│   ├── apps/
│   │   ├── courses/        # 课程管理(已完成)
│   │   ├── exercises/      # 练习系统(已完成)
│   │   ├── users/          # 用户系统(待完善)
│   │   ├── community/      # 社区功能(待开发)
│   │   └── analytics/      # 数据分析(待开发)
│   ├── config/             # Django配置
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Vue 3前端
│   ├── src/
│   │   ├── views/         # 页面组件(已完成)
│   │   ├── components/    # 公共组件(已完成)
│   │   ├── api/           # API封装(已完成)
│   │   ├── stores/        # Pinia状态(已完成)
│   │   └── router/        # 路由配置(已完成)
│   └── package.json
├── docs/                   # 项目文档
│   ├── 开发规划.md         # 详细开发规划
│   ├── DEVELOPMENT.md      # 开发指南
│   ├── TODO.md             # 待办事项
│   └── PROJECT_SUMMARY.md  # 项目总结
├── nginx/                  # Nginx配置
├── docker-compose.yml      # Docker编排
└── dev-start.sh           # 一键启动脚本
```

## 📚 核心功能

### 已实现
- ✅ 课程分类和课程管理
- ✅ 课时详情展示
- ✅ Markdown内容渲染
- ✅ 学习进度追踪
- ✅ 练习题目管理
- ✅ 代码提交记录
- ✅ API文档(Swagger)

### 待开发
- ⏳ 用户登录注册(JWT已配置)
- ⏳ 课程内容导入脚本
- ⏳ 在线代码编辑器(Monaco Editor)
- ⏳ 代码在线运行(Docker沙箱)
- ⏳ 数据可视化(ECharts)
- ⏳ 社区问答功能

## 🛠️ 技术栈

**后端:**
- Django 4.2 + Django REST Framework
- MySQL 8.0 + Redis 7.0
- Celery(异步任务)
- JWT认证

**前端:**
- Vue 3 + Vite
- Element Plus
- Pinia(状态管理)
- Axios
- Markdown-it + Highlight.js

**部署:**
- Docker + Docker Compose
- Nginx

## 📖 文档

- **开发规划**: `docs/开发规划.md` - 查看详细的功能规划和架构设计
- **开发指南**: `docs/DEVELOPMENT.md` - 开发流程和常见问题
- **待办事项**: `docs/TODO.md` - 功能开发优先级
- **项目总结**: `docs/PROJECT_SUMMARY.md` - 当前完成情况

## 🔧 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 重启服务
docker-compose restart backend

# 进入容器
docker-compose exec backend bash

# 停止所有服务
docker-compose down

# 数据库迁移
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

## 🎯 下一步开发建议

1. **立即可做**
   - 实现用户登录注册页面
   - 编写课程导入脚本(从Day01-100的MD文件)
   - 完善课程详情页样式

2. **本周目标**
   - 集成Monaco Editor代码编辑器
   - 实现Python代码在线执行
   - 数据可视化仪表盘

3. **本月目标**
   - 社区功能开发
   - 性能优化
   - 单元测试

## 🐛 已知问题

- 用户登录注册功能未实现(页面已创建,后端JWT已配置)
- 部分视图组件为占位页面(ExerciseDetail, Notes等)
- 课程内容需要导入(当前数据库为空)

## 📞 获取帮助

- 项目Issue: https://github.com/marvel1203/Python-100-Days/issues
- 查看API文档: http://localhost:8020/swagger/ (启动后访问)
- 开发文档: `docs/` 目录

---

**当前状态**: ✅ MVP阶段完成,可以开始迭代开发

**作者**: 骆昊 | **License**: MIT
