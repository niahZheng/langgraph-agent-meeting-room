"""状态持久化工具 - 使用浏览器localStorage保存用户状态"""

import json
import streamlit as st
import streamlit.components.v1 as components


def init_state_restoration():
    """初始化状态恢复 - 在页面加载时从localStorage恢复状态"""
    # 只在第一次运行时执行
    if "_state_restored" not in st.session_state:
        st.session_state._state_restored = True
        
        # 从URL参数恢复状态（如果存在，说明是第一次恢复）
        query_params = st.query_params
        restored_from_url = False
        
        for key, value in query_params.items():
            if key.startswith('restore_'):
                state_key = key.replace('restore_', '')
                # 只在session_state中没有该键或值为空时才恢复
                if state_key not in st.session_state or not st.session_state[state_key]:
                    # URL参数会自动解码，直接使用
                    st.session_state[state_key] = value
                    restored_from_url = True
        
        # 如果从URL恢复了状态，不清除URL参数（让meeting_app.py处理）
        if restored_from_url:
            return True
        
        # 如果没有URL参数，尝试从localStorage恢复（通过JavaScript触发）
        # 检查哪些状态需要恢复（包括登录状态）
        needs_restore = {
            "room_id": st.session_state.get("room_id") is None or st.session_state.get("room_id") == "",
            "username": not st.session_state.get("logged_in", False) or st.session_state.get("username") is None,
            "session_token": not st.session_state.get("logged_in", False) or st.session_state.get("session_token") is None,
            "user_language": st.session_state.get("user_language") is None,
            "room_language": st.session_state.get("room_language") is None,
            "auto_refresh": st.session_state.get("auto_refresh") is None
        }
        
        if any(needs_restore.values()):
            # 使用components.html确保JavaScript在页面加载时立即执行
            try:
                html = """
                <script>
                (function() {
                    try {
                        console.log('[状态恢复] 开始检查 localStorage...');
                        const stateJson = localStorage.getItem('meeting_app_state');
                        if (stateJson) {
                            console.log('[状态恢复] 找到 localStorage 数据:', stateJson);
                            const state = JSON.parse(stateJson);
                            const urlParams = new URLSearchParams(window.location.search);
                            let needsReload = false;
                            
                            // 检查需要恢复的状态（包括登录状态）
                            if (!urlParams.has('restore_room_id') && state.room_id) {
                                urlParams.set('restore_room_id', encodeURIComponent(state.room_id));
                                needsReload = true;
                                console.log('[状态恢复] 需要恢复 room_id:', state.room_id);
                            }
                            if (!urlParams.has('restore_username') && state.username) {
                                urlParams.set('restore_username', encodeURIComponent(state.username));
                                needsReload = true;
                                console.log('[状态恢复] 需要恢复 username:', state.username);
                            }
                            if (!urlParams.has('restore_session_token') && state.session_token) {
                                urlParams.set('restore_session_token', encodeURIComponent(state.session_token));
                                needsReload = true;
                                console.log('[状态恢复] 需要恢复 session_token');
                            }
                            if (!urlParams.has('restore_user_language') && state.user_language) {
                                urlParams.set('restore_user_language', encodeURIComponent(state.user_language));
                                needsReload = true;
                            }
                            if (!urlParams.has('restore_room_language') && state.room_language) {
                                urlParams.set('restore_room_language', encodeURIComponent(state.room_language));
                                needsReload = true;
                            }
                            if (!urlParams.has('restore_auto_refresh') && state.auto_refresh !== undefined) {
                                urlParams.set('restore_auto_refresh', String(state.auto_refresh));
                                needsReload = true;
                            }
                            
                            if (needsReload) {
                                const newUrl = window.location.pathname + '?' + urlParams.toString();
                                console.log('[状态恢复] 准备重载页面，URL:', newUrl);
                                window.location.replace(newUrl);
                                return; // 立即返回，不再执行后续代码
                            } else {
                                console.log('[状态恢复] 无需重载，状态已恢复或不存在');
                            }
                        } else {
                            console.log('[状态恢复] localStorage 中没有找到状态数据');
                        }
                    } catch (e) {
                        console.error('[状态恢复] 错误:', e);
                    }
                })();
                </script>
                """
                # 使用st.markdown确保JavaScript在父页面执行（不是iframe中）
                # components.html 会在 iframe 中执行，无法访问父页面的 localStorage
                st.markdown(html, unsafe_allow_html=True)
                # 注意：JavaScript是异步的，无法在Python中判断是否需要重载
                # 只有当JavaScript检测到需要重载时才会重载，否则继续执行
            except Exception as e:
                # 如果失败，记录错误但不中断程序
                pass  # 静默失败，不影响主要功能
        
        return restored_from_url
    
    return False


def save_state_to_local_storage():
    """将当前session_state保存到浏览器localStorage"""
    # 需要持久化的状态键
    state_keys = [
        "room_id",
        "current_user",
        "user_language",
        "room_language",
        "auto_refresh"
    ]
    
    state_dict = {}
    for key in state_keys:
        if key in st.session_state:
            value = st.session_state[key]
            # 只保存非空值
            if value is not None and value != "":
                state_dict[key] = value
    
    if state_dict:
        try:
            state_json = json.dumps(state_dict, ensure_ascii=False)
            state_json_escaped = json.dumps(state_json)  # 双重转义用于JavaScript
            html = f"""
            <script>
            (function() {{
                try {{
                    const stateJson = {state_json_escaped};
                    localStorage.setItem('meeting_app_state', stateJson);
                    console.log('状态已保存:', {json.dumps(state_dict)});
                }} catch (e) {{
                    console.error('保存状态失败:', e);
                }}
            }})();
            </script>
            """
            # 使用st.markdown代替components.html
            st.markdown(html, unsafe_allow_html=True)
        except Exception:
            pass  # 静默失败，不影响主要功能


def auto_save_state():
    """自动保存状态 - 在状态改变时调用"""
    # 检查是否有状态改变
    if "_last_saved_state" not in st.session_state:
        st.session_state._last_saved_state = {}
    
    current_state = {
        "room_id": st.session_state.get("room_id"),
        "current_user": st.session_state.get("current_user"),
        "user_language": st.session_state.get("user_language"),
        "room_language": st.session_state.get("room_language"),
        "auto_refresh": st.session_state.get("auto_refresh")
    }
    
    # 如果状态改变，保存到localStorage
    if current_state != st.session_state._last_saved_state:
        save_state_to_local_storage()
        st.session_state._last_saved_state = current_state


def clear_room_state():
    """清除房间相关状态（退出房间时调用）"""
    try:
        html = """
        <script>
        (function() {
            try {
                const stateJson = localStorage.getItem('meeting_app_state');
                if (stateJson) {
                    const state = JSON.parse(stateJson);
                    // 只清除房间ID，保留其他状态
                    delete state.room_id;
                    localStorage.setItem('meeting_app_state', JSON.stringify(state));
                    console.log('房间状态已清除');
                }
            } catch (e) {
                console.error('清除房间状态失败:', e);
            }
        })();
        </script>
        """
        # 使用st.markdown代替components.html
        st.markdown(html, unsafe_allow_html=True)
    except Exception:
        pass  # 静默失败，不影响主要功能
