# DND 角色塑造平台 · 开发任务清单

## Phase 1：MVP

### 基础工程搭建
- [ ] 初始化 Git 仓库，配置 .gitignore
- [ ] 创建 Django 项目结构（config/apps/data/scripts）
- [ ] 创建 React + TypeScript + Tailwind 项目
- [ ] 编写开发环境 docker-compose.yml（nginx + django + postgresql + redis）
- [ ] 编写 .env.example（含详细中文注释）
- [ ] 配置 Django settings（base/development/production 三套）
- [ ] 配置 Django REST Framework + simplejwt
- [ ] 配置 CORS（django-cors-headers）

### 游戏数据准备（dnd5e_2014）
- [ ] 整理 rulesets.json（定义规则集）
- [ ] 整理 races.json（13个基础种族 + 亚种族）
- [ ] 整理 classes.json（12个职业 + 各等级特性）
- [ ] 整理 subclasses.json（各职业至少1个子职业）
- [ ] 整理 backgrounds.json（基础背景）
- [ ] 整理 spells.json（至少覆盖1-5环常用法术）
- [ ] 整理 shared/conditions.json、damage_types.json
- [ ] 编写 scripts/import_gamedata.py 导入脚本
- [ ] 验证导入脚本正确运行

### 后端：用户系统（users app）
- [ ] 自定义 User 模型（AbstractUser，UUID主键，email登录）
- [ ] 注册 API（POST /api/auth/register/）
- [ ] 登录 API（POST /api/auth/login/，返回JWT）
- [ ] Token 刷新 API
- [ ] 当前用户信息 API（GET /api/auth/me/）

### 后端：游戏数据（gamedata app）
- [ ] Ruleset 模型 + API
- [ ] Race / Subrace 模型 + API（含过滤）
- [ ] CharClass / Subclass 模型 + API
- [ ] Background 模型 + API
- [ ] Spell 模型 + API（含多条件过滤）
- [ ] Feat 模型 + API

### 后端：角色管理（characters app）
- [ ] Character 模型（完整字段，含JSONB字段）
- [ ] 角色列表/创建 API
- [ ] 角色详情/更新/删除 API
- [ ] 角色分享 API（生成share_token，切换is_public）
- [ ] 公开分享页 API（无需登录）
- [ ] 权限控制（只能访问自己的角色）

### 前端：基础框架
- [ ] 配置 React Router（页面路由）
- [ ] 配置 Axios（API 请求层，含 JWT 拦截器）
- [ ] 配置 Zustand（authStore / wizardStore / characterStore）
- [ ] 实现 JWT 自动刷新逻辑
- [ ] 实现受保护路由（未登录跳转登录页）

### 前端：用户认证页面
- [ ] 登录页面
- [ ] 注册页面
- [ ] 表单验证

### 前端：角色创建向导（核心）
- [ ] 向导容器组件（步骤导航 + 进度条）
- [ ] Step 1：选择规则集
- [ ] Step 2：基础信息（名字/性别/年龄/外貌）
- [ ] Step 3：选择种族（卡片列表 + 亚种族选择 + 特性展示）
- [ ] Step 4：选择职业（卡片列表 + 特性展示）
- [ ] Step 5：分配属性值（标准数组拖拽 / 点数购买 / 手动输入）
- [ ] Step 6：选择背景（列表 + 性格特质随机/自定义）
- [ ] Step 7：选择法术（法术类职业专属，可跳过）
- [ ] Step 8：初始装备
- [ ] 向导完成 → 角色卡预览 → 提交创建

### 前端：角色管理页面
- [ ] 我的角色列表页（角色卡片网格）
- [ ] 角色详情/查看页（完整角色卡展示）
- [ ] 角色编辑页（更新角色信息）
- [ ] 角色公开分享页（share token 访问，只读）
- [ ] 移动端响应式适配

### 部署文档
- [ ] README.md（项目介绍 + 快速开始）
- [ ] docs/deployment.md（详细部署指南，面向零基础）
- [ ] docs/development.md（本地开发环境搭建）
- [ ] docs/data-import.md（游戏数据导入说明）
- [ ] 生产环境 docker-compose.prod.yml
- [ ] nginx/nginx.prod.conf（含 SSL 配置说明）

---

## Phase 2：核心体验完善

### 规则文档库
- [ ] RuleDocument 模型（树形结构 + tsvector）
- [ ] 编写 scripts/import_chm.py（解析CHM源码→存入数据库）
- [ ] 规则文档目录树 API
- [ ] 规则文档单页内容 API
- [ ] 规则文档全文搜索 API
- [ ] 前端：规则文档页面（左树右文布局）
- [ ] 前端：搜索框（实时建议）
- [ ] 向导中的规则快速预览面板

### 优化
- [ ] 移动端角色卡详细优化
- [ ] 角色广场页面（浏览公开角色）
- [ ] GitHub Actions CI/CD 配置

---

## Phase 3：AIGC 功能

### AI 基础设施
- [ ] AIProvider 抽象接口设计
- [ ] OpenAIProvider 实现
- [ ] ClaudeProvider 实现（可选）
- [ ] QianwenProvider 实现（可选）
- [ ] 环境变量配置切换逻辑

### AIGC 功能
- [ ] 背景故事生成 API + 前端（角色详情页触发）
- [ ] 角色扮演助手 API + 前端对话界面
- [ ] 种族沉浸式描述（向导Step3中展示，带缓存）
- [ ] 角色立绘生成（接入图像API + COS存储）

---

## Phase 4：锦上添花

- [ ] PDF 导出（WeasyPrint，标准5e角色卡模板）
- [ ] Excel 导出
- [ ] D&D 5e 2024版数据整理 + 导入
- [ ] 用户头像上传
- [ ] 角色升级辅助（自动计算新等级特性）
