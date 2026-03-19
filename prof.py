import streamlit as st
import pandas as pd
import datetime
import os

STUDENTS_FILE = "students.csv"
ABSENCE_FILE = "absence.csv"

# تحميل التلاميذ
def load_students():
    if os.path.exists(STUDENTS_FILE):
        return pd.read_csv(STUDENTS_FILE)
    else:
        df = pd.DataFrame(columns=["name", "lastname", "level", "class"])
        df.to_csv(STUDENTS_FILE, index=False)
        return df

# حفظ الغياب
def save_absence(data):
    if os.path.exists(ABSENCE_FILE):
        df = pd.read_csv(ABSENCE_FILE)
    else:
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame(data)])
    df.to_csv(ABSENCE_FILE, index=False)

def prof_panel():
    st.title("👨‍🏫 نظام الغياب")

    # ===== اختيار المعلومات =====
    level = st.selectbox("السلك", [
        "الأولى إعدادي",
        "الثانية إعدادي",
        "الثالثة إعدادي",
        "جدع مشترك"
    ])

    class_num = st.text_input("رقم القسم")

    session = st.selectbox("الحصة", [
        "الأولى",
        "الثانية",
        "الثالثة",
        "الرابعة"
    ])

    period = st.selectbox("الفترة", [
        "صباحية",
        "مسائية"
    ])

    today = datetime.date.today()
    day_name = today.strftime("%A")

    st.info(f"📅 التاريخ: {today}")
    st.info(f"📆 اليوم: {day_name}")

    # ===== عرض التلاميذ =====
    if st.button("عرض التلاميذ"):
        df = load_students()

        students = df[
            (df["level"] == level) &
            (df["class"] == class_num)
        ]

        if students.empty:
            st.warning("لا يوجد تلاميذ")
        else:
            st.session_state["students"] = students
            st.session_state["absents"] = []

    # ===== لائحة التلاميذ =====
    if "students" in st.session_state:
        st.subheader("📋 لائحة التلاميذ")

        for i, row in st.session_state["students"].iterrows():
            col1, col2 = st.columns([3,1])

            with col1:
                st.write(f"{row['name']} {row['lastname']}")

            with col2:
                if st.button("🔴 غائب", key=i):
                    st.session_state["absents"].append(i)

        # ===== حفظ =====
        if st.button("💾 حفظ الغياب"):
            data = []

            for i in st.session_state["absents"]:
                student = st.session_state["students"].loc[i]

                data.append({
                    "name": student["name"],
                    "lastname": student["lastname"],
                    "level": level,
                    "class": class_num,
                    "date": today,
                    "day": day_name,
                    "session": session,
                    "period": period
                })

            save_absence(data)
            st.success("✅ تم حفظ الغياب")