# 部署会话修改记录与更新脚本设计说明

本文记录本次部署协助过程中对项目做出的修改，以及 `deploy/update.sh` 的设计思路。

## 一、部署目标

本次部署目标是让项目能在阿里云 ECS + 宝塔面板环境中运行，并支持后续从 GitHub 一键更新。

当前部署架构：

- 宝塔 Nginx 对外提供 HTTP 访问。
- 宝塔反向代理到本机 `127.0.0.1:8080`。
- `web` 容器运行前端静态页面，并把 `/api/` 请求转发给后端容器。
- `server` 容器运行 FastAPI 后端，监听 `127.0.0.1:8000`。
- `db` 容器运行 PostgreSQL，数据保存在 Docker volume `postgres_data`。

这样设计的重点是：公网只需要开放 `80` 和后续域名备案完成后的 `443`，数据库和后端端口不直接暴露给公网。

## 二、本次对项目做出的修改

### 1. 调整生产环境变量示例

修改文件：`.env.example`

改动内容：

- 将 `APP_ENV` 改为 `production`。
- 增加 `POSTGRES_PASSWORD`。
- 将 `DATABASE_URL` 从 SQLite 改为 PostgreSQL：

```env
DATABASE_URL=postgresql+psycopg://lixue:please-change-this-database-password@db:5432/lixue
```

- 将 `JWT_SECRET`、`ADMIN_PASSWORD` 改成明确要求替换的生产占位值。

原因：原来的 `.env.example` 使用 SQLite，而 `docker-compose.yml` 中已经有 PostgreSQL 容器。两者不一致会导致生产环境数据库行为混乱。

### 2. 调整 Docker Compose 生产部署配置

修改文件：`docker-compose.yml`

改动内容：

- PostgreSQL 密码改为从 `.env` 的 `POSTGRES_PASSWORD` 读取。
- 移除数据库公网端口映射，避免暴露 `5432`。
- 后端端口改为只绑定本机：

```yaml
ports:
  - "127.0.0.1:8000:8000"
```

- 前端端口改为只绑定本机：

```yaml
ports:
  - "127.0.0.1:8080:80"
```

- 给 `db`、`server`、`web` 增加 `restart: unless-stopped`。

原因：外部访问统一通过宝塔 Nginx，容器端口只给服务器本机访问，降低公网暴露面。

### 3. 增加 PostgreSQL Python 驱动

修改文件：`server/pyproject.toml`

新增依赖：

```toml
"psycopg[binary]>=3.2.0"
```

原因：后端使用 SQLAlchemy 连接 PostgreSQL 时需要 PostgreSQL 驱动。没有这个依赖，生产环境会无法连接 PostgreSQL。

### 4. 增加宝塔部署说明

新增文件：`docs/baota-deployment.md`

内容覆盖：

- 域名解析。
- 安全组端口。
- 上传项目。
- 创建 `.env`。
- 启动 Docker Compose。
- 宝塔创建站点。
- 宝塔反向代理。
- HTTPS 申请。
- 常见维护命令。

### 5. 增加 GitHub 更新部署说明

新增文件：`docs/git-update-deployment.md`

内容覆盖：

- 本地开发、测试、提交 GitHub 的流程。
- 第一次把服务器目录从手动上传模式切换成 GitHub clone 模式。
- 如何备份和恢复服务器 `.env`。
- 后续如何运行 `bash deploy/update.sh`。
- 常见检查命令。

### 6. 增加一键更新脚本

新增文件：`deploy/update.sh`

用途：在服务器上从 GitHub 拉取最新代码，重新构建 Docker 服务，并完成健康检查。

### 7. 增加 Git 忽略规则

新增文件：`.gitignore`

主要忽略：

- `.env`
- `web/node_modules/`
- `web/dist/`
- `.pytest_tmp/`
- `picture/`
- `docx_assets/`
- `*.tar`
- `*.xlsx`
- `*.docx`
- `员工.csv`

原因：避免把服务器密码、依赖目录、构建产物、截图、原始文档、员工数据等内容提交到 GitHub。

### 8. 增加部署配置测试

新增文件：

- `server/tests/test_config.py`
- `server/tests/test_deployment_config.py`
- `server/tests/test_update_script.py`

测试覆盖：

- 环境变量能覆盖默认数据库地址。
- 后端依赖包含 PostgreSQL 驱动。
- `.env.example` 使用 Docker Compose 中的 PostgreSQL 地址。
- 更新脚本保留 `.env`。
- 更新脚本使用 `git fetch origin` 和 `git pull --ff-only`。
- 更新脚本会执行 Docker 重建和前后端健康检查。
- 更新脚本会等待服务启动完成后再判定健康检查失败。
- 更新脚本包含失败回退逻辑。

## 三、`deploy/update.sh` 设计思路

### 1. 默认部署目录固定

脚本默认项目目录是：

```bash
/www/wwwroot/lixue-quiz
```

脚本内通过环境变量允许覆盖：

```bash
PROJECT_DIR="${PROJECT_DIR:-/www/wwwroot/lixue-quiz}"
```

这样普通使用时不需要传参数；如果以后测试或迁移目录，也可以临时指定 `PROJECT_DIR`。

### 2. 先检查关键前提

脚本会先检查：

- 当前目录是否存在。
- 当前目录是否是 Git 仓库。
- `.env` 是否存在。
- `git` 是否可用。
- `docker` 是否可用。
- `docker compose` 是否可用。
- 当前 Git 工作区是否干净。

原因：更新脚本不应该在环境不完整时继续执行，否则可能出现半更新状态。

### 3. 不自动生成或覆盖 `.env`

脚本只检查 `.env` 是否存在，不复制、不覆盖、不从 Git 恢复 `.env`。

原因：`.env` 保存服务器数据库密码、管理员密码、JWT 密钥等敏感配置。它应只存在于服务器本地，不应提交到 GitHub，也不应被更新脚本覆盖。

### 4. 使用快进更新

脚本执行：

```bash
git fetch origin
git pull --ff-only
```

`--ff-only` 表示只允许快进更新。如果服务器分支和 GitHub 分支发生分叉，脚本会停止。

原因：服务器不应该自动合并冲突，也不应该自动产生合并提交。生产服务器只负责拉取已经验证过的代码。

### 5. 更新前记录当前版本

脚本在更新前记录：

```bash
previous_revision=$(git rev-parse HEAD)
```

原因：如果后续 Docker 构建或健康检查失败，可以回退到更新前的代码版本。

### 6. Docker 重建和启动

脚本执行：

```bash
docker compose up -d --build
```

原因：不管是前端、后端还是依赖发生变化，都通过统一命令重建并启动服务。Docker Compose 会复用缓存，通常不会重复下载所有内容。

### 7. 后端健康检查

脚本会等待后端健康接口恢复，而不是在容器刚 `Started` 时立即判定失败。默认最多检查 30 次，每次间隔 2 秒。

脚本检查：

```bash
curl --fail --silent --show-error http://127.0.0.1:8000/api/health
```

后端正常时返回：

```json
{"status":"ok"}
```

### 8. 前端健康检查

脚本会等待前端页面恢复。默认最多检查 30 次，每次间隔 2 秒。

脚本检查：

```bash
curl --fail --silent --show-error --head http://127.0.0.1:8080
```

前端正常时应返回 HTTP 200。

### 9. 失败时回退

如果 Docker 构建失败，或前后端在重试等待后仍然检查失败，脚本会执行：

```bash
git reset --hard "$previous_revision"
docker compose up -d --build
```

然后再次检查前后端。

原因：更新失败时，服务器应尽量恢复到上一个可运行版本。

## 四、脚本不会做什么

`deploy/update.sh` 不会：

- 不会删除数据库 volume。
- 不会执行 `docker compose down -v`。
- 不会覆盖 `.env`。
- 不会自动解决 Git 冲突。
- 不会自动创建 GitHub 仓库。
- 不会自动配置 GitHub 私有仓库权限。
- 不会自动申请 HTTPS。

这些行为要么有数据风险，要么需要人工确认。

## 五、后续推荐流程

### 日常开发

```text
本地修改代码
本地运行测试和构建
git add / git commit
git push 到 GitHub
服务器执行 bash deploy/update.sh
```

### 服务器更新

```bash
cd /www/wwwroot/lixue-quiz
bash deploy/update.sh
```

### 更新后检查

```bash
docker compose ps
curl http://127.0.0.1:8000/api/health
curl -I http://127.0.0.1:8080
```

## 六、本次验证结果

本地已执行：

```bash
python -m pytest tests -q
```

结果：32 个测试通过。

本地已执行：

```bash
npm run build
```

结果：前端生产构建通过。

本地 Windows 环境没有 `bash` 命令，因此 `bash -n deploy/update.sh` 需要在服务器上执行：

```bash
cd /www/wwwroot/lixue-quiz
bash -n deploy/update.sh
```

如果没有输出，表示脚本语法检查通过。
