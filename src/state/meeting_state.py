"""会议聊天室状态定义"""

from typing import TypedDict, List, Literal, Optional, Annotated, Any
from langchain_core.messages import BaseMessage, HumanMessage


def convert_messages(left: List[BaseMessage], right: Any, **kwargs) -> List[BaseMessage]:
    """合并消息列表
    
    Args:
        left: 左侧消息列表
        right: 右侧消息（可以是单个消息或消息列表）
        
    Returns:
        合并后的消息列表
    """
    if right is None:
        return left
    
    # 如果 right 是单个消息，转换为列表
    if isinstance(right, BaseMessage):
        right_messages = [right]
    elif isinstance(right, str):
        # 如果是字符串，转换为 HumanMessage
        right_messages = [HumanMessage(content=str(right))]
    elif isinstance(right, list):
        right_messages = right
    else:
        # 其他类型转换为字符串
        right_messages = [HumanMessage(content=str(right))]
    
    # 合并消息列表
    return left + right_messages


class MeetingState(TypedDict):
    """会议聊天室状态
    
    Attributes:
        messages: 聊天消息列表
        room_language: 会议室主体语言 ('zh' 或 'en')
        current_user: 当前发言用户
        audio_data: 音频数据（base64编码或文件路径）
        original_text: 原始输入文本（可能是语音识别结果）
        translated_text: 翻译后的文本
        participants: 参与者列表
    """
    messages: Annotated[list[BaseMessage], convert_messages]
    room_language: Literal["zh", "en"]
    current_user: str
    audio_data: Optional[str]  # base64编码的音频数据或文件路径
    original_text: Optional[str]  # 原始输入文本
    translated_text: Optional[str]  # 翻译后的文本
    participants: List[str]  # 参与者列表
