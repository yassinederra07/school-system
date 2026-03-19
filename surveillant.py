import streamlit as st
import pandas as pd
import os

DATA_FOLDER = "data"
ABSENCE_FILE = f"{DATA_FOLDER}/absence.csv"

def get_class_file(level, class_num):
    level = level.replace(" ", "_")
    return f"{DATA_FOLDER}/{level}_{class_num}.csv"

# =========================
# 📥 تحميل التلاميذ
# =========================
def load_students(level, class_num):
    file = get_class_file(level, class_num)

    if os.path.exists(file):
        df = pd.read_csv(file, encoding="utf-8-sig")

        df.columns = df.columns.str.strip()

        if "name" not in df.columns:
            df["name"] = ""
        if "lastname" not in df.columns:
            df["lastname"] = ""
        if "status" not in df.columns:
            df["status"] = "active"

        return df

    return pd.DataFrame()

# =========================
# 📥 تحميل الغياب
# =========================
def load_absence():
    if os.path.exists(ABSENCE_FILE):
        df = pd.read_csv(ABSENCE_FILE, encoding="utf-8-sig")

        if "class" in df.columns:
            df["class"] = df["class"].astype(str)

        # 🔥 إضافة allowed إذا ماكايناش
        if "allowed" not in df.columns:
            df["allowed"] = 0

        return df

    return pd.DataFrame()

# =========================
# ✅ السماح بالدخول (المهم)
# =========================
def allow_student(name, lastname, class_id):
    if os.path.exists(ABSENCE_FILE):
        df = pd.read_csv(ABSENCE_FILE, encoding="utf-8-sig")

        if "allowed" not in df.columns:
            df["allowed"] = 0

        df.loc[
            (df["name"] == name) &
            (df["lastname"] == lastname) &
            (df["class"] == class_id),
            "allowed"
        ] = 1

        df.to_csv(ABSENCE_FILE, index=False, encoding="utf-8-sig")

# =========================
# ❌ رفض (status)
# =========================
def update_status(level, class_num, name, lastname, status):
    file = get_class_file(level, class_num)

    if os.path.exists(file):
        df = pd.read_csv(file, encoding="utf-8-sig")

        if "status" not in df.columns:
            df["status"] = "active"

        df.loc[
            (df["name"] == name) &
            (df["lastname"] == lastname),
            "status"
        ] = status

        df.to_csv(file, index=False, encoding="utf-8-sig")

# =========================
# 🧑‍💼 واجهة الحارس العام
# =========================
def surveillant_panel():
    st.title("🧑‍💼 الحارس العام")

    level = st.selectbox("السلك", [
        "الأولى إعدادي",
        "الثانية إعدادي",
        "الثالثة إعدادي",
        "جدع مشترك"
    ])

    class_num = st.text_input("رقم القسم")

    if st.button("عرض"):
        students = load_students(level, class_num)
        absence = load_absence()

        if students.empty:
            st.warning("❌ لا يوجد هذا القسم")
        else:
            st.session_state["students"] = students.reset_index(drop=True)
            st.session_state["absence"] = absence

    if "students" in st.session_state:
        students = st.session_state["students"]
        absence = st.session_state["absence"]

        st.subheader("📋 لائحة التلاميذ")

        class_id = f"{level.replace(' ', '')}{class_num}"

        for i, row in students.iterrows():

            # 🔍 الغياب
            student_absence = pd.DataFrame()
            if not absence.empty:
                student_absence = absence[
                    (absence["name"] == row["name"]) &
                    (absence["lastname"] == row["lastname"]) &
                    (absence["class"] == class_id)
                ]

            # 🔥 هنا الحل الحقيقي
            if not student_absence.empty:
                is_absent = (student_absence["allowed"] == 0).any()
            else:
                is_absent = False

            is_stopped = row["status"] == "stopped"

            # 🎨 الحالة
            if is_stopped:
                bg_color = "#cccccc"
                status_text = "⛔ مرفوض"
            elif is_absent:
                bg_color = "#ffcccc"
                status_text = "🔴 غائب"
            else:
                bg_color = "#ffffff"
                status_text = "🟢 حاضر"

            with st.expander(f"👤 {row['name']} {row['lastname']} - {status_text}"):

                st.markdown(
                    f"""
                    <div style="
                        background-color:{bg_color};
                        padding:10px;
                        border-radius:10px;
                        margin-bottom:10px;
                        border:1px solid #ddd;
                    ">
                        👤 {row['name']} {row['lastname']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if student_absence.empty:
                    st.success("✅ لا يوجد غياب")
                else:
                    st.warning(f"📊 عدد الغيابات: {len(student_absence)}")

                    for _, abs_row in student_absence.iterrows():
                        st.error(
                            f"📅 {abs_row['date']} | {abs_row['day']} | {abs_row['session']} | {abs_row['period']}"
                        )

                col1, col2 = st.columns(2)

                # ✅ السماح
                with col1:
                    if st.button("✅ السماح بالدخول", key=f"ok_{row['name']}_{i}"):
                        allow_student(row["name"], row["lastname"], class_id)
                        st.success("✔️ تم السماح")
                        st.rerun()

                # ❌ رفض
                with col2:
                    if st.button("❌ رفض", key=f"no_{row['name']}_{i}"):
                        update_status(level, class_num, row["name"], row["lastname"], "stopped")
                        st.error("⛔ تم الرفض")
                        st.rerun()

# تشغيل
surveillant_panel()