"""消息处理节点"""

from langchain_core.messages import HumanMessage
from ..state.meeting_state import MeetingState


def message_node(state: MeetingState) -> dict:
    """消息处理节点：将处理后的文本添加到消息列表
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态，包含新消息（包含原始文本和翻译文本）
    """
    current_user = state.get("current_user", "用户")
    translated_text = state.get("translated_text")
    original_text = state.get("original_text")
    room_language = state.get("room_language", "zh")
    
    if not original_text:
        return {"messages": []}
    
    # 检测原始语言
    from ..services.translation import TranslationService
    translation_service = TranslationService()
    original_lang = translation_service.detect_language(original_text)
    
    # 创建消息，包含原始文本和翻译文本
    # 格式：用户名: 原始文本 | 翻译文本
    if translated_text and translated_text != original_text:
        message_content = f"{current_user}: {original_text} | {translated_text} | {original_lang}"
    else:
        message_content = f"{current_user}: {original_text} | | {original_lang}"
    
    new_message = HumanMessage(content=message_content)
    
    return {
        "messages": [new_message]
    }
