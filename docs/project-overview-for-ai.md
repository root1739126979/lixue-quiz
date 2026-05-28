# 砺学刷题平台 MVP 项目综述

本文面向后续接手的 AI 或工程师，目标是用一份文档说明项目背景、已实现功能、技术路径、实现方式、数据结构、接口、测试状态和后续注意事项。

## 1. 关键文档路径

项目规格、计划和使用说明都在仓库内：

- 当前推荐 Spec：`docs/superpowers/specs/2026-05-28-lixue-quiz-platform-mvp-v2.md`
- 早期设计备份：`docs/superpowers/specs/2026-05-28-lixue-quiz-platform-design.md`
- 实施计划书：`docs/superpowers/plans/2026-05-28-lixue-quiz-platform-mvp.md`
- 面向用户的使用说明：`docs/lixue-mvp-user-guide.md`
- 项目 README：`README.md`

## 2. 项目定位

项目名：砺学多题库刷题平台 MVP。

目标：为企业内部员工提供移动端刷题、错题巩固、模拟考试、积分排行和 AI 讲解能力；为管理员提供员工导入、题库导入、题目维护、积分规则、数据看板和 CSV 导出能力。

当前 MVP 重点是内测闭环：

- 管理员能创建题库并导入题目。
- 管理员能导入员工账号。
- 员工能登录、选择题库、练习答题、查看错题、参加模拟考试。
- 系统能记录答题、错题、积分、考试和导出基础数据。
- AI 讲解可按需启用，未配置或失败时不影响原始解析学习流程。

## 3. 当前已完成功能

### 3.1 后端已完成

后端位于 `server/`，使用 FastAPI + SQLAlchemy。

已实现能力：

- 健康检查：`GET /api/health`
- 员工登录：`POST /api/auth/login`
- 员工个人中心：`GET /api/me`
- 管理员登录：`POST /api/admin/auth/login`
- 后台接口统一 admin token 鉴权：`/api/admin/*` 除登录外均要求管理员 token
- 员工账号 CSV/XLSX 导入：`POST /api/admin/employees/import`
- 员工列表：`GET /api/admin/employees`
- 题库创建、列表、更新启停：`POST/GET/PATCH /api/admin/banks`
- 题目 CSV 导入：`POST /api/admin/banks/{bank_id}/questions/import`
- 题目列表、详情、编辑：`GET/PATCH /api/admin/questions`
- 员工可用题库列表：`GET /api/banks`
- 练习抽题：`POST /api/practice/sessions`
- 练习提交答案：`POST /api/practice/answers`
- 错题列表和标记掌握：`GET /api/wrong-questions`、`POST /api/wrong-questions/{question_id}/master`
- 全局排行榜和题库排行榜：`GET /api/rankings/global`、`GET /api/rankings/banks/{bank_id}`
- 模拟考试创建和交卷：`POST /api/exams/attempts`、`POST /api/exams/attempts/{attempt_id}/submit`
- AI 讲解接口：`POST /api/questions/{question_id}/ai-explanation`
- 积分规则读取和更新：`GET/PUT /api/admin/point-rules`
- LLM 配置读取和更新：`GET/PUT /api/admin/llm-config`
- 数据看板：`GET /api/admin/dashboard`
- CSV 导出：`GET /api/admin/exports/users`、`answers`、`exams`

### 3.2 前端已完成

前端位于 `web/`，使用 React + Vite + TypeScript + React Router + TanStack Query。

员工端页面：

- `/login`：员工登录
- `/banks`：题库选择
- `/practice/:bankId`：练习答题
- `/wrong`：错题库
- `/ranking`：排行榜
- `/exam/:bankId`：模拟考试
- `/profile`：个人中心

后台页面：

- `/admin/login`：管理员登录
- `/admin`：数据看板
- `/admin/employees`：员工管理和导入
- `/admin/banks`：题库管理
- `/admin/questions`：题目导入和列表
- `/admin/points`：积分规则
- `/admin/llm`：AI 讲解配置页面
- `/admin/exports`：CSV 导出

前端 API 基址在 `web/src/api/client.ts`：

- 默认 `API_BASE = "/api"`
- 可通过 `VITE_API_BASE` 覆盖
- token 存在 `localStorage.lixue_token`

### 3.3 部署文件已完成

- `docker-compose.yml`
- `server/Dockerfile`
- `web/Dockerfile`
- `web/nginx.conf`
- `deploy/nginx.conf`
- `.env.example`

## 4. 技术路径

### 4.1 后端技术栈

- Python 3.12+，当前环境也可在 Python 3.13 跑测试
- FastAPI
- SQLAlchemy 2
- Pydantic Settings
- SQLite 默认本地开发数据库：`sqlite+pysqlite:///./dev.db`
- PostgreSQL 作为生产推荐数据库，配置来自 `DATABASE_URL`
- `openpyxl` 用于员工 Excel 导入
- `httpx` 用于 OpenAI-compatible LLM 请求
- pytest 后端测试

注意：当前没有 Alembic migration 实现，应用启动时在 `create_app()` 内调用 `Base.metadata.create_all(engine)` 自动建表。

### 4.2 前端技术栈

- React 18
- Vite 5
- TypeScript
- React Router
- TanStack Query
- lucide-react 图标
- 原生 CSS：`web/src/styles.css`

### 4.3 安全实现

密码哈希：

- 文件：`server/app/security.py`
- 使用 Python 标准库 PBKDF2-HMAC-SHA256
- 格式：`pbkdf2_sha256$<salt>$<digest>`

Token：

- 自实现 HMAC-SHA256 JWT-like token
- payload 包含 `sub`、`role`、`exp`
- role 分为 `employee` 和 `admin`

后台鉴权：

- 文件：`server/app/main.py`
- middleware 拦截 `/api/admin/*`
- `/api/admin/auth/login` 不需要 token
- 其他后台接口必须携带 `Authorization: Bearer <token>` 且 role 为 `admin`

员工鉴权：

- `get_current_user()` 校验 token role 为 `employee`
- 同时校验用户存在且 `is_active=True`

## 5. 核心实现方式

### 5.1 题目导入

实现文件：

- `server/app/services/csv_importer.py`
- `server/app/routers/admin.py`

CSV 支持字段：

```text
题号,题型,题干,选项A,选项B,选项C,选项D,选项E,正确答案,正确答案文本,解析
```

题型映射：

- `单选题` -> `single`
- `多选题` -> `multiple`
- `判断题` -> `judgment`

导入规则：

- 题号、题型、题干、正确答案必填。
- 单选题只能有一个答案。
- 多选题答案会归一化为按字母排序的逗号格式，例如 `C，A,B` -> `A,B,C`。
- 正确答案必须出现在已有非空选项中。
- 错误行不会导致解析崩溃，会进入 `errors`。
- 同一题库内 `source_no` 重复会导致导入接口返回 400。

当前真实 CSV：

- 文件：`question/questions.csv`
- 总行数：169
- 可导入有效题：168
- 第 169 行缺少正确答案，会作为错误行报告

### 5.2 员工导入

实现文件：`server/app/routers/admin.py`

支持 CSV 和 XLSX。

字段：

```text
姓名,工号,手机号,部门,状态,初始密码
```

规则：

- 姓名必填。
- 工号或手机号至少一个必填。
- 同一上传文件内工号、手机号重复会返回 400。
- 已存在用户会更新姓名、工号、手机号、部门、状态。
- 只有上传行提供 `初始密码` 时才覆盖已有密码。
- 未提供初始密码时使用 `123456`。

### 5.3 答题与积分

实现文件：

- `server/app/routers/practice.py`
- `server/app/services/scoring.py`

练习抽题：

- 从启用题库中随机抽取启用题目。
- 最多返回 50 题。
- 不返回正确答案。

答题提交：

- 对答案做归一化。
- 与题目正确答案比较。
- 写入 `answer_records`。
- 按积分规则写入 `point_transactions`。
- 根据正确/错误更新 `wrong_questions`。

积分规则：

- `answer_base_points`
- `correct_bonus_points`
- `wrong_retry_correct_points` 当前模型有字段，但练习逻辑尚未单独使用该字段
- `exam_complete_points`
- `daily_point_limit`

每日积分上限：

- `award_points_with_daily_limit()` 按用户当天已得积分计算剩余额度。
- 超过每日上限时只发放剩余额度或 0 分。

### 5.4 错题状态

实现文件：

- `server/app/routers/practice.py`
- `server/app/routers/wrong_questions.py`

规则：

- 同一用户同一题只有一条错题记录。
- 答错时：
  - 若不存在错题记录，创建 `open`。
  - 若已存在，状态重置为 `open`，错误次数加 1。
- 答对时：
  - 若存在 `open` 错题，标记为 `mastered`。
  - 若不存在错题，返回 `none`。
- 员工可手动调用 `POST /api/wrong-questions/{question_id}/master` 标记掌握。

### 5.5 排行榜

实现文件：`server/app/routers/rankings.py`

当前排序：

- 基于 `point_transactions` 聚合用户积分。
- 全局榜不筛题库。
- 题库榜按 `bank_id` 筛选。
- 当前 SQL 排序主要按积分降序、用户 ID 升序。

注意：Spec 中还定义了同分按正确率、答题数、最近得分时间等更细排序，当前实现返回了 `accuracy`、`answer_count`、`last_scored_at` 字段，但排序尚未完整使用这些 tie-breaker。

### 5.6 模拟考试

实现文件：`server/app/routers/exams.py`

流程：

1. 员工调用 `POST /api/exams/attempts`。
2. 系统按题库 `exam_question_count` 随机抽题。
3. 创建 `exam_attempts`。
4. 将本次题目快照写入 `exam_attempt_questions`。
5. 员工调用 `POST /api/exams/attempts/{attempt_id}/submit` 交卷。
6. 系统按快照中的正确答案判分，写入 `exam_answers`。
7. 写入考试得分、正确数、提交时间。
8. 按 `exam_complete_points` 发放考试完成积分。

考试约束：

- 题库必须启用。
- 没有题目时返回 400。
- 每次考试只能提交一次。
- 服务端按开始时间 + 限时判断是否超时。

### 5.7 AI 讲解

实现文件：

- `server/app/routers/practice.py`
- `server/app/services/llm.py`

启用条件：

- 数据库 `llm_configs` 有启用配置，或环境变量配置：
  - `LLM_ENABLED=true`
  - `LLM_BASE_URL`
  - `LLM_API_KEY`
  - `LLM_MODEL`

调用方式：

- 构建中文讲解 prompt。
- 调用 OpenAI-compatible `/chat/completions`。
- 成功后写入 `ai_explanations`。
- 失败写入 `llm_request_logs` 并返回 502。
- 未启用返回 409：`AI讲解未启用`。

缓存键：

- `question_id`
- `question_updated_at`
- `model`
- `prompt_version`

安全注意：

- 当前 `api_key_encrypted` 字段名称为 encrypted，但实现中只是明文保存；生产环境需改为环境变量或真实加密存储。

### 5.8 数据导出

实现文件：

- `server/app/services/exports.py`
- `server/app/routers/admin.py`

导出格式：

- UTF-8 BOM CSV
- 使用 `text/csv; charset=utf-8`

导出内容：

- 用户学习汇总：姓名、工号、手机号、部门、累计答题数
- 答题记录：用户 ID、题库 ID、题目 ID、选择答案、是否正确、积分
- 考试成绩：用户 ID、题库 ID、题数、分数、正确数、提交时间

## 6. 数据结构

核心模型在 `server/app/models.py`。

### 6.1 用户与权限

`users`

- `id`
- `name`
- `work_no`
- `phone`
- `department`
- `password_hash`
- `feishu_user_id`
- `is_active`
- `created_at`
- `updated_at`

`admins`

- `id`
- `username`
- `password_hash`
- `created_at`

### 6.2 题库与题目

`question_banks`

- `id`
- `name`
- `description`
- `is_active`
- `exam_question_count`
- `exam_time_limit_minutes`
- `created_at`
- `updated_at`

`questions`

- `id`
- `bank_id`
- `source_no`
- `question_type`
- `stem`
- `correct_answer`
- `correct_answer_text`
- `explanation`
- `module`
- `difficulty`
- `is_active`
- `created_at`
- `updated_at`

约束：

- `bank_id + source_no` 唯一

`question_options`

- `id`
- `question_id`
- `label`
- `content`

约束：

- `question_id + label` 唯一

### 6.3 导入

`import_batches`

- `id`
- `import_type`
- `total_rows`
- `imported_count`
- `error_count`
- `created_at`

### 6.4 答题、错题与积分

`answer_records`

- `id`
- `user_id`
- `bank_id`
- `question_id`
- `selected_answer`
- `is_correct`
- `source`
- `points_awarded`
- `created_at`

`wrong_questions`

- `id`
- `user_id`
- `bank_id`
- `question_id`
- `status`
- `wrong_count`
- `last_wrong_at`
- `mastered_at`

约束：

- `user_id + question_id` 唯一

`point_rules`

- `id`
- `answer_base_points`
- `correct_bonus_points`
- `wrong_retry_correct_points`
- `exam_complete_points`
- `daily_point_limit`

`point_transactions`

- `id`
- `user_id`
- `bank_id`
- `points`
- `reason`
- `created_at`

### 6.5 考试

`exam_attempts`

- `id`
- `user_id`
- `bank_id`
- `question_count`
- `time_limit_minutes`
- `score`
- `correct_count`
- `submitted_at`
- `created_at`

`exam_attempt_questions`

- `id`
- `attempt_id`
- `question_id`
- `source_no`
- `question_type`
- `stem`
- `options_json`
- `correct_answer`
- `correct_answer_text`
- `explanation`

约束：

- `attempt_id + question_id` 唯一

`exam_answers`

- `id`
- `attempt_id`
- `question_id`
- `selected_answer`
- `is_correct`

### 6.6 AI 讲解

`ai_explanations`

- `id`
- `question_id`
- `question_updated_at`
- `model`
- `prompt_version`
- `content`
- `created_at`

约束：

- `question_id + question_updated_at + model + prompt_version` 唯一

`llm_request_logs`

- `id`
- `question_id`
- `status`
- `latency_ms`
- `error_message`
- `estimated_cost`
- `created_at`

`llm_configs`

- `id`
- `enabled`
- `base_url`
- `api_key_encrypted`
- `model`
- `prompt_version`

### 6.7 审计

`audit_logs`

- `id`
- `actor_type`
- `action`
- `detail`
- `created_at`

注意：模型已定义，但当前业务路由没有系统性写入审计日志。

## 7. API 总览

### 7.1 公共与员工接口

- `GET /api/health`
- `POST /api/auth/login`
- `GET /api/me`
- `GET /api/banks`
- `GET /api/banks/{bank_id}/summary`
- `POST /api/practice/sessions`
- `POST /api/practice/answers`
- `GET /api/wrong-questions`
- `POST /api/wrong-questions/{question_id}/master`
- `GET /api/rankings/global`
- `GET /api/rankings/banks/{bank_id}`
- `POST /api/exams/attempts`
- `POST /api/exams/attempts/{attempt_id}/submit`
- `POST /api/questions/{question_id}/ai-explanation`

### 7.2 管理后台接口

- `POST /api/admin/auth/login`
- `POST /api/admin/employees/import`
- `GET /api/admin/employees`
- `POST /api/admin/banks`
- `GET /api/admin/banks`
- `PATCH /api/admin/banks/{bank_id}`
- `POST /api/admin/banks/{bank_id}/questions/import`
- `GET /api/admin/questions`
- `GET /api/admin/questions/{question_id}`
- `PATCH /api/admin/questions/{question_id}`
- `GET /api/admin/dashboard`
- `GET /api/admin/exports/users`
- `GET /api/admin/exports/answers`
- `GET /api/admin/exports/exams`
- `GET /api/admin/point-rules`
- `PUT /api/admin/point-rules`
- `GET /api/admin/llm-config`
- `PUT /api/admin/llm-config`

## 8. 前端结构

```text
web/src/
├── App.tsx
├── main.tsx
├── styles.css
├── api/
│   ├── client.ts
│   └── types.ts
├── employee/
│   ├── LoginPage.tsx
│   ├── EmployeeLayout.tsx
│   ├── BankSelectPage.tsx
│   ├── PracticePage.tsx
│   ├── WrongQuestionsPage.tsx
│   ├── RankingPage.tsx
│   ├── ExamPage.tsx
│   └── ProfilePage.tsx
└── admin/
    ├── AdminLoginPage.tsx
    ├── AdminLayout.tsx
    ├── DashboardPage.tsx
    ├── EmployeesPage.tsx
    ├── QuestionBanksPage.tsx
    ├── QuestionsPage.tsx
    ├── PointRulesPage.tsx
    ├── LlmConfigPage.tsx
    └── ExportsPage.tsx
```

前端状态管理很轻：

- TanStack Query 用于请求、缓存和刷新。
- 登录 token 存到 `localStorage.lixue_token`。
- 员工和管理员共用同一个 token key，因此同一浏览器同时切换员工/管理员时可能互相覆盖。

## 9. 后端结构

```text
server/app/
├── main.py
├── config.py
├── database.py
├── security.py
├── models.py
├── routers/
│   ├── admin.py
│   ├── auth.py
│   ├── banks.py
│   ├── practice.py
│   ├── wrong_questions.py
│   ├── rankings.py
│   └── exams.py
└── services/
    ├── csv_importer.py
    ├── scoring.py
    ├── llm.py
    ├── dashboard.py
    └── exports.py
```

## 10. 启动与部署

### 10.1 本地后端

```powershell
cd server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 10.2 本地前端

```powershell
cd web
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

### 10.3 Docker 部署

```powershell
copy .env.example .env
docker compose up -d --build
```

生产前必须修改：

- `JWT_SECRET`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- PostgreSQL 密码和连接串
- LLM 配置，如需启用 AI 讲解

## 11. 测试与验证

后端测试：

```powershell
cd server
python -m pytest tests -q
```

当前测试覆盖：

- 健康检查
- 密码哈希和 token
- CSV 题目导入
- SQLAlchemy 模型建表
- 员工导入和登录
- 题库和题目导入 API
- 练习答题、判分和反馈
- 错题生命周期
- 排行榜契约和积分规则
- 模拟考试创建、快照和判分
- LLM prompt 和未启用降级
- CSV 导出

前端构建：

```powershell
cd web
npm run build
```

最近一次验证状态：

- 后端：`23 passed`
- 前端：Vite build 成功

## 12. 当前已知限制与后续改进点

1. 没有 Alembic migration，当前用 `Base.metadata.create_all()` 自动建表。
2. 默认本地 SQLite 可用，生产推荐 PostgreSQL，但尚未验证完整生产迁移流程。
3. `llm_configs.api_key_encrypted` 当前实际是明文保存，生产需改为环境变量或加密存储。
4. `audit_logs` 模型已定义，但后台关键操作尚未系统性写入审计日志。
5. 排行榜排序尚未完整实现 Spec 的同分 tie-breaker。
6. `wrong_retry_correct_points` 字段存在，但练习答题逻辑尚未单独使用错题重做积分。
7. 员工和管理员前端共用 `localStorage.lixue_token`，同浏览器切换身份会覆盖 token。
8. 前端 AI 配置页目前是静态表单，尚未接入 `GET/PUT /api/admin/llm-config`。
9. 题目维护页目前主要支持列表和导入，编辑/停用 UI 还比较基础。
10. 当前使用 `datetime.utcnow()`，Python 3.13 测试会出现弃用警告，后续可改为 timezone-aware UTC。
11. Docker Compose 包含 PostgreSQL，但后端默认 `.env.example` 需要按部署环境确认 `DATABASE_URL`。

## 13. 给后续 AI 的工作建议

接手时先读：

1. `docs/superpowers/specs/2026-05-28-lixue-quiz-platform-mvp-v2.md`
2. `docs/superpowers/plans/2026-05-28-lixue-quiz-platform-mvp.md`
3. `docs/project-overview-for-ai.md`
4. `server/app/models.py`
5. `server/app/main.py`
6. `web/src/App.tsx`

修改后必须至少运行：

```powershell
cd server
python -m pytest tests -q

cd ../web
npm run build
```

若新增业务能力，优先补后端测试，再改实现。不要只改前端假数据；当前 MVP 已经有可用后端路径，新增页面应尽量接真实 API。
