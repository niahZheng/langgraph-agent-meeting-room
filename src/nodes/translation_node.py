"""翻译节点"""

from ..state.meeting_state import MeetingState
from ..services.translation import TranslationService


def translation_node(state: MeetingState) -> dict:
    """翻译节点：根据会议室语言翻译文本
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态，包含翻译后的文本
    """
    room_language = state.get("room_language", "zh")
    original_text = state.get("original_text")
    
    if not original_text:
        return {"translated_text": None}
    
    try:
        # 初始化翻译服务
        translation_service = TranslationService()
        
        # 检测输入语言
        detected_lang = translation_service.detect_language(original_text)
        
        # 如果检测到的语言与会议室语言不同，需要翻译
        if detected_lang != room_language:
            translated_text = translation_service.translate(
                original_text,
                source_lang=detected_lang,
                target_lang=room_language
            )
            return {
                "translated_text": translated_text
            }
        else:
            # 语言相同，不需要翻译
            return {
                "translated_text": original_text
            }
            
    except Exception as e:
        print(f"翻译节点出错: {str(e)}")
        # 翻译失败时返回原文
        return {
            "translated_text": original_text
        }
