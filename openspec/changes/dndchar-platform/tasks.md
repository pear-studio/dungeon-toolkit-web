# Dungeon Toolkit · 开发任务清单

## Phase 1：MVP

### 基础工程搭建
- [x] 初始化 Git 仓库，配置 .gitignore
- [x] 创建 Django 项目结构（config/apps/data/scripts）
- [x] 创建 React + TypeScript + Tailwind 项目
- [x] 编写开发环境 docker-compose.yml（nginx + django + postgresql + redis）
- [x] 编写 .env.example（含详细中文注释）
- [x] 配置 Django settings（base/development/production 三套）
- [x] 配置 Django REST Framework + simplejwt
- [x] 配置 CORS（django-cors-headers）

### 游戏数据准备（dnd5e_2014）
- [x] 整理 rulesets.json（定义规则集）
- [x] 整理 races.json（9个基础种族 + 亚种族）
- [x] 整理 classes.json（12个职业，含 hit_die / primary_ability / saving_throws / is_spellcaster）
- [x] 整理 backgrounds.json（13个背景，含技能熟练、工具熟练、特性描述）
- [ ] 整理 subclasses.json（各职业至少1个子职业）
- [ ] 整理 spells.json（至少覆盖1-5环常用法术）
- [ ] 整理 shared/conditions.json、damage_types.json
- [x] 编写 scripts/import_gamedata.py 导入脚本
- [x] 验证导入脚本正确运行

### 后端：用户系统（users app）
- [x] 自定义 User 模型（AbstractUser，UUID主键，email登录）
- [x] 注册 API（POST /api/auth/register/）
- [x] 登录 API（POST /api/auth/login/，返回JWT）
- [x] Token 刷新 API
- [x] 当前用户信息 API（GET /api/auth/me/）

### 后端：游戏数据（gamedata app）
- [x] Ruleset 模型 + API
- [x] Race / Subrace 模型 + API（含过滤）
- [x] CharClass / Subclass 模型 + API
- [x] Background 模型 + API
- [x] Spell 模型 + API（含多条件过滤）
- [ ] Feat 模型 + API

### 后端：角色管理（characters app）
- [x] Character 模型（完整字段，含JSONB字段）
- [x] 角色列表/创建 API
- [x] 角色详情/更新/删除 API
- [x] 角色分享 API（生成share_token，切换is_public）
- [x] 公开分享页 API（无需登录）
- [x] 权限控制（只能访问自己的角色）

### 前端：基础框架
- [x] 配置 React Router（页面路由）
- [x] 配置 Axios（API 请求层，含 JWT 拦截器）
- [x] 配置 Zustand（authStore）
- [x] 配置 Zustand（wizardStore / characterStore / gamedataStore）
- [ ] 实现 JWT 自动刷新逻辑
- [x] 实现受保护路由（未登录跳转登录页）
- [x] api.ts 统一 PagedResponse<T> 处理 DRF 分页

### 前端：用户认证页面
- [x] 登录页面
- [x] 注册页面
- [ ] 表单验证（待完善）

### 前端：角色创建向导（核心）
- [x] 向导容器组件（CreatePage，单页滚动式）
- [x] Step 1：选择规则集（RulesetSection，支持锁定/更换）
- [x] Step 2：选择种族（RaceSection，含自定义种族/亚种族/性别/年龄滑条）
- [x] Step 3：选择职业（ClassSection，含自定义职业/职业详情展示）
- [x] Step 4：分配属性值（AbilityScoresSection，标准数组/购点法/随机骰点）
- [x] Step 5：描述角色（DescribeSection，名字/背景/阵营/外貌/个性细节）
- [x] 向导完成 → 提交创建 → 跳转 Dashboard
- [x] 统一深色主题（DESIGN_SYSTEM.md 规范落地）
- [ ] Step 6：选择法术（法术类职业专属）
- [ ] Step 7：初始装备
- [ ] 角色卡完整预览页

### 前端：角色管理页面
- [x] 我的角色列表页（Dashboard，角色卡片网格，CharacterCard 组件）
- [ ] 角色详情/查看页（完整角色卡展示）
- [ ] 角色编辑页（更新角色信息）
- [ ] 角色公开分享页（share token 访问，只读）
- [ ] 移动端响应式适配

### 部署文档
- [ ] README.md（项目介绍 + 快速开始）
- [ ] docs/deployment.md（详细部署指南，面向零基础）
- [x] docs/frontend-conventions.md（前端开发规范）
- [x] DESIGN_SYSTEM.md（UI 设计规范 Token）
- [ ] docs/development.md（本地开发环境搭建）
- [ ] docs/data-import.md（游戏数据导入说明）
- [ ] 生产环境 docker-compose.prod.yml
- [ ] nginx/nginx.prod.conf（含 SSL 配置说明）

### 测试
- [x] unittest/test_api.py（后端 API smoke test，覆盖注册/登录/角色/游戏数据接口）

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