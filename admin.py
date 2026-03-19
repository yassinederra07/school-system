import streamlit as st
import random
import string
from database import load_users, save_user, get_system_status, set_system_status

# 🔐 توليد password
def generate_password():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(10))

# 🎯 توليد login
def generate_login(name, lastname):
    return f"{name.lower()}{lastname.lower()}@taalim.ma"

def admin_panel():
    st.title("🧑‍🔧 الطاقم التقني")

    df = load_users()

    # =========================
    # 🔒 معلومات الحساب التقني
    # =========================
    st.info("👨‍💻 الحساب التقني الوحيد:\nlogin: yassinederra@service")

    # =========================
    # ➕ إضافة مستخدم
    # =========================
    st.subheader("➕ إضافة مستخدم")

    name = st.text_input("الإسم")
    lastname = st.text_input("النسب")
    phone = st.text_input("رقم الهاتف")
    subject = st.text_input("المادة")

    role = st.selectbox("الفئة", [
        "prof",
        "surveillant",
        "directeur"
    ])

    if st.button("إنشاء حساب"):
        if name and lastname and phone and subject:
            login = generate_login(name, lastname)
            password = generate_password()

            save_user(login, password, role, name, lastname, phone, subject)

            st.success(f"✅ login: {login}")
            st.warning(f"🔐 password: {password}")
            st.rerun()
        else:
            st.error("❌ جميع الخانات ضرورية")

    # =========================
    # 📊 إحصائيات
    # =========================
    st.subheader("📊 إحصائيات المستخدمين")
    st.dataframe(df)

    # =========================
    # ⛔ توقيف حساب
    # =========================
    st.subheader("⛔ توقيف حساب")

    if not df.empty:
        selected_user = st.selectbox(
            "اختار login لتوقيفه",
            df["login"]
        )

        if st.button("توقيف الحساب"):
            df.loc[df["login"] == selected_user, "status"] = "stopped"
            df.to_csv("users.csv", index=False)
            st.success("تم توقيف الحساب ✅")
            st.rerun()

    # =========================
    # ❌ حذف حساب
    # =========================
    st.subheader("❌ حذف حساب")

    if not df.empty:
        delete_user = st.selectbox(
            "اختار login لحذفه",
            df["login"],
            key="delete_user"
        )

        if st.button("حذف الحساب"):
            df = df[df["login"] != delete_user]
            df.to_csv("users.csv", index=False)
            st.success("تم حذف الحساب ✅")
            st.rerun()

    # =========================
    # 🔌 التحكم في النظام
    # =========================
    st.subheader("🔌 التحكم في النظام")

    status = get_system_status()
    st.write(f"حالة النظام: {status}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("إيقاف النظام"):
            set_system_status("off")
            st.error("🚫 النظام متوقف")
            st.rerun()

    with col2:
        if st.button("تشغيل النظام"):
            set_system_status("on")
            st.success("✅ النظام يعمل")
            st.rerun()