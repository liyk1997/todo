# 贡献指南

感谢您对 Todo 项目的关注！我们欢迎任何形式的贡献。

## 🤝 如何贡献

### 报告问题
- 在提交问题之前，请先搜索现有的 [Issues](https://github.com/liyk1997/todo/issues)
- 使用清晰、描述性的标题
- 提供详细的问题描述和复现步骤
- 包含相关的错误信息和截图

### 提交功能请求
- 详细描述新功能的用途和价值
- 解释为什么这个功能对项目有益
- 提供可能的实现方案

### 代码贡献

#### 开发环境设置
1. Fork 本仓库
2. 克隆你的 Fork：
   ```bash
   git clone https://github.com/your-username/todo.git
   cd todo
   ```
3. 安装依赖：
   ```bash
   npm install
   cd backend && pip install -r requirements.txt
   ```
4. 创建新分支：
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### 代码规范
- **前端**：遵循 Vue 3 + TypeScript 最佳实践
- **后端**：遵循 Python PEP 8 代码规范
- **提交信息**：使用清晰、描述性的提交信息

#### 测试
- 确保所有现有测试通过
- 为新功能添加相应的测试
- 测试多平台兼容性（H5、小程序等）

#### 提交 Pull Request
1. 确保代码符合项目规范
2. 更新相关文档
3. 提供清晰的 PR 描述
4. 关联相关的 Issues

## 📝 开发指南

### 项目结构
```
src/
├── pages/          # 页面组件
├── components/     # 公共组件
├── api/           # API 接口
└── static/        # 静态资源

backend/
├── main.py        # FastAPI 主应用
├── models.py      # 数据模型
├── database.py    # 数据库操作
└── websocket_manager.py # WebSocket 管理
```

### 开发流程
1. 创建功能分支
2. 开发新功能
3. 编写测试
4. 更新文档
5. 提交 PR

### 代码审查
- 所有 PR 都需要经过代码审查
- 维护者会及时回复和处理
- 根据反馈进行必要的修改

## 🎯 优先级

我们特别欢迎以下类型的贡献：
- 🐛 Bug 修复
- 📱 多平台兼容性改进
- 🎨 UI/UX 优化
- 📚 文档完善
- 🔧 性能优化
- 🌐 国际化支持

## 📞 联系我们

如有任何问题，欢迎通过以下方式联系：
- 提交 [Issue](https://github.com/liyk1997/todo/issues)
- 发起 [Discussion](https://github.com/liyk1997/todo/discussions)

感谢您的贡献！🎉