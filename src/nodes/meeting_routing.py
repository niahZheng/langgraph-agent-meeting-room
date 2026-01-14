"""会议工作流路由"""

from typing import Literal
from ..state.meeting_state import MeetingState


def should_translate(state: MeetingState) -> Literal["translate", "skip_translate"]:
    """
    判断是否需要翻译
    
    Args:
        state: 当前状态
        
    Returns:
        "translate" 如果需要翻译，"skip_translate" 如果不需要
    """
    room_language = state.get("room_language", "zh")
    original_text = state.get("original_text")
    translated_text = state.get("translated_text")
    
    # 如果已经有翻译结果，跳过
    if translated_text:
        return "skip_translate"
    
    if not original_text:
        return "skip_translate"
    
    # 检测语言
    from ..services.translation import TranslationService
    translation_service = TranslationService()
    detected_lang = translation_service.detect_language(original_text)
    
    # 如果检测到的语言与会议室语言不同，需要翻译
    if detected_lang != room_language:
        return "translate"
    else:
        return "skip_translate"


def should_recognize_speech(state: MeetingState) -> Literal["recognize", "skip_recognize"]:
    """
    判断是否需要语音识别（用于入口路由）
    
    Args:
        state: 当前状态
        
    Returns:
        "recognize" 如果有音频数据需要识别，"skip_recognize" 如果不需要
    """
    audio_data = state.get("audio_data")
    original_text = state.get("original_text")
    
    # 如果有音频数据，需要识别
    if audio_data:
        return "recognize"
    # 如果已经有原始文本（文本输入），跳过识别
    elif original_text:
        return "skip_recognize"
    else:
        return "skip_recognize"
