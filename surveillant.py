import streamlit as st
import pandas as pd
import os

STUDENTS_FILE = "students.csv"
ABSENCE_FILE = "absence.csv"

def load_students():
    if os.path.exists(STUDENTS_FILE):
        return pd.read_csv(STUDENTS_FILE)
    else:
        return pd.DataFrame()

def load_absence():
    if os.path.exists(ABSENCE_FILE):
        return pd.read_csv(ABSENCE_FILE)
    else:
        return pd.DataFrame()

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
        students = load_students()
        absence = load_absence()

        class_students = students[
            (students["level"] == level) &
            (students["class"] == class_num)
        ]

        if class_students.empty:
            st.warning("لا يوجد تلاميذ")
        else:
            st.subheader("📋 لائحة التلاميذ")

            for i, row in class_students.iterrows():
                st.markdown(f"### {row['name']} {row['lastname']}")

                student_absence = absence[
                    (absence["name"] == row["name"]) &
                    (absence["lastname"] == row["lastname"])
                ]

                if student_absence.empty:
                    st.success("✅ لا يوجد غياب")
                else:
                    for _, abs_row in student_absence.iterrows():
                        st.error(
                            f"📅 {abs_row['date']} | {abs_row['day']} | {abs_row['session']} | {abs_row['period']}"
                        )

                col1, col2 = st.columns(2)

                with col1:
                    st.button("✅ السماح بالدخول", key=f"ok_{i}")

                with col2:
                    st.button("❌ رفض", key=f"no_{i}")