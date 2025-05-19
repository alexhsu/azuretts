from flask import Flask, request, jsonify, send_file, send_from_directory
import os
import time
import yaml
import azure.cognitiveservices.speech as speechsdk
from datetime import datetime
import zipfile
import io

# 加载配置文件
def load_config():
    config = {
        'azure_tts': {
            'subscription_key': os.getenv('AZURE_TTS_KEY', ''),
            'region': os.getenv('AZURE_TTS_REGION', ''),
            'voice_name': os.getenv('AZURE_TTS_VOICE', 'zh-CN-XiaoxiaoNeural')
        },
        'output': {
            'directory': os.getenv('AUDIO_OUTPUT_DIR', 'audio_output')
        },
        'http_server': {
            'host': os.getenv('SERVER_HOST', '0.0.0.0'),
            'port': int(os.getenv('SERVER_PORT', '5000')),
            'debug': os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
        }
    }
    
    # 如果存在配置文件，则从配置文件加载
    if os.path.exists('config.yaml'):
        with open('config.yaml', 'r', encoding='utf-8') as f:
            yaml_config = yaml.safe_load(f)
            # 合并配置，环境变量优先级高于配置文件
            for section in yaml_config:
                if section in config:
                    config[section].update(yaml_config[section])
    
    return config

config = load_config()

app = Flask(__name__, static_folder='static', static_url_path='')

# 创建输出目录
OUTPUT_DIR = config['output']['directory']
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 添加根路由，返回前端页面
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# 添加通配符路由，处理前端路由
@app.route('/<path:path>')
def catch_all(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

def create_speech_synthesizer():
    if not config['azure_tts']['subscription_key'] or not config['azure_tts']['region']:
        raise ValueError("Azure TTS subscription key and region must be provided")
        
    speech_config = speechsdk.SpeechConfig(
        subscription=config['azure_tts']['subscription_key'],
        region=config['azure_tts']['region']
    )
    speech_config.speech_synthesis_voice_name = config['azure_tts']['voice_name']
    return speechsdk.SpeechSynthesizer(speech_config=speech_config)

def generate_speech(text, filename):
    speech_synthesizer = create_speech_synthesizer()
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        with open(output_path, "wb") as file:
            file.write(speech_synthesis_result.audio_data)
        return True, output_path
    else:
        return False, str(speech_synthesis_result.cancellation_details.reason)

def create_zip_file(files, batch_id):
    """创建包含所有音频文件的ZIP包"""
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for file in files:
            file_path = os.path.join(OUTPUT_DIR, file['file_path'])
            if os.path.exists(file_path):
                zf.write(file_path, file['file_path'])
    
    memory_file.seek(0)
    return memory_file

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': '请提供文本内容'}), 400
            
        text = data['text']
        if not text:
            return jsonify({'error': '文本内容不能为空'}), 400
            
        # 按行分割文本
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return jsonify({'error': '文本内容不能为空'}), 400

        # 生成时间戳作为批次标识
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results = []
        
        # 为每行文本生成音频
        for i, line in enumerate(lines, 1):
            filename = f"speech_{timestamp}_{i:03d}.mp3"
            success, result = generate_speech(line, filename)
            
            if success:
                results.append({
                    'line_number': i,
                    'text': line,
                    'file_path': filename
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'第 {i} 行语音生成失败: {result}'
                }), 500
        
        return jsonify({
            'success': True,
            'message': '语音生成成功',
            'batch_id': timestamp,
            'total_lines': len(lines),
            'files': results
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500

@app.route('/api/audio/<filename>', methods=['GET'])
def get_audio(filename):
    try:
        return send_file(
            os.path.join(OUTPUT_DIR, filename),
            mimetype='audio/mpeg',
            as_attachment=True
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'文件不存在或无法访问: {str(e)}'
        }), 404

@app.route('/api/download-all/<batch_id>', methods=['GET'])
def download_all(batch_id):
    try:
        # 获取该批次的所有文件
        files = []
        for filename in os.listdir(OUTPUT_DIR):
            if filename.startswith(f"speech_{batch_id}"):
                files.append({
                    'file_path': filename,
                    'line_number': int(filename.split('_')[-1].split('.')[0])
                })
        
        if not files:
            return jsonify({
                'success': False,
                'error': '未找到相关音频文件'
            }), 404

        # 创建ZIP文件
        zip_file = create_zip_file(files, batch_id)
        
        return send_file(
            zip_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'audio_files_{batch_id}.zip'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'创建压缩包失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(
        host=config['http_server']['host'],
        port=config['http_server']['port'],
        debug=config['http_server']['debug']
    ) 