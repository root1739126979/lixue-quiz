# GitHub 一键更新部署说明

这份说明用于把服务器部署方式切换成 GitHub 更新模式。完成后，日常更新只需要：

当前项目 GitHub 仓库地址：

```text
https://github.com/root1739126979/lixue-quiz
```

```bash
cd /www/wwwroot/lixue-quiz
bash deploy/update.sh
```

## 一、本地更新流程

以后每次改代码：

1. 在本地完成代码修改。
2. 本地运行测试和构建。
3. 提交到 GitHub。
4. 登录宝塔终端，在服务器执行：

```bash
cd /www/wwwroot/lixue-quiz
bash deploy/update.sh
```

脚本会自动拉取 GitHub 最新代码、重新构建 Docker 服务，并检查前端和后端是否正常。

## 二、第一次切换到 GitHub 模式

服务器当前目录如果是手动上传的文件，通常不是 Git 仓库。第一次需要重新用 GitHub 仓库建立目录。

先把服务器上的 `.env` 备份出来：

```bash
cd /www/wwwroot/lixue-quiz
cp .env /root/lixue-quiz.env.backup
```

再备份当前项目目录：

```bash
cd /www/wwwroot
mv lixue-quiz lixue-quiz-manual-backup
```

然后从 GitHub 克隆项目：

```bash
cd /www/wwwroot
git clone https://github.com/root1739126979/lixue-quiz.git lixue-quiz
```

恢复服务器配置文件：

```bash
cp /root/lixue-quiz.env.backup /www/wwwroot/lixue-quiz/.env
```

进入项目并启动：

```bash
cd /www/wwwroot/lixue-quiz
bash deploy/update.sh
```

## 三、脚本会做什么

`deploy/update.sh` 会执行：

1. 检查当前目录是否是 Git 仓库。
2. 检查 `.env` 是否存在。
3. 检查 Git、Docker、Docker Compose 是否可用。
4. 确认当前分支没有未提交的本地修改。
5. 记录当前 Git 版本。
6. 执行 `git fetch origin`。
7. 执行 `git pull --ff-only`。
8. 执行 `docker compose up -d --build`。
9. 检查后端健康接口。
10. 检查前端页面。
11. 如果构建或检查失败，自动回退到更新前的 Git 版本并重启旧版本。

## 四、注意事项

- 不要把 `.env` 提交到 GitHub。
- 不要执行 `docker compose down -v`，这会删除数据库数据。
- 如果 GitHub 仓库是私有仓库，服务器需要配置 GitHub 访问权限。
- 推荐先使用公开仓库或配置 SSH key 后再使用私有仓库。
- 如果 `git pull --ff-only` 失败，说明服务器上的分支和 GitHub 分支发生分叉，需要人工处理。

## 五、常用命令

查看当前服务：

```bash
cd /www/wwwroot/lixue-quiz
docker compose ps
```

查看后端日志：

```bash
cd /www/wwwroot/lixue-quiz
docker compose logs -f server
```

手动检查后端：

```bash
curl http://127.0.0.1:8000/api/health
```

手动检查前端：

```bash
curl -I http://127.0.0.1:8080
```
