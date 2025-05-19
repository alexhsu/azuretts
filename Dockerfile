# 使用Python 3.9作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY app.py .
COPY config.yaml .

# 创建音频输出目录
RUN mkdir -p audio_output

# 复制前端构建后的静态文件
COPY web/dist/ /app/static/

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV AZURE_TTS_KEY=""
ENV AZURE_TTS_REGION=""
ENV AZURE_TTS_VOICE="zh-CN-XiaoxiaoNeural"
ENV AUDIO_OUTPUT_DIR="audio_output"
ENV SERVER_HOST="0.0.0.0"
ENV SERVER_PORT="5000"
ENV FLASK_DEBUG="false"

# 启动应用
CMD ["python", "app.py"] 