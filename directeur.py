import streamlit as st
import pandas as pd
import os
import random
import string
from difflib import get_close_matches

# ⚠️ إذا بغيت AI حقيقي
USE_AI = False  # بدلها True إذا عندك API

# =========================
# 📁 الملفات
# =========================
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

ABSENCE_FILE = f"{DATA_FOLDER}/absence.csv"
USERS_FILE = f"{DATA_FOLDER}/users.csv"

# =========================
# 📥 CSV (حل العربية نهائيا + separator fix)
# =========================
def load_data(file):
    if os.path.exists(file):
        try:
            df = pd.read_csv(file, encoding="utf-8-sig", sep=",")
        except:
            df = pd.read_csv(file, encoding="utf-8-sig", sep=";")

        # 🔥 إصلاح في حالة الأعمدة مدموجة
        if len(df.columns) == 1:
            df = df[df.columns[0]].str.split(",", expand=True)

            if df.shape[1] >= 6:
                df.columns = ["name","lastname","birth","number","gender","status"][:df.shape[1]]

        return df

    return pd.DataFrame()

def save_data(df, file):
    df.to_csv(file, index=False, encoding="utf-8-sig", sep=",")

# =========================
# 📁 ملف لكل قسم
# =========================
def get_class_file(level, class_num):
    level = level.replace(" ", "_")
    return f"{DATA_FOLDER}/{level}_{class_num}.csv"

# =========================
# 🔐 password
# =========================
def generate_password():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

# =========================
# 🎯 login
# =========================
def generate_login(name, lastname):
    return f"{name}{lastname}@taalim.ma".replace(" ", "").lower()

# =========================
# 🤖 AI حقيقي (اختياري)
# =========================
def ai_search(df, query):
    try:
        from openai import OpenAI
        client = OpenAI(api_key="YOUR_API_KEY")

        names = (df["name"] + " " + df["lastname"]).tolist()

        prompt = f"""
        عندي هذه الأسماء:
        {names}

        المستخدم كتب: {query}

        شكون أقرب اسم؟ رجع غير الاسم.
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content.strip()
        return df[(df["name"] + " " + df["lastname"]) == result]

    except:
        return df

# =========================
# 🤖 بحث ذكي (بدون API)
# =========================
def smart_search(df, query):
    if df.empty:
        return df

    df["full"] = (df["name"].astype(str) + " " + df["lastname"].astype(str))
    matches = get_close_matches(query, df["full"], n=10, cutoff=0.3)

    return df[df["full"].isin(matches)]

# =========================
# 🤵 لوحة المدير
# =========================
def directeur_panel():
    st.title("🔥 نظام إدارة الثانوية (AI)")

    choice = st.selectbox("اختار", [
        "إضافة قسم",
        "إضافة تلميذ",
        "توقيف تلميذ",
        "إرجاع تلميذ",
        "تسجيل الغياب",
        "Dashboard"
    ])

    # =========================
    # ➕ إضافة قسم
    # =========================
    if choice == "إضافة قسم":
        level = st.selectbox("السلك", [
            "الأولى إعدادي","الثانية إعدادي","الثالثة إعدادي","جدع مشترك"
        ])

        class_num = st.text_input("القسم")
        file = st.file_uploader("Excel", type=["xlsx"])

        if st.button("إنشاء"):
            if file and class_num:
                df_excel = pd.read_excel(file, dtype=str).fillna("")

                students = []
                for _, row in df_excel.iterrows():
                    students.append({
                        "name": str(row[0]).strip(),
                        "lastname": str(row[1]).strip(),
                        "birth": row[2],
                        "number": row[3],
                        "gender": row[4],
                        "status": "active"
                    })

                df = pd.DataFrame(students)
                save_data(df, get_class_file(level, class_num))

                st.success("✅ تم إنشاء القسم بملف خاص")

    # =========================
    # ➕ إضافة تلميذ
    # =========================
    elif choice == "إضافة تلميذ":
        level = st.text_input("السلك")
        class_num = st.text_input("القسم")

        name = st.text_input("الإسم")
        lastname = st.text_input("النسب")

        if st.button("إضافة"):
            file = get_class_file(level, class_num)
            df = load_data(file)

            new = {
                "name": name,
                "lastname": lastname,
                "birth": "",
                "number": len(df)+1,
                "gender": "",
                "status": "active"
            }

            df = pd.concat([df, pd.DataFrame([new])])
            save_data(df, file)

            st.success("✅ تمت الإضافة")

    # =========================
    # ⛔ توقيف (AI)
    # =========================
    elif choice == "توقيف تلميذ":
        level = st.text_input("السلك")
        class_num = st.text_input("القسم")

        file = get_class_file(level, class_num)
        df = load_data(file)

        search = st.text_input("🤖 ابحث بأي طريقة")

        if search:
            if USE_AI:
                df = ai_search(df, search)
            else:
                df = smart_search(df, search)

        if df.empty:
            st.warning("❌ لا يوجد")
        else:
            for i, row in df.iterrows():
                col1, col2, col3 = st.columns([4,2,2])

                with col1:
                    st.write(f"👤 {row['name']} {row['lastname']}")

                with col2:
                    st.write(row["status"])

                with col3:
                    if row["status"] == "active":
                        if st.button("⛔", key=f"s_{i}"):
                            df_all = load_data(file)
                            df_all.at[i, "status"] = "stopped"
                            save_data(df_all, file)
                            st.rerun()

    # =========================
    # 🔄 إرجاع
    # =========================
    elif choice == "إرجاع تلميذ":
        level = st.text_input("السلك")
        class_num = st.text_input("القسم")

        file = get_class_file(level, class_num)
        df = load_data(file)

        stopped = df[df["status"] == "stopped"]

        for i, row in stopped.iterrows():
            st.write(f"{row['name']} {row['lastname']}")

            if st.button("🔄", key=f"r_{i}"):
                df.at[i, "status"] = "active"
                save_data(df, file)
                st.rerun()

    # =========================
    # 📝 غياب
    # =========================
    elif choice == "تسجيل الغياب":
        level = st.text_input("السلك")
        class_num = st.text_input("القسم")

        file = get_class_file(level, class_num)
        df = load_data(file)

        date = st.date_input("📅")

        absences = []

        for i, row in df.iterrows():
            col1, col2 = st.columns([4,1])

            with col1:
                st.write(f"{row['name']} {row['lastname']}")

            with col2:
                if st.checkbox("غائب", key=f"a_{i}"):
                    absences.append({
                        "name": row["name"],
                        "lastname": row["lastname"],
                        "date": date,
                        "class": class_num
                    })

        if st.button("حفظ"):
            df_abs = load_data(ABSENCE_FILE)
            df_abs = pd.concat([df_abs, pd.DataFrame(absences)])
            save_data(df_abs, ABSENCE_FILE)

            st.success("✅ تم حفظ الغياب")

    # =========================
    # 📊 Dashboard
    # =========================
    elif choice == "Dashboard":
        df = load_data(ABSENCE_FILE)

        if df.empty:
            st.warning("لا يوجد بيانات")
        else:
            st.bar_chart(df.groupby("name").size())

# تشغيل
directeur_panel()