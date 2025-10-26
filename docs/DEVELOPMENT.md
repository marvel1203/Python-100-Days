# Python-100天学习平台开发指南

## 开发环境设置

### 前置要求
- Docker Desktop
- Node.js 18+ (本地开发)
- Python 3.11+ (本地开发)
- Git

### 快速启动

1. **使用自动化脚本启动**
```bash
chmod +x dev-start.sh
./dev-start.sh
```

2. **手动启动**
```bash
# 启动所有服务
docker-compose up -d

# 执行数据库迁移
docker-compose exec backend python manage.py migrate

# 创建超级用户
docker-compose exec backend python manage.py createsuperuser
```

## 开发工作流

### 后端开发

1. **修改代码后重启服务**
```bash
docker-compose restart backend
```

2. **查看后端日志**
```bash
docker-compose logs -f backend
```

3. **进入后端容器**
```bash
docker-compose exec backend bash
```

4. **创建新的Django应用**
```bash
cd backend
python manage.py startapp app_name
# 将应用添加到 config/settings.py 的 INSTALLED_APPS
```

5. **数据库操作**
```bash
# 创建迁移文件
docker-compose exec backend python manage.py makemigrations

# 执行迁移
docker-compose exec backend python manage.py migrate

# 进入Django shell
docker-compose exec backend python manage.py shell
```

### 前端开发

1. **本地开发(推荐)**
```bash
cd frontend
npm install
npm run dev
```

2. **在容器中开发**
```bash
# 查看前端日志
docker-compose logs -f frontend

# 重启前端服务
docker-compose restart frontend
```

3. **构建生产版本**
```bash
cd frontend
npm run build
```

## 代码规范

### Python代码规范
- 遵循PEP 8规范
- 使用Black进行代码格式化
- 使用flake8进行代码检查

```bash
# 安装开发工具
pip install black flake8

# 格式化代码
black backend/

# 检查代码
flake8 backend/
```

### Vue代码规范
- 使用ESLint
- 组件命名使用PascalCase
- 文件命名使用kebab-case

## 常见问题

### 1. 端口冲突
如果8020或9540端口被占用,修改docker-compose.yml中的端口映射:
```yaml
services:
  backend:
    ports:
      - "8021:8020"  # 改为其他端口
```

### 2. 数据库连接失败
检查MySQL服务是否启动:
```bash
docker-compose ps mysql
docker-compose logs mysql
```

### 3. 前端无法访问后端API
确认后端服务正常运行,检查CORS配置:
```python
# backend/config/settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:9540',
]
```

### 4. Redis连接失败
检查Redis服务:
```bash
docker-compose ps redis
docker-compose exec redis redis-cli ping
```

## 测试

### 后端测试
```bash
# 运行所有测试
docker-compose exec backend python manage.py test

# 运行特定应用的测试
docker-compose exec backend python manage.py test apps.courses
```

### 前端测试
```bash
cd frontend
npm run test
```

## 数据库管理

### 导出数据
```bash
# 导出所有数据
docker-compose exec backend python manage.py dumpdata > backup.json

# 导出特定应用数据
docker-compose exec backend python manage.py dumpdata courses > courses_data.json
```

### 导入数据
```bash
docker-compose exec backend python manage.py loaddata backup.json
```

### 重置数据库
```bash
# 删除所有迁移
find backend/apps -path "*/migrations/*.py" -not -name "__init__.py" -delete
find backend/apps -path "*/migrations/*.pyc" -delete

# 删除数据库
docker-compose down -v

# 重新创建
docker-compose up -d
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

## 性能优化

### 后端优化
1. 使用select_related和prefetch_related减少数据库查询
2. 合理使用Redis缓存
3. 数据库索引优化
4. 使用Django Debug Toolbar分析性能

### 前端优化
1. 路由懒加载
2. 图片压缩和懒加载
3. 使用Vite的代码分割
4. 合理使用Vue的keep-alive

## 部署准备

### 环境变量配置
生产环境需要修改以下配置:

```bash
# backend/.env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com
DB_PASSWORD=strong-password
```

### 安全检查清单
- [ ] DEBUG设置为False
- [ ] 使用强密码
- [ ] 配置HTTPS
- [ ] 设置正确的ALLOWED_HOSTS
- [ ] 保护敏感信息(SECRET_KEY等)
- [ ] 配置防火墙规则
- [ ] 启用CSRF保护
- [ ] 配置日志监控

## 获取帮助

- 查看API文档: http://localhost:8020/swagger/
- 项目Issue: https://github.com/marvel1203/Python-100-Days/issues
- 开发文档: 见docs目录
