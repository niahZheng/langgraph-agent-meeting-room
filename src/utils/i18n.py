"""国际化 (i18n) 支持 - 动态语言识别和多语言界面"""

import streamlit as st
from typing import Dict, Optional
import json


# 语言资源文件
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "zh": {
        # 通用
        "app_title": "多人会议聊天室",
        "welcome": "欢迎",
        "login": "登录",
        "logout": "注销",
        "register": "注册",
        "username": "用户名",
        "password": "密码",
        "confirm_password": "确认密码",
        "email": "邮箱",
        "submit": "提交",
        "cancel": "取消",
        "success": "成功",
        "error": "错误",
        "warning": "警告",
        "info": "信息",
        
        # 房间相关
        "create_room": "创建房间",
        "join_room": "加入房间",
        "create_or_join_room": "创建或加入房间",
        "room_id": "房间ID",
        "room_name": "房间名称",
        "room_language": "房间语言",
        "leave_room": "退出房间",
        "current_room": "当前房间",
        "room_list": "房间列表",
        "select_room": "选择房间",
        "no_rooms": "暂无可用房间",
        "room_created": "房间创建成功",
        "room_joined": "已加入房间",
        "room_left": "已退出房间",
        "room_not_found": "房间不存在",
        "already_in_room": "您已在此房间中",
        "already_in_other_room": "您已在其他房间中，请先退出当前房间",
        
        # 参与者
        "participants": "参与者列表",
        "participant": "参与者",
        "admin": "管理员",
        "remove_participant": "移除参与者",
        "user_joined": "加入了房间",
        "user_left": "离开了房间",
        "user_removed": "被移出房间",
        
        # 消息
        "send_message": "发送消息",
        "message_sent": "消息已发送",
        "message_failed": "消息发送失败",
        "input_message": "输入消息...",
        "voice_input": "语音输入",
        "send_text": "发送文字",
        "send_audio": "发送语音",
        "chat_messages": "聊天消息",
        "no_messages": "暂无消息",
        
        # 语言设置
        "my_display_language": "我的显示语言",
        "chinese": "中文",
        "english": "English",
        "language": "语言",
        
        # 系统消息
        "system": "系统",
        "please_login": "请先登录",
        "please_join_room": "请先创建或加入房间",
        "please_join_room_to_chat": "请先创建或加入房间才能开始聊天",
        "auto_refresh": "自动刷新",
        "auto_refresh_on": "自动刷新已开启",
        "auto_refresh_off": "自动刷新已关闭",
        "refresh_interval": "页面将每{}秒自动更新",
        
        # 错误消息
        "error_empty_message": "消息内容不能为空",
        "error_not_in_room": "请先创建或加入房间",
        "error_not_logged_in": "用户未登录",
        "error_username_exists": "该房间中已存在同名用户，无法加入",
        "error_room_exists": "房间已存在",
        "error_operation_failed": "操作失败",
        
        # 使用说明
        "usage_instructions": "使用说明",
        "usage_create_join": "创建/加入房间：输入房间ID，点击创建或加入",
        "usage_send_message": "发送消息：输入文字或使用语音输入",
        "usage_language": "语言设置：选择您的显示语言",
        "usage_auto_refresh": "自动刷新：开启后自动接收新消息",
    },
    "en": {
        # Common
        "app_title": "Multi-Person Meeting Chatroom",
        "welcome": "Welcome",
        "login": "Login",
        "logout": "Logout",
        "register": "Register",
        "username": "Username",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "email": "Email",
        "submit": "Submit",
        "cancel": "Cancel",
        "success": "Success",
        "error": "Error",
        "warning": "Warning",
        "info": "Info",
        
        # Room related
        "create_room": "Create Room",
        "join_room": "Join Room",
        "create_or_join_room": "Create or Join Room",
        "room_id": "Room ID",
        "room_name": "Room Name",
        "room_language": "Room Language",
        "leave_room": "Leave Room",
        "current_room": "Current Room",
        "room_list": "Room List",
        "select_room": "Select Room",
        "no_rooms": "No available rooms",
        "room_created": "Room created successfully",
        "room_joined": "Joined room",
        "room_left": "Left room",
        "room_not_found": "Room not found",
        "already_in_room": "You are already in this room",
        "already_in_other_room": "You are already in another room, please leave the current room first",
        
        # Participants
        "participants": "Participants",
        "participant": "Participant",
        "admin": "Administrator",
        "remove_participant": "Remove Participant",
        "user_joined": "joined the room",
        "user_left": "left the room",
        "user_removed": "was removed from the room",
        
        # Messages
        "send_message": "Send Message",
        "message_sent": "Message sent",
        "message_failed": "Failed to send message",
        "input_message": "Input message...",
        "voice_input": "Voice Input",
        "send_text": "Send Text",
        "send_audio": "Send Audio",
        "chat_messages": "Chat Messages",
        "no_messages": "No messages yet",
        
        # Language settings
        "my_display_language": "My Display Language",
        "chinese": "中文",
        "english": "English",
        "language": "Language",
        
        # System messages
        "system": "System",
        "please_login": "Please login first",
        "please_join_room": "Please create or join a room first",
        "please_join_room_to_chat": "Please create or join a room to start chatting",
        "auto_refresh": "Auto Refresh",
        "auto_refresh_on": "Auto refresh enabled",
        "auto_refresh_off": "Auto refresh disabled",
        "refresh_interval": "Page will auto-update every {} seconds",
        
        # Error messages
        "error_empty_message": "Message content cannot be empty",
        "error_not_in_room": "Please create or join a room first",
        "error_not_logged_in": "User not logged in",
        "error_username_exists": "A user with the same name already exists in this room",
        "error_room_exists": "Room already exists",
        "error_operation_failed": "Operation failed",
        
        # Usage instructions
        "usage_instructions": "Usage Instructions",
        "usage_create_join": "Create/Join Room: Enter room ID and click create or join",
        "usage_send_message": "Send Message: Enter text or use voice input",
        "usage_language": "Language Settings: Select your display language",
        "usage_auto_refresh": "Auto Refresh: Enable to automatically receive new messages",
    }
}


def detect_browser_language() -> str:
    """检测浏览器语言设置
    
    Returns:
        检测到的语言代码 ("zh" 或 "en")，默认为 "zh"
    """
    try:
        # 使用 JavaScript 检测浏览器语言
        html = """
        <script>
        (function() {
            const lang = navigator.language || navigator.userLanguage;
            const langCode = lang.toLowerCase().split('-')[0];
            // 将语言代码保存到 sessionStorage
            if (langCode === 'zh' || langCode === 'en') {
                sessionStorage.setItem('detected_language', langCode);
            } else {
                // 默认使用英文（如果浏览器语言不是中文或英文）
                sessionStorage.setItem('detected_language', 'en');
            }
        })();
        </script>
        """
        st.markdown(html, unsafe_allow_html=True)
        
        # 尝试从 sessionStorage 读取（需要等待 JavaScript 执行）
        # 由于 Streamlit 的限制，我们使用 URL 参数或 session_state
        # 这里先返回默认值，实际检测在初始化时完成
        return "zh"
    except:
        return "zh"


def get_user_language() -> str:
    """获取用户当前选择的语言
    
    Returns:
        用户语言代码 ("zh" 或 "en")
    """
    # 优先使用用户手动选择的语言
    if "user_language" in st.session_state:
        return st.session_state.user_language
    
    # 其次使用检测到的浏览器语言
    if "detected_language" in st.session_state:
        return st.session_state.detected_language
    
    # 默认使用中文
    return "zh"


def set_user_language(lang: str):
    """设置用户语言
    
    Args:
        lang: 语言代码 ("zh" 或 "en")
    """
    if lang in ["zh", "en"]:
        st.session_state.user_language = lang


def t(key: str, **kwargs) -> str:
    """翻译函数 - 获取当前语言的翻译文本
    
    Args:
        key: 翻译键
        **kwargs: 格式化参数（用于字符串格式化）
        
    Returns:
        翻译后的文本
    """
    lang = get_user_language()
    translations = TRANSLATIONS.get(lang, TRANSLATIONS["zh"])
    text = translations.get(key, key)  # 如果找不到翻译，返回键本身
    
    # 如果有格式化参数，进行字符串格式化
    if kwargs:
        try:
            text = text.format(**kwargs)
        except:
            pass
    
    return text


def init_language_detection():
    """初始化语言检测 - 在应用启动时调用"""
    # 从 URL 参数读取检测到的语言（如果已设置）
    detected_lang = st.query_params.get("detected_lang")
    
    # 如果用户语言未设置，尝试检测浏览器语言
    if "user_language" not in st.session_state:
        if detected_lang and detected_lang in ["zh", "en"]:
            # 使用 URL 参数中的语言
            st.session_state.user_language = detected_lang
            st.session_state.detected_language = detected_lang
        else:
            # 检测浏览器语言（使用 JavaScript）
            html = """
            <script>
            (function() {
                if (!sessionStorage.getItem('browser_lang_detected')) {
                    const lang = navigator.language || navigator.userLanguage;
                    const langCode = lang.toLowerCase().split('-')[0];
                    let detectedLang = 'zh'; // 默认中文
                    
                    if (langCode === 'zh') {
                        detectedLang = 'zh';
                    } else if (langCode === 'en') {
                        detectedLang = 'en';
                    } else {
                        // 如果浏览器语言不是中文或英文，默认使用英文
                        detectedLang = 'en';
                    }
                    
                    // 将检测到的语言保存到 URL 参数
                    const urlParams = new URLSearchParams(window.location.search);
                    if (!urlParams.has('detected_lang')) {
                        urlParams.set('detected_lang', detectedLang);
                        window.history.replaceState({}, '', window.location.pathname + '?' + urlParams.toString());
                        sessionStorage.setItem('browser_lang_detected', 'true');
                        // 触发页面重新加载以应用语言设置
                        setTimeout(function() {
                            window.location.reload();
                        }, 100);
                    }
                }
            })();
            </script>
            """
            st.markdown(html, unsafe_allow_html=True)
            
            # 如果 URL 参数中有语言，使用它
            if detected_lang and detected_lang in ["zh", "en"]:
                st.session_state.user_language = detected_lang
                st.session_state.detected_language = detected_lang
            else:
                # 默认使用中文
                st.session_state.user_language = "zh"
                st.session_state.detected_language = "zh"
