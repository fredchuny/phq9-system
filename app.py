import streamlit as st
from supabase import create_client, Client

# 初始化 Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 檢查登入狀態
user = None
try:
    session = supabase.auth.get_session()
    if session and session.user:
        user = session.user
except Exception:
    pass

st.title("📊 PHQ-9 完整健康評估系統")

if not user:
    st.info("👋 歡迎使用本系統！請選擇以下方式登入。")
    
    # 使用 Tabs 區分兩種登入方式
    tab1, tab2 = st.tabs(["🔑 密碼登入", "🚀 Google 帳號登入"])
    
    # --- Tab 1: 密碼登入 ---
    with tab1:
        email = st.text_input("電子信箱", key="login_email")
        password = st.text_input("密碼", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("登入", type="primary", use_container_width=True):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.success("登入成功！請重新整理網頁。")
                    st.rerun()
                except Exception as e:
                    st.error(f"登入失敗：{e}")
                    
        with col2:
            if st.button("註冊新帳號", use_container_width=True):
                try:
                    res = supabase.auth.sign_up({"email": email, "password": password})
                    st.success("註冊成功！現在可以直接點擊「登入」囉。")
                except Exception as e:
                    st.error(f"註冊失敗：{e}")

    # --- Tab 2: Google 登入 ---
    with tab2:
        if st.button("使用 Google 帳號快速登入", type="secondary"):
            try:
                res = supabase.auth.sign_in_with_oauth({
                    "provider": "google",
                    "options": {
                        "redirect_to": "https://afancfdlwnbokaohkrsy.supabase.co/auth/v1/callback"
                    }
                })
                auth_url = res.url
                st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'{auth_url}\'" />', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"啟動 Google 登入失敗：{e}")
