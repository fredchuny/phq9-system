import streamlit as st
from supabase import create_client, Client

# ==========================================
# 1. 頁面基本配置（必須放在最上面）
# ==========================================
st.set_page_config(
    page_title="PHQ-9 完整健康評估系統",
    page_icon="📊",
    layout="centered"
)

# ==========================================
# 2. 初始化 Supabase 用戶端
# ==========================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 3. 登入狀態持久化管理 (使用 st.session_state)
# ==========================================
if "user" not in st.session_state:
    st.session_state.user = None
    
    # 嘗試從 Supabase 當前的 Session 恢復（作為備用）
    try:
        session = supabase.auth.get_session()
        if session and session.user:
            st.session_state.user = session.user
    except Exception:
        pass

# 定義登出函式
def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state.user = None
    st.rerun()

# ==========================================
# 4. 畫面渲染邏輯
# ==========================================
st.title("📊 PHQ-9 完整健康評估系統")

# --- 情況 A：使用者尚未登入 ---
if st.session_state.user is None:
    st.info("👋 歡迎使用本系統！請選擇以下方式登入以開始您的健康評估。")
    
    # 使用 Tabs 區分密碼登入與 Google 登入
    tab1, tab2 = st.tabs(["🔑 密碼登入", "🚀 Google 帳號登入"])
    
    # 【Tab 1: 密碼登入與註冊】
    with tab1:
        email = st.text_input("電子信箱", key="login_email", placeholder="example@gmail.com")
        password = st.text_input("密碼", type="password", key="login_password", placeholder="請輸入密碼")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("登入", type="primary", use_container_width=True):
                if not email or not password:
                    st.warning("請輸入完整的電子信箱與密碼！")
                else:
                    try:
                        # 呼叫 Supabase 進行密碼驗證
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        
                        # 🎯 關鍵修正：成功後立刻鎖定到 Streamlit 記憶體
                        st.session_state.user = res.user
                        st.success("登入成功！頁面載入中...")
                        st.rerun()
                    except Exception as e:
                        # 捕捉常見的未驗證錯誤或密碼錯誤
                        error_msg = str(e)
                        if "Email not confirmed" in error_msg:
                            st.error("❌ 登入失敗：該信箱尚未點擊驗證信！請前往您的 Gmail 收信。")
                        else:
                            st.error(f"❌ 登入失敗：{error_msg}")
                            
        with col2:
            if st.button("註冊新帳號", use_container_width=True):
                if not email or not password:
                    st.warning("請輸入欲註冊的電子信箱與密碼！")
                elif len(password) < 6:
                    st.warning("為了帳號安全，密碼長度至少需要 6 個字元！")
                else:
                    try:
                        res = supabase.auth.sign_up({"email": email, "password": password})
                        st.success("📨 註冊發送成功！請立刻前往您的信箱點擊「確認驗證連結」，驗證後即可返回此處登入。")
                    except Exception as e:
                        st.error(f"❌ 註冊失敗：{e}")

    # 【Tab 2: Google 快速登入】
    with tab2:
        st.write("點擊下方按鈕將跳轉至 Google 帳號授權頁面：")
        if st.button("使用 Google 帳號快速登入", type="secondary", use_container_width=True):
            try:
                # 調用 Google OAuth
                res = supabase.auth.sign_in_with_oauth({
                    "provider": "google",
                    "options": {
                        # 直接指定你在 Supabase 綁定的 Callback 網址
                        "redirect_to": "https://afancfdlwnbokaohkrsy.supabase.co/auth/v1/callback"
                    }
                })
                # 執行瀏覽器重導向至 Google 登入畫面
                auth_url = res.url
                st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'{auth_url}\'" />', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ 啟動 Google 登入失敗：{e}")

# --- 情況 B：使用者已成功登入 (呈現系統核心功能) ---
else:
    current_user = st.session_state.user
    
    # 頂部功能列與登出按鈕
    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.success(f"🟢 已成功登入帳號：{current_user.email}")
    with col_logout:
        st.button("登出系統", on_click=logout, type="secondary", use_container_width=True)
        
    st.divider()
    
    # ==========================================
    # 5. 您的問卷或核心系統功能放在這裡
    # ==========================================
    st.subheader("📋 患者健康問卷 (PHQ-9)")
    st.write("請根據過去兩星期以來，您受到下列問題困擾的頻率進行填寫：")
    
    # 範例問卷題目
    q1 = st.radio("1. 做任何事都提不起勁或沒有樂趣？", ["完全沒有", "有幾天", "一半以上的天數", "幾乎天天"])
    q2 = st.radio("2. 感到心情低落、沮喪或絕望？", ["完全沒有", "有幾天", "一半以上的天數", "幾乎天天"])
    
    if st.button("提交評估報告", type="primary"):
        st.balloons()
        st.success("數據已成功儲存至後端資料庫！感謝您的填寫。")
