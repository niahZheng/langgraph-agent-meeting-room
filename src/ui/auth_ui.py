"""用户认证UI组件"""

import streamlit as st
import streamlit.components.v1 as components
from ..services.auth_service import get_auth_service
from .state_persistence import save_state_to_local_storage


def render_login_page():
    """渲染登录页面"""
    auth_service = get_auth_service()
    
    st.title("🔐 用户登录")
    st.markdown("---")
    
    # 登录表单
    with st.form("login_form"):
        username = st.text_input("用户名", key="login_username")
        password = st.text_input("密码", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_submit = st.form_submit_button("登录", use_container_width=True, type="primary")
        with col2:
            register_link = st.form_submit_button("前往注册", use_container_width=True)
        
        if login_submit:
            if not username or not password:
                st.error("请填写用户名和密码")
            else:
                success, error_msg, session_token = auth_service.login(username, password)
                if success:
                    # 保存登录状态到session_state
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.session_token = session_token
                    # 保存到Cookie（用于持久化）
                    _save_auth_state(username, session_token)
                    # 同时在URL中设置session_token，确保刷新后能恢复
                    st.query_params.update(session_token=session_token, username=username)
                    st.success(f"✅ 登录成功！欢迎 {username}")
                    st.rerun()
                else:
                    st.error(f"❌ {error_msg}")
        
        if register_link:
            st.session_state.show_register = True
            st.rerun()
    
    # 注册表单
    if st.session_state.get("show_register", False):
        st.markdown("---")
        st.subheader("📝 用户注册")
        
        with st.form("register_form"):
            reg_username = st.text_input("用户名（至少3个字符）", key="reg_username")
            reg_password = st.text_input("密码（至少6个字符）", type="password", key="reg_password")
            reg_password_confirm = st.text_input("确认密码", type="password", key="reg_password_confirm")
            reg_email = st.text_input("邮箱（可选）", key="reg_email")
            
            col1, col2 = st.columns(2)
            with col1:
                register_submit = st.form_submit_button("注册", use_container_width=True, type="primary")
            with col2:
                back_to_login = st.form_submit_button("返回登录", use_container_width=True)
            
            if register_submit:
                if not reg_username or not reg_password:
                    st.error("请填写用户名和密码")
                elif reg_password != reg_password_confirm:
                    st.error("两次输入的密码不一致")
                else:
                    success, error_msg = auth_service.register(reg_username, reg_password, reg_email if reg_email else None)
                    if success:
                        st.success("✅ 注册成功！请登录")
                        st.session_state.show_register = False
                        st.rerun()
                    else:
                        st.error(f"❌ {error_msg}")
            
            if back_to_login:
                st.session_state.show_register = False
                st.rerun()


def _save_auth_state(username: str, session_token: str):
    """保存认证状态到Cookie（专业方法）"""
    try:
        import json
        # 使用Cookie存储session token，30天有效期
        html = f"""
        <script>
        console.log('[保存Cookie] 开始保存认证状态到Cookie');
        (function() {{
            try {{
                // 设置Cookie，30天有效期
                const expires = new Date();
                expires.setTime(expires.getTime() + (30 * 24 * 60 * 60 * 1000));
                const sessionTokenValue = {json.dumps(session_token)};
                const usernameValue = {json.dumps(username)};
                document.cookie = 'session_token=' + encodeURIComponent(sessionTokenValue) + ';expires=' + expires.toUTCString() + ';path=/';
                document.cookie = 'username=' + encodeURIComponent(usernameValue) + ';expires=' + expires.toUTCString() + ';path=/';
                console.log('[保存Cookie] 认证状态已保存到Cookie - session_token:', sessionTokenValue ? '已设置' : '未设置', 'username:', usernameValue);
                console.log('[保存Cookie] 当前document.cookie:', document.cookie);
            }} catch (e) {{
                console.error('[保存Cookie] 保存认证状态失败:', e);
            }}
        }})();
        </script>
        """
        # 使用st.markdown确保JavaScript在父页面执行（不是iframe中）
        # components.html 会在 iframe 中执行，无法访问父页面的 Cookie
        st.markdown(html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"保存认证状态失败: {str(e)}")


def check_login() -> bool:
    """检查用户是否已登录（如果session_state中没有，尝试从localStorage恢复）"""
    # 如果session_state中已有登录状态，验证它
    if st.session_state.get("logged_in", False):
        session_token = st.session_state.get("session_token")
        if session_token:
            auth_service = get_auth_service()
            valid, username = auth_service.validate_session(session_token)
            if valid and username == st.session_state.get("username"):
                return True
            else:
                # Session无效，清除登录状态
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.session_token = None
                return False
        else:
            return False
    
    # 如果session_state中没有登录状态，尝试从URL参数恢复（由init_state_restoration处理）
    # 这里只检查是否已经恢复
    return False  # 如果还没有恢复，返回False，让init_state_restoration处理


def logout():
    """登出用户"""
    auth_service = get_auth_service()
    session_token = st.session_state.get("session_token")
    if session_token:
        auth_service.logout(session_token)
    
    # 清除登录状态
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.session_token = None
    
    # 清除Cookie
    html = """
    <script>
    (function() {
        try {
            // 清除Cookie
            document.cookie = 'session_token=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;';
            document.cookie = 'username=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;';
            console.log('Cookie已清除');
        } catch (e) {
            console.error('清除Cookie失败:', e);
        }
    })();
    </script>
    """
    st.markdown(html, unsafe_allow_html=True)
