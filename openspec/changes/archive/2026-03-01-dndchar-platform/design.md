# Dungeon Toolkit · 技术设计文档

## 系统架构总览

```
用户浏览器
    │
    ▼ HTTPS
┌─────────────────────────────────────────┐
│              腾讯云 CVM                  │
│                                         │
│  ┌─────────────┐                        │
│  │    Nginx    │  :80/:443              │
│  │  反向代理   │  静态文件服务            │
│  └──────┬──────┘                        │
│         │                               │
│  ┌──────▼──────┐   ┌────────────────┐  │
│  │   Django    │──▶│  PostgreSQL    │  │
│  │  REST API   │   │  :5432         │  │
│  │  :8000      │   └────────────────┘  │
│  └──────┬──────┘                        │
│         │            ┌───────────────┐  │
│         └───────────▶│    Redis      │  │
│                       │  (可选)       │  │
│                       └───────────────┘  │
└─────────────────────────────────────────┘
         │
         ▼ API 调用
   外部 AI 服务
   (OpenAI / Claude / 通义千问)
```

---

## 项目目录结构

```
dungeon-toolkit/
├── docker-compose.yml           # 开发环境
├── docker-compose.prod.yml      # 生产环境
├── backend/                     # (见下方 backend 目录)
│   └── .env.example             # 环境变量模板（含详细注释）
├── README.md                    # 项目介绍 + 快速开始
│
├── docs/                        # 详细文档
│   ├── deployment.md            # 部署指南（面向小白）
│   ├── development.md           # 开发环境搭建
│   ├── data-import.md           # 游戏数据导入说明
│   └── api.md                   # API 文档
│
├── backend/                     # Django 后端
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/                  # Django 项目配置
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── users/               # 用户认证
│   │   ├── characters/          # 角色管理
│   │   ├── gamedata/            # 游戏数据（种族/职业/法术等）
│   │   ├── rules/               # 规则文档库
│   │   └── aigc/                # AI 功能
│   ├── data/                    # 游戏数据 JSON 文件
│   │   ├── rulesets.json
│   │   ├── dnd5e_2014/
│   │   │   ├── races.json
│   │   │   ├── classes.json
│   │   │   ├── subclasses.json
│   │   │   ├── spells.json
│   │   │   ├── backgrounds.json
│   │   │   ├── feats.json
│   │   │   └── equipment.json
│   │   └── shared/
│   │       ├── conditions.json
│   │       └── damage_types.json
│   └── scripts/
│       ├── import_gamedata.py   # 导入 JSON 游戏数据
│       └── import_chm.py        # 导入 CHM 规则文档
│
├── frontend/                    # React 前端
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── pages/
│       │   ├── Home/
│       │   ├── Auth/            # 登录/注册
│       │   ├── Character/       # 角色管理
│       │   ├── Wizard/          # 角色创建向导
│       │   ├── Rules/           # 规则文档库
│       │   └── Share/           # 角色公开分享页
│       ├── components/          # 可复用组件
│       ├── api/                 # API 调用层（axios）
│       ├── store/               # 状态管理（Zustand）
│       └── types/               # TypeScript 类型定义
│
└── nginx/
    ├── nginx.conf               # 开发环境配置
    └── nginx.prod.conf          # 生产环境配置（含 SSL）
```

---

## 数据库模型设计

### 规则集（Ruleset）

```sql
ruleset
├── id            UUID PK
├── system        VARCHAR  -- "dnd"
├── edition       VARCHAR  -- "5e"
├── version       VARCHAR  -- "2014" | "2024"
├── name          VARCHAR  -- "D&D 5e 2014版"
├── is_default    BOOLEAN
├── is_active     BOOLEAN  -- 是否启用（预留切换）
└── description   TEXT
```

### 游戏数据表（gamedata app）

```sql
race                              -- 种族
├── id            UUID PK
├── ruleset_id    FK → ruleset
├── source_ruleset_id  FK → ruleset  -- 方案C：标记数据来源版本
├── name          VARCHAR  -- "精灵"
├── slug          VARCHAR  -- "elf"
├── data          JSONB    -- { speed, size, ability_bonus, traits, ... }
└── description   TEXT

subrace                           -- 亚种族
├── id, ruleset_id, race_id
├── name, slug, data JSONB
└── description

char_class                        -- 职业（class是Python保留字）
├── id, ruleset_id, source_ruleset_id
├── name, slug
├── hit_die       INTEGER  -- 6/8/10/12
├── primary_ability  VARCHAR
├── data          JSONB    -- { saving_throws, armor_profs, level_features:{1:[...],2:[...]} }
└── description

subclass
├── id, ruleset_id, char_class_id
├── name, slug, data JSONB
└── description

background
├── id, ruleset_id, source_ruleset_id
├── name, slug
├── skill_proficiencies  JSONB  -- ["历史", "宗教"]
├── tool_proficiencies   JSONB
├── languages_count      INTEGER
├── equipment            JSONB
├── feature              JSONB  -- { name, description }
└── personality_traits / ideals / bonds / flaws  JSONB  -- 各4条供选择

spell
├── id, ruleset_id, source_ruleset_id
├── name          VARCHAR  -- "火球术"
├── slug          VARCHAR
├── level         INTEGER  -- 0-9（0为戏法）
├── school        VARCHAR  -- "塑能"
├── casting_time  VARCHAR
├── range         VARCHAR
├── components    JSONB    -- ["语言","姿势","材料"]
├── material      VARCHAR  -- 材料成分描述
├── duration      VARCHAR
├── concentration BOOLEAN
├── ritual        BOOLEAN
├── classes       JSONB    -- ["法师","术士"]  可施此法术的职业
└── description   TEXT

feat                             -- 专长
├── id, ruleset_id, source_ruleset_id
├── name, slug, prerequisite, data JSONB
└── description
```

### 用户与角色

```sql
user                             -- 使用 Django AbstractUser
├── id            UUID PK
├── email         VARCHAR UNIQUE
├── username      VARCHAR UNIQUE
├── password      VARCHAR (hashed)
├── avatar        VARCHAR (URL)
├── is_active     BOOLEAN
└── created_at    TIMESTAMP

character
├── id            UUID PK
├── user_id       FK → user
├── ruleset_id    FK → ruleset
│
│  -- 基础信息
├── name          VARCHAR
├── race_id       FK → race
├── subrace_id    FK → subrace (nullable)
├── class_id      FK → char_class
├── subclass_id   FK → subclass (nullable)
├── level         INTEGER  -- 1-20
├── background_id FK → background
├── alignment     VARCHAR  -- "守序善良"
├── experience    INTEGER
│
│  -- 六维属性
├── strength      INTEGER
├── dexterity     INTEGER
├── constitution  INTEGER
├── intelligence  INTEGER
├── wisdom        INTEGER
├── charisma      INTEGER
│
│  -- 战斗属性（部分可自动计算，但存储允许手动覆盖）
├── hp_max        INTEGER
├── hp_current    INTEGER
├── hp_temp       INTEGER
├── armor_class   INTEGER
├── speed         INTEGER
├── initiative    INTEGER
├── proficiency_bonus INTEGER
│
│  -- 死亡豁免
├── death_saves   JSONB    -- { successes: 0, failures: 0 }
│
│  -- 可变/半结构化数据
├── skill_proficiencies   JSONB  -- { "运动": "proficient", "历史": "expertise" }
├── saving_throw_profs    JSONB  -- ["力量", "体质"]
├── class_features        JSONB  -- 职业特性（高度差异化）
├── inventory             JSONB  -- [{ name, qty, weight, equipped, description }]
├── spells                JSONB  -- { known:[], prepared:[], slots:{1:{max:4,used:2},...} }
├── currency              JSONB  -- { cp, sp, ep, gp, pp }
├── languages             JSONB  -- ["通用语","精灵语"]
├── tool_proficiencies    JSONB
├── other_proficiencies   JSONB
│
│  -- 角色扮演信息
├── appearance            TEXT
├── backstory             TEXT
├── personality_traits    TEXT
├── ideals                TEXT
├── bonds                 TEXT
├── flaws                 TEXT
├── notes                 TEXT
│
│  -- AIGC 生成内容
├── ai_portrait_url       VARCHAR  -- AI 生成立绘 URL
├── ai_backstory          TEXT     -- AI 生成的背景故事
│
│  -- 分享
├── is_public             BOOLEAN  DEFAULT FALSE
├── share_token           VARCHAR UNIQUE  -- 公开分享用的随机token
│
└── created_at / updated_at  TIMESTAMP
```

### 规则文档（rules app）

```sql
rule_document                    -- CHM 解析后的文档节点
├── id            UUID PK
├── ruleset_id    FK → ruleset
├── title         VARCHAR
├── slug          VARCHAR
├── parent_id     FK → rule_document (self-referential, nullable)
├── content       TEXT     -- HTML 内容
├── order         INTEGER  -- 同级排序
├── level         INTEGER  -- 目录层级深度
├── search_vector TSVECTOR -- PostgreSQL 全文搜索向量（自动维护）
└── created_at    TIMESTAMP
```

---

## API 设计

### 认证

```
POST   /api/auth/register/        注册
POST   /api/auth/login/           登录（返回JWT）
POST   /api/auth/refresh/         刷新Token
POST   /api/auth/logout/          登出
GET    /api/auth/me/              当前用户信息
```

### 角色管理

```
GET    /api/characters/           我的角色列表
POST   /api/characters/           创建角色
GET    /api/characters/{id}/      角色详情
PUT    /api/characters/{id}/      更新角色
DELETE /api/characters/{id}/      删除角色
POST   /api/characters/{id}/share/    开启/关闭公开分享
GET    /api/characters/share/{token}/ 公开分享页（无需登录）
```

### 游戏数据（向导用）

```
GET    /api/gamedata/rulesets/            规则集列表
GET    /api/gamedata/races/?ruleset=xxx   种族列表
GET    /api/gamedata/races/{slug}/        种族详情（含亚种族）
GET    /api/gamedata/classes/?ruleset=xxx 职业列表
GET    /api/gamedata/classes/{slug}/      职业详情（含各等级特性）
GET    /api/gamedata/spells/?level=1&class=wizard  法术列表（支持过滤）
GET    /api/gamedata/backgrounds/         背景列表
GET    /api/gamedata/feats/               专长列表
```

### 规则文档

```
GET    /api/rules/tree/?ruleset=xxx       目录树
GET    /api/rules/{slug}/                 单页内容
GET    /api/rules/search/?q=火球术         全文搜索
```

### AIGC

```
POST   /api/aigc/portrait/        生成角色立绘（传入角色ID）
POST   /api/aigc/backstory/       生成背景故事
POST   /api/aigc/chat/            角色扮演对话
GET    /api/aigc/race-lore/{slug}/  种族背景故事（AI生成+缓存）
```

---

## 角色创建向导（当前实现：5步 MVP）

> 当前已实现前 5 步核心流程，后续法术/装备步骤在 Phase 2 补全。

```
Step 1: 选择规则集（RulesetSection）
  → 显示可用规则集（D&D 5e 2014版 已上线 / 2024版 即将推出）
  → 选择后点击「确认」锁定规则集，支持「更换」

Step 2: 选择种族（RaceSection）
  → 从后端 /api/gamedata/races/ 动态加载种族卡片
  → 含自定义种族选项
  → 选中后展开：亚种族选择、性别、年龄滑条

Step 3: 选择职业（ClassSection）
  → 从后端 /api/gamedata/classes/ 动态加载职业卡片
  → 展示命中骰、主要属性、施法标记、豁免骰
  → 含自定义职业选项

Step 4: 分配属性值（AbilityScoresSection）
  → 三种方式可选：
    a. 标准数组 [15,14,13,12,10,8] 点击分配
    b. 购点法（27点）± 按钮交互
    c. 随机骰点（4d6取最高3骰）
  → 自动叠加种族属性加值，显示最终值和修正值
  → 底部属性总览面板

Step 5: 描述角色（DescribeSection）
  → 角色名输入
  → 背景选择（从后端动态加载）
  → 阵营选择（3×3方格）
  → 外貌描述（可选）
  → 个性细节：特征/理想/牵绊/缺点（折叠展开）

完成 → 提交创建 → 跳转 Dashboard
```

### 计划补全的步骤（Phase 2）

```
Step 6: 选择法术（仅法术职业显示此步）
Step 7: 初始装备选择
完成 → 角色卡完整预览 → 确认创建
```

---

## AIGC 模块设计

```
AI 提供商抽象层（适配器模式）：

AIProvider (抽象接口)
    ├── OpenAIProvider
    ├── ClaudeProvider
    └── QianwenProvider (通义千问)

通过环境变量 AI_PROVIDER=openai 切换
用户自备 API Key，存于服务端环境变量

功能设计：

1. 角色立绘生成
   → 根据种族/性别/外貌描述拼装 Prompt
   → 调用图像生成 API（DALL-E / Stable Diffusion）
   → 图片存储到对象存储（腾讯云 COS）
   → URL 保存到角色记录

2. 背景故事生成
   → 输入：种族+职业+背景+性格特质+理念+牵绊+缺点
   → 输出：300-500字中文背景故事
   → 支持「重新生成」和「手动编辑」

3. 角色扮演助手
   → 系统Prompt注入角色完整信息
   → 以第一人称扮演角色回答
   → 对话历史存于前端，不持久化到数据库

4. 种族背景故事（沉浸式展示）
   → 在种族选择步骤自动展示
   → AI生成后缓存（Redis/数据库），相同种族不重复生成
```

---

## CHM 文档处理流程

```
CHM 文件（源码文本格式）
    │
    ▼
scripts/import_chm.py
    │
    ├── 解析目录结构（HHC/目录文件）
    ├── 遍历所有 HTML 页面
    ├── 清洗 HTML（保留语义标签，去除样式）
    ├── 建立父子关系（目录树）
    ├── 生成 slug（URL友好）
    │
    ▼
批量写入 PostgreSQL rule_document 表
    │
    ▼
触发 tsvector 更新（全文搜索索引）
    │
    ▼
前端展示：
  左侧：可折叠目录树（懒加载）
  右侧：内容区（HTML渲染）
  顶部：搜索框（实时搜索建议）
```

---

## 数据版本策略（方案C）

```
source_ruleset_id 标记说明：

场景：为 2024 版数据库写入数据时
  - 2024版有改动的内容：source_ruleset_id = 2024版ruleset.id
  - 从2014版复制过来的内容：source_ruleset_id = 2014版ruleset.id

查询时：
  GET /api/gamedata/races/?ruleset=dnd5e_2024
  → 返回 ruleset_id = dnd5e_2024 的所有种族
  → 无需关心 source_ruleset_id（仅用于数据追踪）
```

---

## 部署架构

### Docker Compose 服务

```yaml
services:
  nginx:      # 反向代理 + 静态文件
  backend:    # Django Gunicorn
  frontend:   # React 构建产物（由 nginx 服务）
  db:         # PostgreSQL
  redis:      # Redis（可选）
```

### 环境变量（.env.example）

```
# 数据库
DATABASE_URL=postgresql://user:password@db:5432/dungeon_toolkit

# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# AI 配置（可选，不配置则 AIGC 功能不可用）
AI_PROVIDER=openai          # openai | claude | qianwen
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=            # 留空使用官方，或填代理地址

# 对象存储（AI立绘图片存储，可选）
COS_SECRET_ID=
COS_SECRET_KEY=
COS_BUCKET=
COS_REGION=ap-guangzhou

# Redis（可选）
REDIS_URL=redis://redis:6379/0
```

### GitHub Actions CI/CD

```
触发：push to main 分支

步骤：
  1. 运行后端测试（pytest）
  2. 运行前端构建（npm run build）
  3. 构建 Docker 镜像
  4. SSH 到腾讯云 CVM
  5. docker-compose pull && docker-compose up -d
```

---

## 前端状态管理

```
Zustand stores：

authStore         用户登录状态、JWT Token
characterStore    角色列表数据、CRUD 操作
wizardStore       向导步骤状态（5步临时数据 + rulesetConfirmed 锁定标志）
gamedataStore     规则集/种族/职业/背景（内存缓存，页面初始化时统一 fetchAll）
```

### gamedataStore 数据流规范

```
App 初始化
  └─ gamedataStore.fetchAll()
       ├─ GET /api/gamedata/races/       → PagedResponse<Race>    → store.races[]
       ├─ GET /api/gamedata/classes/     → PagedResponse<Class>   → store.classes[]
       ├─ GET /api/gamedata/backgrounds/ → PagedResponse<Bg>      → store.backgrounds[]
       └─ GET /api/gamedata/rulesets/    → PagedResponse<Ruleset> → store.rulesets[]

各 Section 组件直接读取 store，禁止在组件内单独发起 fetch。
```

### DRF 分页处理

后端默认启用分页，返回格式为：

```json
{ "count": 9, "next": null, "previous": null, "results": [...] }
```

前端 `api.ts` 统一使用 `PagedResponse<T>` 接口处理，
`gamedataStore` 中取 `res.data.results` 存入 store。

---

## UI 设计规范（Design System）

> 完整规范见根目录 `DESIGN_SYSTEM.md`，以下为核心原则摘要。

| 规则 | 规范值 |
|------|--------|
| 卡片背景（未选中） | `!bg-slate-800`（必须加 `!` 防止浏览器覆盖） |
| 卡片背景（选中） | `!bg-amber-500/10` |
| 卡片文字（未选中） | `text-slate-200`（禁止用 `text-white`） |
| 卡片文字（选中） | `text-amber-400` |
| 次要说明 | `text-slate-400` |
| 页面背景 | `bg-slate-900` |
| 主面板背景 | `bg-slate-800` |
| 输入框背景 | `bg-slate-700` |
| 主操作按钮 | `bg-amber-500 text-slate-900` |

---

## 关键技术决策记录

| 决策 | 选择 | 原因 |
|------|------|------|
| 前后端分离 | 是 | 移动端响应式需求，未来可能扩展 App |
| 角色数据建模 | 固定列+JSONB混合 | 固定属性用列（查询性能），职业特性等用JSONB |
| 规则集扩展 | ruleset表+FK | 新增规则集只加数据，不改代码 |
| 版本数据共享 | 方案C完全复制+source标记 | 查询简单，冗余可接受 |
| AI提供商 | 适配器模式+环境变量切换 | 用户自备Key，不锁定提供商 |
| 图片存储 | 对象存储（COS） | 不占服务器磁盘，CDN加速 |
| 全文搜索 | PostgreSQL tsvector | 无需额外组件，够用 |
| 认证方式 | JWT（djangorestframework-simplejwt） | 前后端分离标准方案 |
