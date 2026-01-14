"""语音识别节点"""

from ..state.meeting_state import MeetingState
from ..services.speech_recognition import SpeechRecognitionService


def speech_recognition_node(state: MeetingState) -> dict:
    """语音识别节点：将音频转换为文字
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态，包含识别出的文字
    """
    audio_data = state.get("audio_data")
    
    if not audio_data:
        # 如果没有音频数据，直接返回
        return {"original_text": None}
    
    try:
        # 初始化语音识别服务
        speech_service = SpeechRecognitionService()
        
        # 识别语音
        recognized_text = speech_service.recognize(audio_data)
        
        if recognized_text:
            return {
                "original_text": recognized_text
            }
        else:
            return {
                "original_text": None
            }
            
    except Exception as e:
        print(f"语音识别节点出错: {str(e)}")
        return {
            "original_text": None
        }
