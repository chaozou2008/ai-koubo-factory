# AI口播工厂 — 产品设计文档

> 版本: v1.0 | 日期: 2026-06-13 | 状态: 待评审

---

## 1. 产品概述

### 1.1 一句话定位

面向国内小商家的AI数字人口播视频生成SaaS平台，让每个商家都能拥有自己的虚拟形象IP。

### 1.2 来源背景

基于两位创业者的对话需求分析：

- **人物A（技术方）**：10年+游戏开发，刚被裁员，正在开发"口播数字人"软件，技术能力强
- **人物B（商业方）**：9年SaaS创业经验，上海10人团队，5000+小微企业客户，电话销售获客，传统SaaS正寻求AI转型

### 1.3 核心价值主张

| 对比维度 | 用户自己做（即梦等） | AI口播工厂 |
|----------|:---:|:---:|
| 角色连续性 | ❌ 每次生成人物不同 | ✅ 永久锁定同一形象 |
| 操作门槛 | 高（需要会写Prompt） | 低（选模板+输入文案） |
| 版权合规 | 模糊 | ✅ 真人扫码授权 |
| 适用场景 | 个人娱乐 | 商家短视频推广获客 |
| 付费方式 | 按次 | 月付，成本可预期 |

---

## 2. 市场定位

### 2.1 目标用户

- 美容店、服装店、瓷砖店等实体小商家
- 果农等农产品推广者
- 需要短视频为生意引流的小微企业主
- **首期行业**：美容美发（模板先行）

### 2.2 差异化

```
小云雀（竞品）  →  短剧市场（红果短剧等平台）
AI口播工厂      →  小商家短视频推广（抖音/视频号）
```

### 2.3 商业模式

- **会员订阅制**：月付套餐（基础版/专业版/企业版）
- **算粒体系**：会员月赠固定算粒 + 可额外购买
- **计费参考**：
  - 腾讯云MAIS：建音色25元 + 0.5元/分钟配音
  - Seedance 2.0 API：$0.08-$0.55/秒视频生成
  - 目标毛利：单价覆盖API成本5-10倍

---

## 3. 核心功能（MVP）

### 3.1 MVP功能范围

| 功能 | 描述 | 优先级 |
|------|------|:--:|
| 用户注册登录 | 手机号注册/登录 | P0 |
| 数字人形象创建 | 上传照片→扫码授权→生成锚定形象 | P0 |
| 行业模板选择 | 首期美容行业模板 | P0 |
| 文案→口播视频 | 输入文案→TTS合成→视频生成 | P0 |
| 视频管理 | 列表查看、下载、删除 | P0 |
| 会员订阅 | 选择套餐、月付 | P0 |
| 算粒管理 | 余额查询、流水记录 | P0 |

### 3.2 不在MVP的功能

- 多行业模板（后续迭代）
- 团队协作/子账号
- API对外开放
- 数据统计看板
- 自定义模板编辑器

---

## 4. 技术架构

### 4.1 技术栈

| 层 | 选型 | 理由 |
|----|------|------|
| 前端 | Vue 3 + Element Plus + Vite | 国内SaaS后台首选，组件库成熟 |
| 后端 | Python + FastAPI | 异步性能好，AI生态强 |
| 数据库 | PostgreSQL | 关系型数据，ACID保障 |
| 缓存 | Redis | 会话+任务队列 |
| 存储 | 阿里云OSS / 腾讯云COS | 视频/图片文件存储 |
| 任务队列 | Celery + Redis | 异步视频生成任务 |
| 视频生成 | Seedance 2.0 API（火山引擎） | 角色一致性业界最佳 |
| 声音/TTS | 腾讯云MAIS | 25元建音色+0.5元/分钟 |

### 4.2 架构图

```
┌──────────────────────────────────────┐
│         Vue 3 + Element Plus          │
│  模板选择 / 文案编辑 / 形象管理 / 下载  │
└──────────────────┬───────────────────┘
                   │ REST API
┌──────────────────▼───────────────────┐
│           Python / FastAPI            │
│                                       │
│  ┌─────────┐ ┌─────────┐ ┌───────────┐ │
│  │ 用户模块 │ │会员计费  │ │ 任务队列   │ │
│  │ 模板管理 │ │数字人模块│ │(Celery)   │ │
│  └─────────┘ └──────┘ └─────┬─────┘ │
│                              │        │
│  ┌───────────────────────────▼──────┐ │
│  │          API 编排调度层           │ │
│  │                                   │ │
│  │  视频生成              TTS        │ │
│  │  (Seedance 2.0)    (腾讯云MAIS)   │ │
│  └──────────────────────────────────┘ │
└──────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────┐
│      PostgreSQL + Redis + OSS/COS    │
└──────────────────────────────────────┘
```

### 4.3 后端模块划分

| 模块 | 职责 |
|------|------|
| 用户模块 | 注册/登录/个人信息 |
| 数字人模块 | 形象创建/授权二维码/素材库管理 |
| 模板模块 | 行业模板CRUD/预览 |
| 视频生成模块 | 文案→TTS→视频生成全链路编排 |
| 会员+计费模块 | 套餐管理/算粒扣减/订单记录 |
| 任务调度模块 | Celery异步任务/状态追踪/失败重试 |
| API编排模块 | 第三方API统一抽象/供应商切换/成本路由 |

---

## 5. 核心流程

### 5.1 用户创建数字人

```
① 用户上传3-5张照片 → ② 后端生成火山引擎授权二维码
    → ③ 真人扫码→实名认证→授权
    → ④ 素材进入私域素材库（通过一致性校验）
    → ⑤ 形象入库，标记为可用
```

### 5.2 生成口播视频

```
① 选择数字人形象 → ② 选择行业模板 → ③ 输入口播文案
    → ④ 点击"生成" → ⑤ 系统扣减算粒
    → ⑥ 异步任务启动：
        a. 调用腾讯云MAIS TTS → 生成音频文件
        b. 调用Seedance 2.0 API → 传入锚定形象+音频+模板参数
        c. 视频生成完成 → 上传OSS → 更新任务状态
    → ⑦ 前端轮询获知完成 → 用户可预览/下载
    → ⚠️ 若生成失败：自动退还已扣算粒，记录退款流水
```

### 5.3 角色一致性保证

| 层级 | 手段 | 实现 |
|:--:|------|------|
| 第一层 | Seedance私域素材库 | 已授权素材永久复用，人物特征不变 |
| 第二层 | 角色ID | 同一形象绑定唯一角色标识 |
| 第三层 | 模板参数固定 | 同形象+同模板参数=一致输出 |

---

## 6. 数据模型

### 6.1 核心表结构

```sql
-- 用户表
users (
    id UUID PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    company_name VARCHAR(100),
    industry VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
)

-- 数字人形象表
avatars (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(50) NOT NULL,
    photo_urls JSONB,              -- 用户上传原图
    material_id VARCHAR(100),      -- 火山引擎私域素材库ID
    character_id VARCHAR(50),      -- 角色唯一标识
    status VARCHAR(20) DEFAULT 'pending',  -- pending/authorized/active/failed
    created_at TIMESTAMP DEFAULT NOW()
)

-- 行业模板表
templates (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    industry VARCHAR(50) NOT NULL,
    thumbnail_url VARCHAR(500),
    preview_video_url VARCHAR(500),
    config JSONB,                  -- 画面参数配置
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
)

-- 视频任务表
video_tasks (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    avatar_id UUID REFERENCES avatars(id),
    template_id UUID REFERENCES templates(id),
    script_text TEXT NOT NULL,
    tts_audio_url VARCHAR(500),
    video_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'queued',
        -- queued/processing/tts_done/video_generating/done/failed
    cost_credits INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
)

-- 会员套餐表
plans (
    id UUID PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    monthly_price DECIMAL(10,2) NOT NULL,
    credits_per_month INTEGER NOT NULL,
    features JSONB,
    status VARCHAR(20) DEFAULT 'active'
)

-- 用户订阅表
subscriptions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    plan_id UUID REFERENCES plans(id),
    started_at TIMESTAMP DEFAULT NOW(),
    expired_at TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'active'
)

-- 算粒流水表
credit_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    amount INTEGER NOT NULL,       -- 正=充值，负=消耗
    balance INTEGER NOT NULL,      -- 变动后余额
    type VARCHAR(20) NOT NULL,     -- charge/consume/refund
    source VARCHAR(100),           -- 来源描述
    created_at TIMESTAMP DEFAULT NOW()
)
```

### 6.2 表关系

```
user ──1:N──→ avatar ──1:N──→ video_task
user ──1:1──→ subscription ──N:1──→ plan
user ──1:N──→ credit_log
video_task ──N:1──→ template
```

---

## 7. API接口设计

### 7.1 接口列表

```
POST   /api/auth/login              # 登录
POST   /api/auth/register           # 注册

GET    /api/avatars                  # 我的形象列表
POST   /api/avatars                  # 创建形象（上传照片）
GET    /api/avatars/:id              # 形象详情
DELETE /api/avatars/:id              # 删除形象

GET    /api/templates                # 可用模板列表（按行业筛选）
GET    /api/templates/:id            # 模板详情+预览

POST   /api/videos                   # 提交生成任务
GET    /api/videos                   # 我的视频列表
GET    /api/videos/:id               # 视频详情（含状态和下载链接）
DELETE /api/videos/:id               # 删除视频

GET    /api/plans                    # 套餐列表
POST   /api/subscribe                # 订阅/续费

GET    /api/credits/balance          # 剩余算粒
GET    /api/credits/log              # 算粒流水

POST   /api/webhooks/video-callback  # Seedance回调（内部）
```

### 7.2 视频生成接口详例

**请求：**
```
POST /api/videos
{
    "avatar_id": "uuid",
    "template_id": "uuid",
    "script_text": "大家好，我是XX美容的专属顾问，今天给大家推荐..."
}
```

**响应：**
```json
{
    "task_id": "uuid",
    "status": "queued",
    "estimated_seconds": 120,
    "cost_credits": 10
}
```

---

## 8. MVP开发排期预估

| 阶段 | 内容 | 工作量（人天） |
|------|------|:--:|
| 项目初始化 | 前后端脚手架、数据库搭建、CI/CD | 3 |
| 用户模块 | 注册登录、JWT鉴权 | 3 |
| 数字人模块 | 上传→授权二维码→素材库对接 | 5 |
| 模板模块 | 模板CRUD、预览 | 3 |
| 视频生成核心 | TTS对接、Seedance对接、Celery编排 | 8 |
| 会员+算粒 | 套餐/订阅/计费扣减 | 4 |
| 视频管理 | 列表/详情/下载 | 2 |
| 前端界面 | 所有页面的Vue组件开发 | 8 |
| 联调测试 | 端到端测试、bug修复 | 5 |
| **合计** | | **~41人天** |

---

## 9. 风险与依赖

| 风险 | 影响 | 应对 |
|------|------|------|
| Seedance 2.0 API延迟/不稳定 | 视频生成耗时长 | 异步任务+失败重试+状态通知 |
| Seedance定价变动 | 成本不可控 | 算粒定价留足缓冲空间 |
| 真人授权流程用户流失 | 转化率低 | 优化引导流程，降低认知门槛 |
| 腾讯云MAIS服务中断 | 无法合成语音 | 接入火山引擎TTS作为备选 |
| 抖音/平台对AI内容限流 | 产品价值打折 | 持续关注平台政策，提供"真人辅助"模式 |

---

## 10. 后续迭代方向

- **V1.1**：3-5个行业模板（服装、餐饮、建材、农产品）
- **V1.2**：视频编辑器（字幕样式、背景音乐、片头片尾）
- **V2.0**：自定义模板编辑器、团队协作、数据看板
- **V3.0**：API对外开放、渠道分销体系
