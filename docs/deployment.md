# 服务器部署指南

> 目标环境：腾讯云 CVM · Ubuntu 24.04 LTS

---

## 前置准备

### 腾讯云安全组放行端口

控制台路径：云服务器 → 实例 → 安全组 → 添加入站规则

| 协议 | 端口 | 来源 |
|------|------|------|
| TCP | 80 | 0.0.0.0/0 |
| TCP | 22 | 0.0.0.0/0 |

---

## 一、安装依赖

SSH 登录服务器后，切换到 root：

```bash
sudo -i
```

### 更新系统

```bash
apt update && apt upgrade -y
```

> 升级过程中如果弹出 `Configuring openssh-server` 弹窗，选择 **keep the local version currently installed**，按 Enter 确认。
>
> 升级完成后重启服务器：`reboot`，等待约 30 秒后重新 SSH 连接。

### 安装 Docker

```bash
apt install docker.io -y
```

### 安装 Docker Compose v2

```bash
curl -L "https://ghfast.top/https://github.com/docker/compose/releases/download/v2.24.6/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
hash -r
docker-compose --version  # 应输出 Docker Compose version v2.24.6
```

### 配置 Docker 国内镜像源

```bash
nano /etc/docker/daemon.json
```

填入：

```json
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com"
  ]
}
```

重启 Docker：

```bash
systemctl restart docker
```

### 将当前用户加入 docker 组（可选，避免每次加 sudo）

```bash
usermod -aG docker ubuntu
```

重新登录后生效，或执行 `newgrp docker` 立即生效。

---

## 二、部署项目

### 克隆代码

```bash
# 如果 GitHub 访问慢，使用镜像
git clone https://ghfast.top/https://github.com/pear-studio/dungeon-toolkit-web.git
cd dungeon-toolkit-web
```

### 配置环境变量

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

**必须修改的项：**

```env
# 生成随机密钥：python3 -c "import secrets; print(secrets.token_urlsafe(50))"
SECRET_KEY=替换为随机长字符串

# 填写服务器公网 IP 或域名
ALLOWED_HOSTS=你的服务器IP

# 修改为自己的数据库密码（同时要改 docker-compose.yml 里对应的值）
DB_PASSWORD=自定义强密码
```

### 创建 .env 软链接

> docker-compose 默认从根目录读取 `.env` 做变量插值，软链接让两者共用同一份文件，避免重复维护。

```bash
ln -s backend/.env .env
```

### 启动服务

```bash
docker-compose up -d --build
```

第一次启动会拉取镜像、编译前端，约需 **3~5 分钟**。

### 验证启动状态

```bash
docker-compose ps
```

四个服务（db / backend / frontend / nginx）均显示 `running` 或 `exited`（frontend 构建完就退出，正常）即为成功。

打开浏览器访问 `http://你的服务器IP`，看到登录页面说明部署成功 🎉

---

## 三、常用维护命令

```bash
# 查看所有服务状态
docker-compose ps

# 查看后端日志（实时）
docker-compose logs -f backend

# 查看 nginx 日志
docker-compose logs -f nginx

# 重启某个服务
docker-compose restart backend

# 停止所有服务
docker-compose down

# 拉取新代码并重新部署
git pull && docker-compose up -d --build
```

---

## 四、注意事项

- `.env` 文件包含密钥和密码，**不要提交到 Git**（已在 `.gitignore` 中忽略）
- 数据库密码在 `backend/.env` 和 `docker-compose.yml` 中需要保持一致
- 每次执行 `docker-compose` 命令都需要在项目根目录下，或确保根目录有 `.env` 软链接
- 升级 docker-compose 后旧版路径可能还在 PATH 缓存中，执行 `hash -r` 刷新
