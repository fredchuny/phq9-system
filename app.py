import streamlit as st
from supabase import create_client, Client

# 🔐 在 Streamlit Cloud，系統會自動從後台安全設定中抓取這兩個金鑰
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ... 下方維持你原本的 Streamlit 介面與寫入邏輯 ...
