"""会议聊天室工作流"""

import streamlit as st
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from typing import Literal
from ..state.meeting_state import MeetingState
from ..nodes.speech_recognition_node import speech_recognition_node
from ..nodes.translation_node import translation_node
from ..nodes.message_node import message_node
from ..nodes.meeting_routing import should_translate, should_recognize_speech


@st.cache_resource
def get_meeting_app():
    """构建会议聊天室应用（使用缓存）
    
    Returns:
        编译后的 LangGraph 应用
    """
    workflow = StateGraph(MeetingState)
    
    # 创建入口路由节点
    def entry_node(state: MeetingState) -> dict:
        """入口节点：根据输入类型路由到不同节点"""
        # 这个节点不做任何处理，只是路由
        return {}
    
    # 添加节点
    workflow.add_node("entry", entry_node)
    workflow.add_node("speech_recognition", speech_recognition_node)
    workflow.add_node("translation", translation_node)
    workflow.add_node("message", message_node)
    
    # 设置入口点
    workflow.set_entry_point("entry")
    
    # 入口节点后根据是否有音频数据路由
    workflow.add_conditional_edges(
        "entry",
        should_recognize_speech,
        {
            "recognize": "speech_recognition",
            "skip_recognize": "translation"  # 如果没有音频，直接进入翻译（处理文本输入）
        }
    )
    
    # 语音识别后判断是否需要翻译
    workflow.add_conditional_edges(
        "speech_recognition",
        should_translate,
        {
            "translate": "translation",
            "skip_translate": "message"
        }
    )
    
    # 翻译后进入消息处理
    workflow.add_edge("translation", "message")
    
    # 消息处理完成后结束
    workflow.add_edge("message", END)
    
    # 编译工作流
    try:
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    except Exception:
        return workflow.compile()
