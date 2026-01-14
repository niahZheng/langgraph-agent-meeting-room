"""阿里百炼语音识别服务"""

import os
import base64
import json
import requests
from typing import Optional
from ..config.settings import get_settings


class SpeechRecognitionService:
    """阿里百炼语音识别服务"""
    
    def __init__(self):
        """初始化服务"""
        self.settings = get_settings()
        self.api_key = self.settings.dashscope_api_key
        # 阿里百炼语音识别API端点
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription"
    
    def recognize(self, audio_data: str, format: str = "wav", sample_rate: int = 16000) -> Optional[str]:
        """
        识别语音并转换为文字
        
        Args:
            audio_data: base64编码的音频数据或文件路径
            format: 音频格式 (wav, mp3, m4a等)
            sample_rate: 采样率
            
        Returns:
            识别出的文字，如果失败返回None
        """
        try:
            # 如果是文件路径，读取文件并转换为base64
            if os.path.exists(audio_data):
                with open(audio_data, 'rb') as f:
                    audio_bytes = f.read()
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            else:
                # 假设已经是base64编码
                audio_base64 = audio_data
            
            # 调用阿里百炼语音识别API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 阿里百炼语音识别API参数
            payload = {
                "model": "paraformer-realtime-v2",  # 实时语音识别模型
                "format": format,
                "sample_rate": sample_rate,
                "audio": audio_base64
            }
            
            # 如果API不支持直接传base64，可能需要使用文件上传方式
            # 这里先尝试base64方式
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # 解析返回结果
                if "output" in result and "text" in result["output"]:
                    return result["output"]["text"]
                elif "text" in result:
                    return result["text"]
                else:
                    print(f"API返回格式异常: {result}")
                    return None
            else:
                print(f"语音识别API调用失败: {response.status_code}, {response.text}")
                return None
                
        except Exception as e:
            print(f"语音识别出错: {str(e)}")
            return None
    
    def recognize_from_streamlit_audio(self, audio_bytes: bytes) -> Optional[str]:
        """
        从Streamlit音频输入识别
        
        Args:
            audio_bytes: Streamlit audio组件的音频字节数据
            
        Returns:
            识别出的文字
        """
        try:
            # 将音频字节转换为base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            return self.recognize(audio_base64, format="wav", sample_rate=16000)
        except Exception as e:
            print(f"处理Streamlit音频出错: {str(e)}")
            return None
