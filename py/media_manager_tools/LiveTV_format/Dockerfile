# 使用官方 Python 基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装必要的依赖
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码到容器中
COPY . /app

# 开放应用端口
EXPOSE 35456

# 使用 Gunicorn 启动应用
CMD ["gunicorn", "--config", "gunicorn_config.py", "livetv_format:create_app()"]