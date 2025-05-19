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

## 注意事项

- 确保有足够的磁盘空间存储生成的音频文件
- 建议定期清理 `generated_audio` 目录中的旧文件
- 请妥善保管您的 Azure 密钥
- 修改配置后需要重启服务才能生效 