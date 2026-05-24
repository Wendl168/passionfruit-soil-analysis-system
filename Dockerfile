# ============================================================
# Dockerfile - 百香果智能土壤分析系统
# ============================================================
# 构建：
#   docker build -t passionfruit-soil-system .
#
# 运行：
#   docker run -d -p 5000:5000 passionfruit-soil-system
# ============================================================

FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建数据目录（SQLite 存放位置）
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 5000

# 设置默认环境变量
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

# 启动服务
CMD ["python", "app.py"]
