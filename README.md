# Azure TTS 语音生成服务

这是一个基于 Azure 认知服务的文本转语音（TTS）API 服务。

## 功能特点

- 支持中文文本转语音
- 使用 Azure 云服务进行语音合成
- RESTful API 接口
- 自动生成 MP3 音频文件
- 基于 YAML 的配置文件

## 安装

1. 克隆代码库
2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

在 `config.yaml` 中配置服务参数：

```yaml
azure_tts:
  subscription_key: "您的密钥"
  region: "您的区域"
  voice_name: "zh-CN-YunyangNeural"

http_server:
  host: "0.0.0.0"
  port: 5000
  debug: true

output:
  directory: "generated_audio"
```

## 运行服务

```bash
python app.py
```

服务将在配置的地址和端口上运行（默认为 http://localhost:5000）。

## API 使用说明

### 生成语音

**请求：**
```http
POST /api/tts
Content-Type: application/json

{
    "text": "要转换的文本内容"
}
```

**成功响应：**
```json
{
    "success": true,
    "message": "语音生成成功",
    "file_path": "generated_audio/speech_20240321_123456.mp3"
}
```

### 下载音频文件

**请求：**
```http
GET /api/audio/speech_20240321_123456.mp3
```

## 前端构建部署

### 安装前端依赖
```bash
cd web
npm install
```

### 开发模式运行
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

## Docker 部署

### 构建 Docker 镜像
```bash
docker build -t azure-tts-service .
```

### 运行 Docker 容器
```bash
docker run -d \
  -p 5000:5000 \
  -e AZURE_TTS_KEY="您的密钥" \
  -e AZURE_TTS_REGION="您的区域" \
  -e AZURE_TTS_VOICE="zh-CN-XiaoxiaoNeural" \
  -v $(pwd)/audio_output:/app/audio_output \
  --name azure-tts \
  azure-tts-service
```

### 环境变量说明

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| AZURE_TTS_KEY | Azure TTS 服务密钥 | - |
| AZURE_TTS_REGION | Azure 服务区域 | - |
| AZURE_TTS_VOICE | 语音合成声音 | zh-CN-XiaoxiaoNeural |
| AUDIO_OUTPUT_DIR | 音频输出目录 | audio_output |
| SERVER_HOST | 服务器主机地址 | 0.0.0.0 |
| SERVER_PORT | 服务器端口 | 5000 |
| FLASK_DEBUG | 调试模式 | false |

### Docker Compose 部署

创建 `docker-compose.yml` 文件：

```yaml
version: '3'
services:
  azure-tts:
    build: .
    ports:
      - "5000:5000"
    environment:
      - AZURE_TTS_KEY=您的密钥
      - AZURE_TTS_REGION=您的区域
      - AZURE_TTS_VOICE=zh-CN-XiaoxiaoNeural
    volumes:
      - ./audio_output:/app/audio_output
```

使用 Docker Compose 启动服务：

```bash
docker-compose up -d
```

## 注意事项

- 确保有足够的磁盘空间存储生成的音频文件
- 建议定期清理 `generated_audio` 目录中的旧文件
- 请妥善保管您的 Azure 密钥
- 修改配置后需要重启服务才能生效
- 使用 Docker 部署时，请确保正确设置环境变量
- 生产环境部署时建议关闭调试模式 