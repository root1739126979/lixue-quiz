# 宝塔面板部署说明

这份说明用于把当前项目部署到已经安装宝塔面板的阿里云服务器。项目由三部分组成：

- 前端：React/Vite，容器内 Nginx 监听 `8080`
- 后端：FastAPI，容器内监听 `8000`
- 数据库：PostgreSQL，数据保存在 Docker volume 中

## 一、准备信息

部署前先准备好：

- 阿里云服务器公网 IP，例如 `1.2.3.4`
- 已购买的域名，例如 `example.com`
- 宝塔面板登录地址、账号、密码
- 宝塔面板的软件商店里安装：Docker、Nginx

## 二、域名解析

在阿里云域名控制台添加解析记录：

| 主机记录 | 记录类型 | 记录值 |
| --- | --- | --- |
| `@` | `A` | 服务器公网 IP |
| `www` | `A` | 服务器公网 IP |

解析生效后，访问 `http://你的域名` 才会到这台服务器。

## 三、上传项目

推荐在宝塔面板中操作：

1. 打开宝塔面板。
2. 进入左侧「文件」。
3. 打开 `/www/wwwroot`。
4. 新建目录 `lixue-quiz`。
5. 把当前项目上传到 `/www/wwwroot/lixue-quiz`。

上传后目录应类似：

```text
/www/wwwroot/lixue-quiz
├── docker-compose.yml
├── .env.example
├── server
└── web
```

## 四、创建生产环境配置

在宝塔文件管理器中：

1. 复制 `.env.example`。
2. 重命名为 `.env`。
3. 编辑 `.env`。

请至少修改下面三项：

```env
POSTGRES_PASSWORD=换成一个复杂的数据库密码
DATABASE_URL=postgresql+psycopg://lixue:换成同一个数据库密码@db:5432/lixue
JWT_SECRET=换成一串很长的随机字符
ADMIN_PASSWORD=换成管理员登录密码
```

注意：`POSTGRES_PASSWORD` 和 `DATABASE_URL` 中间的密码必须完全一样。

## 五、启动项目

在宝塔面板中打开「终端」，执行：

```bash
cd /www/wwwroot/lixue-quiz
docker compose up -d --build
```

等待完成后执行：

```bash
docker compose ps
```

正常时应看到 `db`、`server`、`web` 都是 running 或 up 状态。

再执行：

```bash
curl http://127.0.0.1:8000/api/health
```

正常返回：

```json
{"status":"ok"}
```

## 六、在宝塔创建网站

1. 打开宝塔面板左侧「网站」。
2. 点击「添加站点」。
3. 域名填写你的域名，例如：

```text
example.com
www.example.com
```

4. 根目录可保持宝塔默认创建的目录。
5. PHP 版本选择「纯静态」。
6. 提交。

## 七、配置反向代理

进入刚创建的网站设置：

1. 点击「反向代理」。
2. 点击「添加反向代理」。
3. 名称填写 `lixue-web`。
4. 目标 URL 填写：

```text
http://127.0.0.1:8080
```

5. 保存。

如果宝塔要求高级配置，可使用下面的 Nginx 配置片段：

```nginx
location / {
    proxy_pass http://127.0.0.1:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

项目前端容器会自动把 `/api/` 请求转发到后端容器，所以宝塔只需要代理到 `8080`。

## 八、申请 HTTPS

进入网站设置：

1. 点击「SSL」。
2. 选择 Let's Encrypt。
3. 勾选域名。
4. 点击申请。
5. 申请成功后开启「强制 HTTPS」。

## 九、首次登录

部署完成后访问：

```text
https://你的域名/admin/login
```

管理员账号密码来自 `.env`：

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=你设置的管理员密码
```

登录后先导入员工，再创建题库并导入题目。

## 十、日常维护命令

查看运行状态：

```bash
cd /www/wwwroot/lixue-quiz
docker compose ps
```

查看后端日志：

```bash
cd /www/wwwroot/lixue-quiz
docker compose logs -f server
```

重启项目：

```bash
cd /www/wwwroot/lixue-quiz
docker compose restart
```

更新代码后重新构建：

```bash
cd /www/wwwroot/lixue-quiz
docker compose up -d --build
```

## 十一、常见问题

如果网页打不开：

1. 检查阿里云安全组是否放行 `80` 和 `443` 端口。
2. 检查宝塔网站是否启用。
3. 执行 `docker compose ps` 看容器是否运行。

如果登录失败：

1. 确认访问的是 `/admin/login`。
2. 确认 `.env` 中 `ADMIN_USERNAME` 和 `ADMIN_PASSWORD` 没写错。
3. 修改 `.env` 后执行 `docker compose restart server`。

如果数据丢失：

1. 不要删除 Docker volume。
2. 不要执行 `docker compose down -v`。
3. 正常重启、重新构建不会删除数据库数据。
