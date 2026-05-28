# 砺学刷题平台 MVP 使用说明

本文面向试用人员、管理员和部署人员，说明如何启动、初始化和使用当前 MVP。

## 1. 启动系统

### 1.1 启动后端

```powershell
cd server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

后端健康检查地址：

```text
http://127.0.0.1:8000/api/health
```

默认本地数据库为 `server/dev.db`。生产部署建议使用 `.env` 配置 PostgreSQL。

### 1.2 启动前端

```powershell
cd web
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

前端访问地址：

```text
http://127.0.0.1:5173
```

## 2. 管理员首次初始化

后台入口：

```text
http://127.0.0.1:5173/admin/login
```

默认管理员账号：

```text
账号：admin
密码：admin123456
```

生产环境必须在 `.env` 中修改 `ADMIN_USERNAME`、`ADMIN_PASSWORD` 和 `JWT_SECRET`。

## 3. 管理后台使用流程

### 3.1 导入员工

进入“员工管理”，上传 CSV 或 Excel 文件。

CSV 表头示例：

```csv
姓名,工号,手机号,部门,状态,初始密码
张三,E001,13800000001,装备部,启用,123456
李四,E002,13800000002,生产部,启用,123456
```

规则：

- `姓名` 必填。
- `工号` 或 `手机号` 至少填写一个。
- 同一个文件内工号、手机号不能重复。
- 未填写 `初始密码` 时默认使用 `123456`。
- `状态` 填“停用”时，该员工不能登录。

### 3.2 创建题库

进入“题库管理”，填写题库名称和说明后创建题库。

题库可启用或停用：

- 启用题库会展示给员工。
- 停用题库不会展示给员工，但历史答题记录仍保留。

### 3.3 导入题目

进入“题目维护”，选择题库后上传 `question/questions.csv`。

当前题目 CSV 表头：

```csv
题号,题型,题干,选项A,选项B,选项C,选项D,选项E,正确答案,正确答案文本,解析
```

支持题型：

- `单选题`
- `多选题`
- `判断题`

注意：当前 `question/questions.csv` 第 169 行缺少正确答案，系统会报告 1 条错误并导入 168 条有效题目。这是预期行为，不是导入崩溃。

### 3.4 配置积分规则

进入“积分规则”，可配置：

- 答题基础分。
- 答对额外分。
- 错题重做答对分。
- 完成考试分。
- 每日积分上限。

规则变更只影响后续答题和考试，不回算历史积分。

### 3.5 查看数据看板

进入“数据看板”，可查看：

- 参与人数。
- 活跃人数。
- 累计答题数。
- 整体正确率。
- 未掌握错题数。

### 3.6 导出数据

进入“数据导出”，可下载：

- 用户学习汇总。
- 答题记录。
- 考试成绩。

导出格式为 UTF-8 BOM CSV，适合用 Excel 打开。

### 3.7 AI 讲解配置

MVP 后端支持 OpenAI-compatible AI 讲解接口。未配置或停用时，员工端会保留原始解析，AI 讲解请求会提示“AI讲解未启用”。

需要启用时，应配置：

- `LLM_ENABLED=true`
- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`

## 4. 员工端使用流程

员工入口：

```text
http://127.0.0.1:5173/login
```

员工使用管理员导入的工号或手机号登录。

### 4.1 选择题库

登录后进入“题库”页，可查看：

- 题库名称。
- 题目数量。
- 已练习数量。
- 正确率。
- 个人积分。

### 4.2 练习答题

点击“开始练习”进入随机练习。

答题提交后会显示：

- 是否正确。
- 正确答案。
- 正确答案文本。
- CSV 原始解析。
- 本次获得积分。
- 错题状态。

多选题答案会按字母排序归一化，例如 `B,A,C` 会按 `A,B,C` 判分。

### 4.3 错题库

答错的题会进入“错题”页。

员工可以查看：

- 所属题库。
- 题干。
- 正确答案。
- 原始解析。
- 错误次数。

点击“标记掌握”后，该题会从未掌握错题列表中移除。

### 4.4 排行榜

进入“排行”页查看：

- 全局榜。
- 题库榜。

当前排序优先按积分降序。

### 4.5 模拟考试

在题库页点击“模拟考试”开始考试。

考试规则：

- 系统按题库考试配置随机抽题。
- 开始考试时会保存题目快照。
- 提交后显示得分、答对数和总题数。
- 每次考试只能提交一次。

### 4.6 个人中心

进入“我的”页查看：

- 姓名。
- 部门。
- 总积分。
- 累计答题数。
- 正确率。
- 未掌握错题数。

## 5. 常见问题

### 5.1 员工无法登录

检查：

- 是否已在后台导入该员工。
- 工号或手机号是否正确。
- 初始密码是否正确。
- 员工状态是否为启用。

### 5.2 题目导入数量不是 169

当前 CSV 第 169 行缺少正确答案，因此 MVP 会导入 168 条有效题目并报告 1 条错误。补齐该行答案后可重新导入。

### 5.3 AI 讲解不可用

检查：

- LLM 是否启用。
- `base_url`、`api_key`、`model` 是否配置。
- OpenAI-compatible 服务是否可访问。

AI 失败不会影响答题，员工仍可查看 CSV 原始解析。

### 5.4 前端接口请求失败

检查：

- 后端是否运行在 `http://127.0.0.1:8000`。
- 前端是否通过 `npm run dev` 启动。
- 登录 token 是否过期或被员工/管理员账号互相覆盖。

## 6. 生产部署与 GitHub 更新流程

生产环境推荐使用：

```text
GitHub 仓库 -> 宝塔服务器 git pull -> Docker Compose 重建 -> 健康检查
```

首次部署前，先在本地初始化 Git 仓库并推送到 GitHub。

### 6.1 本地推送到 GitHub

本项目已经配置 `.gitignore`，会忽略 `.env`、`web/node_modules/`、`web/dist/`、截图、压缩包、Excel/Word 原始文件和员工数据文件。

首次提交示例：

```powershell
git status
git add .
git commit -m "chore: initial project setup"
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

注意：

- 不要把 `.env` 提交到 GitHub。
- 不要把员工名单、截图、宝塔截图、服务器密码文件提交到 GitHub。
- 如果 GitHub 仓库是私有仓库，服务器需要额外配置访问权限。

### 6.2 宝塔服务器第一次切换为 Git 仓库

如果服务器 `/www/wwwroot/lixue-quiz` 目前是手动上传的文件，先备份服务器 `.env`：

```bash
cd /www/wwwroot/lixue-quiz
cp .env /root/lixue-quiz.env.backup
```

备份当前手动上传目录：

```bash
cd /www/wwwroot
mv lixue-quiz lixue-quiz-manual-backup
```

从 GitHub 克隆项目：

```bash
cd /www/wwwroot
git clone https://github.com/你的用户名/你的仓库名.git lixue-quiz
```

恢复服务器 `.env`：

```bash
cp /root/lixue-quiz.env.backup /www/wwwroot/lixue-quiz/.env
```

检查脚本语法：

```bash
cd /www/wwwroot/lixue-quiz
bash -n deploy/update.sh
```

没有输出表示语法正常。

执行首次 Git 模式部署：

```bash
bash deploy/update.sh
```

### 6.3 后续日常更新

以后每次更新：

1. 本地修改代码。
2. 本地运行测试和构建。
3. 提交并推送到 GitHub。
4. 登录宝塔终端。
5. 执行：

```bash
cd /www/wwwroot/lixue-quiz
bash deploy/update.sh
```

脚本会自动：

- 检查 `.env` 是否存在。
- 检查 Git、Docker、Docker Compose。
- 拉取 GitHub 最新代码。
- 执行 `docker compose up -d --build`。
- 检查后端 `http://127.0.0.1:8000/api/health`。
- 检查前端 `http://127.0.0.1:8080`。
- 如果构建或检查失败，回退到更新前版本。

### 6.4 生产部署后建议流程

1. 使用 IP 或已备案域名配置宝塔反向代理到 `http://127.0.0.1:8080`。
2. 域名备案完成后配置 HTTPS。
3. 修改 `.env` 中的管理员密码、数据库密码和 JWT secret。
4. 登录后台。
5. 导入员工。
6. 创建题库。
7. 导入题目 CSV。
8. 让员工从 `/login` 开始内测。
