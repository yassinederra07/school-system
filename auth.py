import streamlit as st
from database import load_users, get_system_status

def login():
    st.title("🏫 Al Masab Service")

    login_input = st.text_input("Login")
    password = st.text_input("Password", type="password")

    if st.button("Se connecter"):

        # =========================
        # 🔌 التحقق من حالة النظام
        # =========================
        system_status = get_system_status()

        if system_status == "off":
            # ❌ غير الطاقم التقني يقدر يدخل
            if login_input != "yassinederra@service":
                st.error("🚫 النظام متوقف من أجل الصيانة")
                return

        # =========================
        # 📥 تحميل المستخدمين
        # =========================
        df = load_users()

        user = df[
            (df["login"] == login_input) &
            (df["password"] == password)
        ]

        if not user.empty:

            # =========================
            # ⛔ التحقق من حالة الحساب
            # =========================
            if user.iloc[0]["status"] == "stopped":
                st.error("❌ تعذر الإتصال بالسيرفر، المرجو التواصل مع الدعم الفني")
                return

            role = user.iloc[0]["role"]
            name = user.iloc[0]["name"]

            st.session_state["login"] = True
            st.session_state["role"] = role
            st.session_state["name"] = name
            st.session_state["user_login"] = login_input

            st.success(f"مرحبا {name}")
            st.rerun()

        else:
            st.error("معلومات خاطئة ❌")