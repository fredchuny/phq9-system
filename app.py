import streamlit as st
from supabase import create_client, Client

# 🔐 在 Streamlit Cloud，系統會自動從你設定的 Secrets 中抓取這兩個金鑰
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# 初始化 Supabase 雲端資料庫連線
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 網頁介面開始 ---
st.title("📊 PHQ-9 完整健康評估系統")
st.caption("數據將直接同步至 Supabase 雲端資料庫")

st.write("---")

# 填寫者基本資料輸入框
user_id = st.text_input("請輸入使用者 ID (例如: patient_001):", value="patient_test_02")
full_name = st.text_input("請輸入真實姓名:", value="王大同")

st.write("### 過去兩星期以來，您有多少天受以下問題困擾？")
st.caption("評分標準： 0: 完全沒有 | 1: 有幾天 | 2: 一半以上的天數 | 3: 幾乎天天")

# 完整 PHQ-9 九道題目
q1 = st.number_input("1. 做任何事情都提不起勁或沒有樂趣", min_value=0, max_value=3, value=0)
q2 = st.number_input("2. 感到心情低落、沮喪或絕望", min_value=0, max_value=3, value=0)
q3 = st.number_input("3. 入睡困難、睡不安穩或睡太多", min_value=0, max_value=3, value=0)
q4 = st.number_input("4. 感到疲倦或沒有活力", min_value=0, max_value=3, value=0)
q5 = st.number_input("5. 食慾不振或吃得太多", min_value=0, max_value=3, value=0)
q6 = st.number_input("6. 覺得自己很糟、覺得自己很失敗，或讓家人失望", min_value=0, max_value=3, value=0)
q7 = st.number_input("7. 專注事情有困難，例如看報紙或看電視時", min_value=0, max_value=3, value=0)
q8 = st.number_input("8. 動作或說話速度慢到別人察覺？或正好相反，煩躁不安到處走動？", min_value=0, max_value=3, value=0)
q9 = st.number_input("9. 有自殺或傷害自己的想法", min_value=0, max_value=3, value=0)

# 整合 9 題分數並計算總分
q_list = [q1, q2, q3, q4, q5, q6, q7, q8, q9]  
total_score = sum(q_list)

# 根據總分給予初步的臨床提示
st.write("---")
st.write(f"### 📊 目前累計總分：**{total_score} 分**")

if total_score >= 20:
    st.warning("提示：重度憂鬱傾向，建議尋求專業醫療或心理諮商協助。")
elif total_score >= 15:
    st.warning("提示：中重度憂鬱傾向，請多留意自身心理狀態並尋求支持。")
elif total_score >= 10:
    st.info("提示：中度憂鬱傾向。")
elif total_score >= 5:
    st.info("提示：輕微憂鬱傾向。")
else:
    st.success("提示：情緒狀態良好。")

st.write("---")

# 送出按鈕
if st.button("確認送出並上傳雲端"):
    if not user_id or not full_name:
        st.error("❌ 請填寫 ID 與姓名！")
    else:
        try:
            # 1. 寫入或更新使用者基本資料
            user_data = {"id": user_id, "full_name": full_name, "role": "patient"}
            supabase.table("phq9_users").upsert(user_data).execute()
            
            # 2. 完整寫入 9 題的分數與總分紀錄
            response_data = {
                "user_id": user_id,
                "q1": q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5, 
                "q6": q6, "q7": q7, "q8": q8, "q9": q9,
                "total_score": total_score
            }
            supabase.table("phq9_responses").insert(response_data).execute()
            
            st.success(f"🎉 成功！9 題數據已完整寫入雲端。使用者：{full_name}，總分：{total_score} 分。")
        except Exception as e:
            st.error(f"寫入失敗：{e}")
