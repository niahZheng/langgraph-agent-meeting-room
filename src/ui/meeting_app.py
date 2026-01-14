"""会议聊天室 Streamlit UI 应用"""

import streamlit as st
import streamlit.components.v1 as components
import base64
import io
import time
from typing import List
from langchain_core.messages import HumanMessage, AIMessage

from ..workflow.meeting_workflow import get_meeting_app
from ..state.meeting_state import MeetingState
from ..services.room_manager import get_room_manager
from .state_persistence import init_state_restoration, auto_save_state
from .auth_ui import render_login_page, check_login, logout
from ..utils.i18n import t, get_user_language, set_user_language, init_language_detection


def create_meeting_app():
    """创建并配置会议聊天室应用"""
    # 初始化语言检测（必须在页面配置之前）
    init_language_detection()
    
    # 获取用户语言并设置页面标题
    user_lang = get_user_language()
    app_title = t("app_title")
    
    st.set_page_config(
        page_title=app_title,
        page_icon="💬",
        layout="wide"
    )
    
    # 注入专业风格的CSS
    st.markdown("""
    <style>
    /* 专业风格 - 调整字体大小和间距 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* 标题字体 */
    h1 {
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    h3 {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* 正文字体 */
    .stMarkdown, .stText, p, div {
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
    }
    
    /* 按钮样式 */
    .stButton > button {
        font-size: 0.85rem !important;
        padding: 0.4rem 1rem !important;
        border-radius: 6px !important;
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input {
        font-size: 0.9rem !important;
        padding: 0.5rem !important;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        font-size: 0.85rem !important;
    }
    
    /* 消息气泡样式优化 */
    .chat-message {
        font-size: 0.9rem !important;
        line-height: 1.4 !important;
    }
    
    /* 系统消息样式 */
    .system-message {
        font-size: 0.8rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 从URL参数恢复登录状态和房间状态（完全依赖URL参数，不依赖JavaScript）
    # 登录成功后，session_token和username会保存在URL中，刷新页面后可以从URL恢复
    query_params = st.query_params
    
    # 从URL参数恢复登录状态
    if "session_token" in query_params and "username" in query_params:
        if not st.session_state.get("session_token"):
            st.session_state.session_token = query_params["session_token"]
        if not st.session_state.get("username"):
            st.session_state.username = query_params["username"]
        # 不清除URL参数，保持登录状态（这样刷新后仍然能恢复）
    
    # 从URL参数恢复房间状态
    if "room_id" in query_params:
        room_id_from_url = query_params["room_id"]
        # 如果session_state中没有房间ID，或者URL中的房间ID不同，尝试恢复
        if not st.session_state.get("room_id") or st.session_state.get("room_id") != room_id_from_url:
            room_manager = get_room_manager()
            room_data = room_manager.get_room(room_id_from_url)
            current_username = st.session_state.get("username")
            
            if room_data and current_username:
                # 检查用户是否仍在房间的参与者列表中
                participants = room_data.get("participants", [])
                participant_names = [p.get("username", "") if isinstance(p, dict) else p for p in participants]
                
                if current_username in participant_names:
                    # 用户仍在房间中，恢复房间状态
                    st.session_state.room_id = room_id_from_url
                    st.session_state._temp_room_language = room_data.get("room_language", "zh")
                    st.session_state.participants = participants
                    st.session_state.meeting_messages = room_data.get("messages", [])
                else:
                    # 用户不在房间中，清除URL参数中的房间ID
                    st.query_params.update(room_id=None)
            elif not room_data:
                # 房间不存在，清除URL参数中的房间ID
                st.query_params.update(room_id=None)
                if st.session_state.get("room_id") == room_id_from_url:
                    st.session_state.room_id = None
                    st.warning("⚠️ 房间已被删除")
    
    # 检查登录状态
    # 如果session_state中有session_token和username，验证它们
    if st.session_state.get("session_token") and st.session_state.get("username"):
        # 验证session token
        from ..services.auth_service import get_auth_service
        auth_service = get_auth_service()
        session_token = st.session_state.get("session_token")
        username = st.session_state.get("username")
        valid, validated_username = auth_service.validate_session(session_token)
        if valid and validated_username == username:
            # Session有效，设置登录状态
            st.session_state.logged_in = True
            # 如果是从URL参数恢复的，清除URL参数（避免重复恢复）
            query_params = st.query_params
            if query_params and any(k.startswith('restore_') for k in query_params.keys()):
                clear_params = {k: None for k in query_params.keys() if k.startswith('restore_')}
                if clear_params:
                    st.query_params.update(**clear_params)
        else:
            # Session无效，清除登录状态
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.session_token = None
    elif st.session_state.get("logged_in", False):
        # 如果没有session_token或username，但有logged_in标志，清除登录状态
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.session_token = None
    
    # 如果未登录，显示登录页面
    if not st.session_state.get("logged_in", False):
        render_login_page()
        return
    
    # 已登录，显示会议应用
    current_username = st.session_state.get("username")
    
    # 如果用户在房间中，验证用户是否仍在房间中
    if st.session_state.get("room_id"):
        room_manager = get_room_manager()
        current_room_id = st.session_state.get("room_id")
        
        if current_room_id:
            room_data = room_manager.get_room(current_room_id)
            if room_data:
                # 检查用户是否仍在参与者列表中
                participants = room_data.get("participants", [])
                participant_names = [p.get("username", "") if isinstance(p, dict) else p for p in participants]
                if current_username not in participant_names:
                    # 用户不在参与者列表中，清除房间状态
                    st.session_state.room_id = None
                    st.warning(f"⚠️ 您已不在房间 **{current_room_id}** 中，请重新加入")
            else:
                # 房间不存在（可能被自动删除）
                st.session_state.room_id = None
                st.warning("⚠️ 房间已被删除")
    
    st.title("💬 多人会议聊天室")
    st.markdown("""
    **智能会议聊天室** - 支持语音输入、自动翻译、多人聊天
    - 🎤 **语音输入**：通过麦克风说话，自动转换为文字
    - 🌐 **自动翻译**：根据会议室语言自动翻译消息
    - 👥 **多人聊天**：支持多个参与者同时聊天
    - 📝 **文字输入**：也可以直接打字输入
    """)
    st.markdown("---")
    
    _render_sidebar()
    _render_main_content()
    
    # 自动保存状态到localStorage
    auto_save_state()


def _render_sidebar():
    """渲染侧边栏"""
    room_manager = get_room_manager()
    
    with st.sidebar:
        st.header("🏠 房间管理")
        
        # 房间列表（实时更新）
        st.subheader("📋 房间列表")
        # 每次渲染时都重新获取房间列表，确保看到最新创建的房间
        rooms = room_manager.list_rooms()
        
        # 显示房间数量提示
        if rooms:
            st.caption(f"📊 共有 {len(rooms)} 个房间")
        else:
            st.caption("📊 暂无房间")
        
        if rooms:
            # 创建房间选择器
            room_options = [f"{room['room_id']} ({room['participant_count']}人)" for room in rooms]
            selected_room_idx = st.selectbox(
                "选择房间",
                options=range(len(room_options)),
                format_func=lambda x: room_options[x] if x < len(room_options) else "",
                key="room_list_select"
            )
            
            if selected_room_idx is not None and selected_room_idx < len(rooms):
                selected_room = rooms[selected_room_idx]
                st.caption(f"创建者: {selected_room['creator']} | 语言: {'中文' if selected_room['room_language'] == 'zh' else 'English'}")
                
                # 加入选中房间按钮
                current_username = st.session_state.get("username")
                current_room_id = st.session_state.get("room_id")
                
                # 只在用户不在任何房间中时显示加入按钮
                if not current_room_id and current_username:
                    if st.button("加入房间", key="join_selected_room", use_container_width=True, type="primary"):
                        # 检查用户名是否可用
                        available, check_error = room_manager.check_username_available(selected_room['room_id'], current_username)
                        if not available:
                            st.error(f"❌ {check_error}")
                        else:
                            # 加入房间
                            user_language = st.session_state.get("_temp_room_language") or st.session_state.get("room_language", "zh")
                            success, join_error = room_manager.join_room(selected_room['room_id'], current_username, user_language=user_language)
                            if success:
                                st.session_state.room_id = selected_room['room_id']
                                # 将房间ID保存到URL参数，确保刷新后能恢复
                                st.query_params.update(room_id=selected_room['room_id'])
                                room_data = room_manager.get_room(selected_room['room_id'])
                                if room_data:
                                    st.session_state._temp_room_language = room_data.get("room_language", "zh")
                                    st.session_state.participants = room_data.get("participants", [])
                                    st.session_state.meeting_messages = room_data.get("messages", [])
                                st.success(f"✅ 已加入房间 **{selected_room['room_id']}**")
                                st.rerun()
                            else:
                                st.error(f"❌ {join_error or '加入房间失败'}")
                elif current_room_id and current_username:
                    # 用户已在某个房间中，显示提示
                    if current_room_id == selected_room['room_id']:
                        st.info(f"✅ 您当前在此房间中")
                    else:
                        st.info(f"ℹ️ 您已在其他房间中，请先退出当前房间")
        else:
            st.info("暂无可用房间")
        
        # 检查用户是否已在房间中
        current_room_id = st.session_state.get("room_id")
        
        # 如果用户不在房间中，显示创建或加入房间的选项
        if not current_room_id:
            st.markdown("---")
            # 房间ID输入（手动创建或加入）
            st.subheader("➕ 创建或加入房间")
            room_id_input = st.text_input(
                "房间ID",
                value="",
                placeholder="输入房间ID或创建新房间",
                key="room_id_input"
            )
            
            # 智能创建或加入按钮
            if st.button("🚀 创建或加入房间", key="create_or_join_room", use_container_width=True, type="primary"):
                if room_id_input:
                    current_username = st.session_state.get("username")
                    if not current_username:
                        st.warning("⚠️ 请先登录")
                    else:
                        # 获取当前语言设置（优先使用临时变量）
                        room_language = st.session_state.get("_temp_room_language") or st.session_state.get("room_language", "zh")
                        user_language = st.session_state.get("_temp_room_language") or st.session_state.get("room_language", "zh")
                        
                        # 尝试创建房间
                        created, status, error_msg = room_manager.create_room(room_id_input, room_language, creator_username=current_username, creator_user_language=user_language)
                        
                        if created:
                            # 房间创建成功
                            st.session_state.room_id = room_id_input
                            # 将房间ID保存到URL参数，确保刷新后能恢复
                            st.query_params.update(room_id=room_id_input)
                            room_data = room_manager.get_room(room_id_input)
                            if room_data:
                                st.session_state._temp_room_language = room_data.get("room_language", "zh")
                                st.session_state.participants = room_data.get("participants", [])
                                st.session_state.meeting_messages = room_data.get("messages", [])
                            st.success(f"✅ 房间 **{room_id_input}** 创建成功！您已自动加入房间。")
                            st.rerun()
                        elif status == "already_member":
                            # 用户已在该房间中，直接加载房间数据
                            st.session_state.room_id = room_id_input
                            # 将房间ID保存到URL参数，确保刷新后能恢复
                            st.query_params.update(room_id=room_id_input)
                            room_data = room_manager.get_room(room_id_input)
                            if room_data:
                                st.session_state._temp_room_language = room_data.get("room_language", "zh")
                                st.session_state.participants = room_data.get("participants", [])
                                st.session_state.meeting_messages = room_data.get("messages", [])
                            st.info(f"ℹ️ 您已在房间 **{room_id_input}** 中")
                            st.rerun()
                        elif status == "exists":
                            # 房间已存在，先检查用户名是否可用
                            available, check_error = room_manager.check_username_available(room_id_input, current_username)
                            if not available:
                                st.error(f"❌ {check_error}")
                                st.info("💡 该房间中已存在同名用户，无法加入")
                            else:
                                # 用户名可用，尝试加入
                                user_language = st.session_state.get("_temp_room_language") or st.session_state.get("room_language", "zh")
                                success, join_error = room_manager.join_room(room_id_input, current_username, user_language=user_language)
                                if success:
                                    st.session_state.room_id = room_id_input
                                    # 将房间ID保存到URL参数，确保刷新后能恢复
                                    st.query_params.update(room_id=room_id_input)
                                    room_data = room_manager.get_room(room_id_input)
                                    if room_data:
                                        st.session_state._temp_room_language = room_data.get("room_language", "zh")
                                        st.session_state.participants = room_data.get("participants", [])
                                        st.session_state.meeting_messages = room_data.get("messages", [])
                                    st.success(f"✅ 房间 **{room_id_input}** 已存在，您已成功加入！")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {join_error or '加入房间失败'}")
                        else:
                            st.error(f"❌ {error_msg or '操作失败'}")
                else:
                    st.warning("⚠️ 请输入房间ID")
        
        # 退出房间按钮（如果用户在房间中，显示退出按钮）
        if current_room_id:
            st.markdown("---")
            if st.button("🚪 退出房间", key="leave_room", use_container_width=True, type="secondary"):
                current_username = st.session_state.get("username")
                if current_username and room_manager.leave_room(current_room_id, current_username):
                    st.session_state.room_id = None
                    st.session_state.meeting_messages = []
                    st.session_state.participants = []
                    if "_temp_room_language" in st.session_state:
                        del st.session_state._temp_room_language
                    # 清除URL参数中的房间ID
                    st.query_params.update(room_id=None)
                    # 清除localStorage中的房间ID
                    from .state_persistence import clear_room_state
                    clear_room_state()
                    st.success("已退出房间")
                    st.rerun()
                else:
                    st.error("退出房间失败")
        
        # 显示当前房间信息
        current_room_id = st.session_state.get("room_id")
        if current_room_id:
            st.markdown("---")
            st.success(f"✅ 当前房间: **{current_room_id}**")
            
            # 显示房间信息
            room_data = room_manager.get_room(current_room_id)
            if room_data:
                st.caption(f"创建时间: {room_data.get('created_at', 'N/A')[:19]}")
        
        st.markdown("---")
        st.header("⚙️ 会议室设置")
        
        # 显示当前登录用户和登出按钮
        current_username = st.session_state.get("username")
        if current_username:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"👤 当前用户: **{current_username}**")
            with col2:
                if st.button("注销", key="logout_button", use_container_width=True, type="secondary"):
                    # 如果用户在房间中，先退出房间
                    current_room_id = st.session_state.get("room_id")
                    if current_room_id and current_username:
                        room_manager.leave_room(current_room_id, current_username)
                    
                    # 执行注销
                    from .auth_ui import logout
                    logout()
                    
                    # 清除房间相关状态
                    st.session_state.room_id = None
                    st.session_state.meeting_messages = []
                    st.session_state.participants = []
                    if "_temp_room_language" in st.session_state:
                        del st.session_state._temp_room_language
                    # 清除URL参数中的房间ID
                    st.query_params.update(room_id=None)
                    
                    st.success("已注销并退出聊天室")
                    st.rerun()
        
        # 初始化用户语言（如果不存在）
        if "room_language" not in st.session_state:
            st.session_state.room_language = "zh"
        
        # 如果已加入房间，从房间数据加载当前用户的语言
        if current_room_id:
            room_data = room_manager.get_room(current_room_id)
            if room_data:
                participants = room_data.get("participants", [])
                # 兼容旧格式
                if participants and isinstance(participants[0], str):
                    participants = [{"username": p, "user_language": room_data.get("room_language", "zh")} for p in participants]
                
                # 查找当前用户的语言设置
                current_username = st.session_state.get("username")
                for p in participants:
                    if isinstance(p, dict) and p.get("username") == current_username:
                        user_lang = p.get("user_language", "zh")
                        st.session_state._temp_room_language = user_lang
                        st.session_state.room_language = user_lang
                        break
        
        # 我的显示语言设置
        current_lang = st.session_state.get("_temp_room_language", st.session_state.get("room_language", get_user_language()))
        user_language = st.selectbox(
            t("my_display_language"),
            ["zh", "en"],
            format_func=lambda x: t("chinese") if x == "zh" else t("english"),
            index=0 if current_lang == "zh" else 1,
            key="user_language"
        )
        # 更新用户语言设置
        set_user_language(user_language)
        
        # 如果用户已加入房间，更新参与者的语言设置
        if current_room_id and user_language != current_lang:
            current_username = st.session_state.get("username")
            if current_username:
                room_manager.update_participant_language(current_room_id, current_username, user_language)
            st.session_state._temp_room_language = user_language
            st.session_state.room_language = user_language
        
        st.markdown("---")
        st.subheader("👥 参与者列表")
        
        # 显示参与者列表（每次渲染时都从最新房间数据获取，确保看到新加入的参与者）
        if current_room_id:
            # 每次都重新获取房间数据，确保获取最新的参与者列表
            room_data = room_manager.get_room(current_room_id)
            if room_data:
                # 从房间数据中获取最新的参与者列表
                participants = room_data.get("participants", [])
                # 兼容旧格式
                if participants and isinstance(participants[0], str):
                    participants = [{"username": p, "user_language": room_data.get("room_language", "zh")} for p in participants]
                
                # 更新 session_state 中的参与者列表（用于其他地方）
                st.session_state.participants = participants
                
                room_default_lang = room_data.get("room_language", "zh")
                creator = room_data.get("creator")  # 获取创建者（管理员）
                current_username = st.session_state.get("username")
                is_admin = room_manager.is_creator(current_room_id, current_username) if current_username else False
                
                # 显示参与者数量
                participant_count = len(participants)
                st.caption(f"👥 共 {participant_count} 人")
                
                if not participants:
                    st.info("暂无参与者")
                else:
                    # 兼容旧格式和新格式
                    for idx, participant in enumerate(participants):
                        if isinstance(participant, dict):
                            username = participant.get("username", "未知用户")
                            lang = participant.get("user_language") or room_default_lang
                            lang_name = "中文" if lang == "zh" else "English"
                            
                            # 检查是否是管理员（创建者）
                            is_creator = username == creator
                            admin_badge = " 👑 管理员" if is_creator else ""
                            
                            # 创建列布局：用户名和移除按钮
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**{username}**{admin_badge} - 🌐 {lang_name}")
                            
                            with col2:
                                # 只有管理员才能看到移除按钮，且不能移除自己
                                if is_admin and username != current_username:
                                    if st.button("移除", key=f"remove_{username}_{idx}", use_container_width=True, type="secondary"):
                                        success, error_msg = room_manager.remove_participant(current_room_id, username, current_username)
                                        if success:
                                            # 添加系统消息，通知其他参与者
                                            leave_time = datetime.now()
                                            time_str = leave_time.strftime("%H:%M:%S")
                                            system_message = {
                                                "type": "system",
                                                "event": "user_removed",
                                                "username": username,
                                                "admin_username": current_username,
                                                "timestamp": leave_time.isoformat(),
                                                "time_str": time_str
                                            }
                                            room_data = room_manager.get_room(current_room_id)
                                            if room_data:
                                                room_data["messages"].append(system_message)
                                                room_data["last_activity"] = leave_time.isoformat()
                                                # 保存房间数据
                                                room_file = room_manager._get_room_file(current_room_id)
                                                with room_manager.lock:
                                                    import json
                                                    with open(room_file, 'w', encoding='utf-8') as f:
                                                        json.dump(room_data, f, ensure_ascii=False, indent=2)
                                            st.success(f"✅ 已移除参与者 **{username}**")
                                            st.rerun()
                                        else:
                                            st.error(f"❌ {error_msg or '移除失败'}")
                        else:
                            # 旧格式（字符串），使用房间默认语言
                            username = participant
                            lang_name = "中文" if room_default_lang == "zh" else "English"
                            is_creator = username == creator
                            admin_badge = " 👑 管理员" if is_creator else ""
                            
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**{username}**{admin_badge} - 🌐 {lang_name}")
                            
                            with col2:
                                if is_admin and username != current_username:
                                    if st.button("移除", key=f"remove_old_{username}_{idx}", use_container_width=True, type="secondary"):
                                        success, error_msg = room_manager.remove_participant(current_room_id, username, current_username)
                                        if success:
                                            # 添加系统消息
                                            leave_time = datetime.now()
                                            time_str = leave_time.strftime("%H:%M:%S")
                                            system_message = {
                                                "type": "system",
                                                "event": "user_removed",
                                                "username": username,
                                                "admin_username": current_username,
                                                "timestamp": leave_time.isoformat(),
                                                "time_str": time_str
                                            }
                                            room_data = room_manager.get_room(current_room_id)
                                            if room_data:
                                                room_data["messages"].append(system_message)
                                                room_data["last_activity"] = leave_time.isoformat()
                                                room_file = room_manager._get_room_file(current_room_id)
                                                with room_manager.lock:
                                                    import json
                                                    with open(room_file, 'w', encoding='utf-8') as f:
                                                        json.dump(room_data, f, ensure_ascii=False, indent=2)
                                            st.success(f"✅ 已移除参与者 **{username}**")
                                            st.rerun()
                                        else:
                                            st.error(f"❌ {error_msg or '移除失败'}")
        else:
            st.info("请先创建或加入房间")
        
        st.markdown("---")
        st.subheader("ℹ️ 使用说明")
        st.markdown("""
        1. **创建/加入房间**：
           - 输入房间ID，点击"创建房间"创建新房间
           - 或输入已有房间ID，点击"加入房间"加入
           - 将房间ID分享给其他人即可一起聊天
        
        2. **输入方式**：
           - 🎤 点击麦克风按钮进行语音输入
           - ⌨️ 在输入框直接打字
        
        3. **自动翻译**：如果您的输入语言与会议室语言不同，会自动翻译
        
        4. **多人聊天**：所有加入同一房间的用户都可以看到彼此的消息
        """)
        
        # 自动刷新开关
        st.markdown("---")
        # 初始化 auto_refresh（如果不存在）
        if "auto_refresh" not in st.session_state:
            st.session_state.auto_refresh = True
        
        auto_refresh = st.checkbox("🔄 自动刷新（每2秒）", value=st.session_state.auto_refresh, key="auto_refresh")
        if auto_refresh:
            st.caption("💡 开启后会自动刷新页面，及时看到新创建的房间、新消息和新参与者")
        else:
            st.caption("⚠️ 关闭后需要手动刷新页面才能看到新房间和新参与者")


def _render_main_content():
    """渲染主内容区域"""
    room_manager = get_room_manager()
    current_room_id = st.session_state.get("room_id")
    
    # 如果已加入房间，从房间加载消息（每次渲染都重新加载，确保看到最新消息）
    if current_room_id:
        # 每次都重新获取房间数据，确保获取最新消息
        room_data = room_manager.get_room(current_room_id)
        if room_data:
            # 同步消息（从房间数据获取最新消息）
            room_messages = room_data.get("messages", [])
            # 直接使用房间中的最新消息，不依赖session_state缓存
            st.session_state.meeting_messages = room_messages
            # 使用临时变量存储房间语言，避免与widget冲突
            st.session_state._temp_room_language = room_data.get("room_language", "zh")
            # 同步参与者列表（从房间数据获取最新列表）
            participants = room_data.get("participants", [])
            # 兼容旧格式
            if participants and isinstance(participants[0], str):
                participants = [{"username": p, "user_language": room_data.get("room_language", "zh")} for p in participants]
            st.session_state.participants = participants
            # 确保房间语言同步到session_state（用于持久化）
            if "room_language" not in st.session_state or st.session_state.room_language != room_data.get("room_language", "zh"):
                st.session_state.room_language = room_data.get("room_language", "zh")
        else:
            # 房间不存在，清除状态
            st.session_state.room_id = None
            st.warning("⚠️ 房间不存在，请重新创建或加入房间")
            return
    else:
        # 未加入房间，显示提示
        st.warning("⚠️ 请先创建或加入房间才能开始聊天")
        return
    
    # 显示聊天消息
    _render_chat_messages()
    
    st.markdown("---")
    
    # 显示消息发送状态（放在显眼位置）
    message_status = st.session_state.get("_last_message_status")
    if message_status == "success":
        st.success("✅ 消息已发送！")
        # 清除状态（在显示后立即清除，避免重复显示）
        if "_last_message_status" in st.session_state:
            del st.session_state._last_message_status
    elif message_status == "error":
        error_msg = st.session_state.get("_last_message_error", "消息发送失败")
        st.error(f"❌ {error_msg}")
        # 清除状态
        if "_last_message_status" in st.session_state:
            del st.session_state._last_message_status
        if "_last_message_error" in st.session_state:
            del st.session_state._last_message_error
    elif message_status == "warning":
        st.warning("⚠️ 消息处理完成，但未生成消息内容")
        # 清除状态
        if "_last_message_status" in st.session_state:
            del st.session_state._last_message_status
    
    # 输入区域
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # 如果消息已发送，清空输入框
        if st.session_state.get("_clear_input", False):
            user_input = st.text_input(
                "输入消息...",
                key="user_input",
                value="",  # 清空输入框
                placeholder="输入消息或使用麦克风..."
            )
            del st.session_state._clear_input
        else:
        user_input = st.text_input(
            t("input_message"),
            key="user_input",
            placeholder=t("input_message")
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # 垂直对齐
        send_text = st.button(t("send_text"), key="send_text", use_container_width=True)
    
    # 语音输入
    st.markdown(f"### 🎤 {t('voice_input')}")
    audio_data = st.audio_input(t("voice_input"), key="audio_input")
    send_audio = st.button(t("send_audio"), key="send_audio")
    
    # 处理输入
    if send_text and user_input:
        # 标记消息已发送，延迟自动刷新
        st.session_state._message_sent = True
        st.session_state._message_sent_time = time.time()
        # 标记需要清空输入框
        st.session_state._clear_input = True
        _process_text_input(user_input)
        st.rerun()
    
    if send_audio and audio_data:
        # 标记消息已发送，延迟自动刷新
        st.session_state._message_sent = True
        st.session_state._message_sent_time = time.time()
        _process_audio_input(audio_data)
        st.rerun()
    
    # 自动刷新提示和实现（智能刷新：用户发送消息后延迟刷新）
    if st.session_state.get("auto_refresh", True):
        refresh_interval = 3000  # 默认3秒
        # 如果用户刚发送了消息，延迟刷新（给用户时间看到成功提示）
        if st.session_state.get("_message_sent", False):
            elapsed = time.time() - st.session_state.get("_message_sent_time", 0)
            if elapsed < 1.5:  # 消息发送后1.5秒内不刷新
                refresh_interval = 1500 - int(elapsed * 1000) + 2000  # 延迟到1.5秒后，再加2秒
            else:
                # 超过1.5秒，清除标记，恢复正常刷新
                del st.session_state._message_sent
                del st.session_state._message_sent_time
        
        st.caption(f"🔄 自动刷新已开启，页面将每{refresh_interval//1000}秒自动更新以接收新消息、新房间和新参与者")
        # 使用setTimeout实现刷新（每次刷新后重新设置，避免累积）
        st.markdown(f"""
        <script>
        (function() {{
            // 只在页面加载时设置一次刷新，避免重复设置
            if (!window._refreshScheduled) {{
                window._refreshScheduled = true;
                setTimeout(function(){{
                    window.location.reload();
                }}, {refresh_interval});
            }}
        }})();
        </script>
        """, unsafe_allow_html=True)
    else:
        st.caption("ℹ️ 自动刷新已关闭，新房间、新消息和新参与者可能不会及时显示")


def _render_chat_messages():
    """渲染聊天消息"""
    st.subheader("💬 聊天记录")
    st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)  # 增加间距
    
    # 创建聊天容器
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.meeting_messages:
            st.info("还没有消息，开始聊天吧！")
        else:
            # 显示所有消息
            for msg in st.session_state.meeting_messages:
                _render_message(msg)


def _render_message(msg: dict):
    """渲染单条消息"""
    # 检查是否是系统消息
    if msg.get("type") == "system":
        event = msg.get("event")
        if event == "user_joined":
            username = msg.get("username", "未知用户")
            time_str = msg.get("time_str", "")
            # 显示系统消息（居中，灰色，小字）- 专业风格
            import html
            username_escaped = html.escape(username)
            st.markdown(f"""
            <div style="text-align: center; color: #6c757d; font-size: 0.75em; padding: 4px 0; margin: 8px 0;">
                <span style="background-color: #e9ecef; padding: 4px 12px; border-radius: 12px; display: inline-block;">
                    👤 <strong>{username_escaped}</strong> 加入了房间 <span style="color: #868e96;">({time_str})</span>
                </span>
            </div>
            """, unsafe_allow_html=True)
        elif event == "user_removed":
            username = msg.get("username", "未知用户")
            admin_username = msg.get("admin_username", "管理员")
            time_str = msg.get("time_str", "")
            # 显示系统消息（居中，灰色，小字）- 专业风格
            import html
            username_escaped = html.escape(username)
            admin_username_escaped = html.escape(admin_username)
            st.markdown(f"""
            <div style="text-align: center; color: #6c757d; font-size: 0.75em; padding: 4px 0; margin: 8px 0;">
                <span style="background-color: #fff3cd; padding: 4px 12px; border-radius: 12px; display: inline-block;">
                    🚪 <strong>{username_escaped}</strong> 被管理员 <strong>{admin_username_escaped}</strong> 移出房间 <span style="color: #868e96;">({time_str})</span>
                </span>
            </div>
            """, unsafe_allow_html=True)
        return  # 系统消息渲染完毕，直接返回
    
    user = msg.get("user", "未知用户")
    original_text = msg.get("original_text", msg.get("content", ""))  # 兼容旧格式
    translated_text = msg.get("translated_text")  # 这是房间语言的翻译
    original_lang = msg.get("original_lang")
    is_current_user = user == st.session_state.get("username", "")
    
    # 获取发送者的语言（从参与者列表中查找）
    sender_language = None
    current_room_id = st.session_state.get("room_id")
    room_manager = None
    room_data = None
    
    if current_room_id:
        from ..services.room_manager import get_room_manager
        room_manager = get_room_manager()
        room_data = room_manager.get_room(current_room_id)
        if room_data:
            participants = room_data.get("participants", [])
            # 兼容旧格式
            if participants and isinstance(participants[0], str):
                participants = [{"username": p, "user_language": room_data.get("room_language", "zh")} for p in participants]
            
            for p in participants:
                if isinstance(p, dict) and p.get("username") == user:
                    sender_language = p.get("user_language") or room_data.get("room_language", "zh")
                    break
                elif isinstance(p, str) and p == user:
                    sender_language = room_data.get("room_language", "zh")
                    break
    
    # 如果没有找到，使用房间默认语言
    if sender_language is None:
        if room_data:
            sender_language = room_data.get("room_language", "zh")
        else:
            sender_language = "zh"  # 默认中文
    
    # 显示用户名和语言
    lang_name = "中文" if sender_language == "zh" else "English"
    user_display = f"{user} ({lang_name})"
    
    # 获取当前用户选择的语言
    user_language = st.session_state.get("_temp_room_language") or st.session_state.get("room_language", "zh")
    
    # 确定要显示的内容
    # 如果原始语言与用户语言不同，需要显示原始+翻译
    if original_lang and original_lang != user_language:
        # 需要翻译到用户选择的语言
        from ..services.translation import TranslationService
        translation_service = TranslationService()
        
        # 如果已经有房间语言的翻译，且房间语言就是用户语言，直接使用
        if translated_text and user_language == (st.session_state.get("_temp_room_language") or st.session_state.get("room_language", "zh")):
            user_translated_text = translated_text
        else:
            # 需要翻译到用户选择的语言
            try:
                user_translated_text = translation_service.translate(
                    original_text,
                    source_lang=original_lang,
                    target_lang=user_language
                )
            except:
                user_translated_text = original_text
        
        # 显示原始语言和翻译（原始在上，翻译在下）
        # 转义HTML特殊字符，避免XSS和显示问题
        import html
        original_text_escaped = html.escape(str(original_text))
        user_translated_text_escaped = html.escape(str(user_translated_text))
        # 构建HTML内容，确保结构正确
        original_html = f'<div style="border-bottom: 1px solid rgba(0,0,0,0.1); padding-bottom: 4px; margin-bottom: 4px; font-style: italic; opacity: 0.7; font-size: 0.85em; color: #666;">{original_text_escaped}</div>'
        translated_html = f'<div style="font-weight: 500; font-size: 0.95em;">{user_translated_text_escaped}</div>'
        display_content_html = original_html + translated_html
    else:
        # 原始语言与用户语言相同，只显示原始文本
        # 转义HTML特殊字符
        import html
        display_content_html = html.escape(str(original_text))
    
    # 转义用户名显示
    import html
    user_display_escaped = html.escape(user_display)
    
    # 根据是否是当前用户决定显示位置
    if is_current_user:
        # 当前用户的消息显示在右侧（专业风格：蓝色气泡）
        st.markdown(f"""
        <div style="text-align: right; margin: 8px 0;">
            <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 8px 12px; border-radius: 12px; max-width: 70%; text-align: left; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="font-size: 0.75em; opacity: 0.9; margin-bottom: 4px; font-weight: 500;">{user_display_escaped}</div>
                <div style="font-size: 0.9em; line-height: 1.4; word-wrap: break-word;">{display_content_html}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 其他用户的消息显示在左侧（专业风格：灰色气泡）
        st.markdown(f"""
        <div style="text-align: left; margin: 8px 0;">
            <div style="display: inline-block; background: #f1f3f5; color: #212529; padding: 8px 12px; border-radius: 12px; max-width: 70%; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <div style="font-size: 0.75em; color: #6c757d; margin-bottom: 4px; font-weight: 500;">{user_display_escaped}</div>
                <div style="font-size: 0.9em; line-height: 1.4; word-wrap: break-word;">{display_content_html}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _process_text_input(text: str):
    """处理文字输入"""
    if not text.strip():
        st.session_state._last_message_status = "error"
        st.session_state._last_message_error = t("error_empty_message")
        return
    
    room_manager = get_room_manager()
    current_room_id = st.session_state.get("room_id")
    
    if not current_room_id:
        st.session_state._last_message_status = "error"
        st.session_state._last_message_error = t("error_not_in_room")
        return
    
    # 获取房间语言（优先使用临时变量，避免与widget冲突）
    room_language = st.session_state.get("_temp_room_language") or st.session_state.get("room_language", "zh")
    current_username = st.session_state.get("username", "")
    
    if not current_username:
        st.session_state._last_message_status = "error"
        st.session_state._last_message_error = t("error_not_logged_in")
        return
    
    # 初始化工作流状态
    initial_state: MeetingState = {
        "messages": [],
        "room_language": room_language,
        "current_user": current_username,
        "audio_data": None,
        "original_text": text,
        "translated_text": None,
        "participants": st.session_state.get("participants", [current_username] if current_username else [])
    }
    
    # 执行工作流
    app = get_meeting_app()
    config = {
        "configurable": {"thread_id": f"room_{current_room_id}"}
    }
    
    try:
        # 执行工作流
        final_state = app.invoke(initial_state, config)
        
        # 获取处理后的消息
        messages = final_state.get("messages", [])
        if messages:
            last_message = messages[-1]
            content = last_message.content
            
            # 解析消息内容（格式：用户名: 原始文本 | 翻译文本 | 原始语言）
            if ":" in content:
                parts = content.split(":", 1)
                user = parts[0].strip()
                msg_parts = parts[1].strip().split(" | ")
                original_text = msg_parts[0].strip() if len(msg_parts) > 0 else ""
                translated_text = msg_parts[1].strip() if len(msg_parts) > 1 and msg_parts[1] else None
                original_lang = msg_parts[2].strip() if len(msg_parts) > 2 else None
            else:
                user = current_username
                original_text = content
                translated_text = None
                original_lang = None
            
            # 如果解析后的原始文本为空，使用原始输入
            if not original_text:
                original_text = text
            
            # 添加到房间（保存原始文本和翻译文本）
            success = room_manager.add_message(
                current_room_id, 
                user, 
                original_text, 
                translated_text=translated_text,
                original_lang=original_lang
            )
            
            if success:
                # 更新本地消息
                st.session_state.meeting_messages.append({
                    "user": user,
                    "original_text": original_text,
                    "translated_text": translated_text,
                    "original_lang": original_lang
                })
                # 显示成功提示（会在rerun后显示）
                st.session_state._last_message_status = "success"
            else:
                st.session_state._last_message_status = "error"
                st.session_state._last_message_error = "消息保存失败"
        else:
            # 如果没有消息返回，直接保存原始文本
            success = room_manager.add_message(
                current_room_id,
                current_username,
                text,
                translated_text=None,
                original_lang=None
            )
            if success:
                st.session_state.meeting_messages.append({
                    "user": current_username,
                    "original_text": text,
                    "translated_text": None,
                    "original_lang": None
                })
                st.session_state._last_message_status = "success"
            else:
                st.session_state._last_message_status = "error"
                st.session_state._last_message_error = "消息保存失败"
    except Exception as e:
        st.session_state._last_message_status = "error"
        st.session_state._last_message_error = f"处理消息时出错: {str(e)}"
        import traceback
        st.exception(e)


def _process_audio_input(audio_data):
    """处理语音输入"""
    room_manager = get_room_manager()
    current_room_id = st.session_state.get("room_id")
    
    if not current_room_id:
        st.error("请先创建或加入房间")
        return
    
    # 获取房间语言（优先使用临时变量，避免与widget冲突）
    room_language = st.session_state.get("_temp_room_language") or st.session_state.get("room_language", "zh")
    current_username = st.session_state.get("username", "")
    
    try:
        # 将音频数据转换为base64
        audio_bytes = audio_data.read()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # 初始化工作流状态
        initial_state: MeetingState = {
            "messages": [],
            "room_language": room_language,
            "current_user": current_username,
            "audio_data": audio_base64,
            "original_text": None,
            "translated_text": None,
            "participants": st.session_state.get("participants", [current_username] if current_username else [])
        }
        
        # 执行工作流
        app = get_meeting_app()
        config = {
            "configurable": {"thread_id": f"room_{current_room_id}"}
        }
        
        # 执行工作流
        final_state = app.invoke(initial_state, config)
        
        # 获取处理后的消息
        messages = final_state.get("messages", [])
        if messages:
            last_message = messages[-1]
            content = last_message.content
            
            # 解析消息内容（格式：用户名: 原始文本 | 翻译文本 | 原始语言）
            if ":" in content:
                parts = content.split(":", 1)
                user = parts[0].strip()
                msg_parts = parts[1].strip().split(" | ")
                original_text = msg_parts[0].strip() if len(msg_parts) > 0 else ""
                translated_text = msg_parts[1].strip() if len(msg_parts) > 1 and msg_parts[1] else None
                original_lang = msg_parts[2].strip() if len(msg_parts) > 2 else None
            else:
                user = current_username
                original_text = content
                translated_text = None
                original_lang = None
            
            # 添加到房间（保存原始文本和翻译文本）
            room_manager.add_message(
                current_room_id, 
                user, 
                original_text, 
                translated_text=translated_text,
                original_lang=original_lang
            )
            
            # 更新本地消息
            st.session_state.meeting_messages.append({
                "user": user,
                "original_text": original_text,
                "translated_text": translated_text,
                "original_lang": original_lang
            })
            
            st.success("语音识别成功！")
    except Exception as e:
        st.error(f"处理语音时出错: {str(e)}")
        st.exception(e)
