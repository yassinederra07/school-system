import streamlit as st
import pandas as pd
import os
import random
import string
from difflib import get_close_matches

# =========================
# 📁 إعداد الملفات
# =========================
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

ABSENCE_FILE = f"{DATA_FOLDER}/absence.csv"
USERS_FILE = f"{DATA_FOLDER}/users.csv"

# =========================
# 📥 CSV
# =========================
def load_data(file):
    if os.path.exists(file):
        try:
            return pd.read_csv(file, encoding="utf-8-sig")
        except:
            return pd.read_csv(file, encoding="utf-8-sig", sep=";")
    return pd.DataFrame()

def save_data(df, file):
    df.to_csv(file, index=False, encoding="utf-8-sig")

# =========================
# 📁 ملفات الأقسام
# =========================
def get_class_file(level, class_num):
    level = level.replace(" ", "_")
    return f"{DATA_FOLDER}/{level}_{class_num}.csv"

def list_classes():
    return [f for f in os.listdir(DATA_FOLDER) if "_" in f and f.endswith(".csv") and "absence" not in f]

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
# 🤖 بحث
# =========================
def smart_search(df, query):
    df["full"] = (df["name"].astype(str) + " " + df["lastname"].astype(str))
    matches = get_close_matches(query, df["full"], n=10, cutoff=0.3)
    return df[df["full"].isin(matches)]

# =========================
# 🔍 تحديد الأعمدة بذكاء
# =========================
def find_column(columns, keywords):
    for key in keywords:
        for col in columns:
            if key in col:
                return col
    return None

# =========================
# 🤵 لوحة المدير
# =========================
def directeur_panel():
    st.title("🔥 نظام إدارة الثانوية PRO")

    choice = st.selectbox("اختار", [
        "إضافة قسم",
        "حذف قسم",
        "إضافة تلميذ",
        "توقيف تلميذ",
        "إرجاع تلميذ",
        "إحصائيات الغياب",
        "إضافة حساب"
    ])

    # =========================
    # ➕ إضافة قسم (FIX FINAL)
    # =========================
    if choice == "إضافة قسم":
        level = st.selectbox("السلك", ["الأولى إعدادي","الثانية إعدادي","الثالثة إعدادي","جدع مشترك"])
        class_num = st.text_input("رقم القسم")
        file = st.file_uploader("📂 Excel", type=["xlsx"])

        if st.button("إنشاء"):
            if file and class_num:
                df_excel = pd.read_excel(file, dtype=str).fillna("")

                # تنظيف الأعمدة
                df_excel.columns = df_excel.columns.str.strip().str.lower()
                cols = df_excel.columns

                # 🔥 التعرف الذكي
                name_col = find_column(cols, ["الاسم", "name"])
                lastname_col = find_column(cols, ["النسب", "lastname"])
                birth_col = find_column(cols, ["تاريخ", "birth"])
                number_col = find_column(cols, ["الرقم", "number"])
                gender_col = find_column(cols, ["النوع", "gender"])

                if not name_col or not lastname_col:
                    st.error("❌ تأكد من وجود الاسم والنسب في Excel")
                    return

                students = []

                for i, row in df_excel.iterrows():
                    name = str(row[name_col]).strip()
                    lastname = str(row[lastname_col]).strip()

                    # 🧠 تصحيح nan
                    if name == "" or name.lower() == "nan":
                        name = "غير معروف"
                    if lastname == "" or lastname.lower() == "nan":
                        lastname = ""

                    students.append({
                        "name": name,
                        "lastname": lastname,
                        "birth": str(row[birth_col]).strip() if birth_col else "",
                        "number": i + 1,
                        "gender": str(row[gender_col]).strip() if gender_col else "",
                        "status": "active"
                    })

                df = pd.DataFrame(students)
                save_data(df, get_class_file(level, class_num))

                st.success("✅ تم إنشاء القسم بنجاح")

    # =========================
    # ❌ حذف قسم
    # =========================
    elif choice == "حذف قسم":
        classes = list_classes()

        if not classes:
            st.warning("لا يوجد أقسام")
        else:
            selected = st.selectbox("اختر قسم", classes)

            if st.button("حذف"):
                os.remove(f"{DATA_FOLDER}/{selected}")
                st.success("✅ تم الحذف")
                st.rerun()

    # =========================
    # ➕ إضافة تلميذ
    # =========================
    elif choice == "إضافة تلميذ":
        level = st.selectbox("السلك", ["الأولى إعدادي","الثانية إعدادي","الثالثة إعدادي","جدع مشترك"])
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
    # ⛔ توقيف
    # =========================
    elif choice == "توقيف تلميذ":
        classes = list_classes()
        selected = st.selectbox("اختر القسم", classes)

        df = load_data(f"{DATA_FOLDER}/{selected}")

        for i, row in df.iterrows():
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"{row['number']} - {row['name']} {row['lastname']}")

            with col2:
                if row["status"] == "active":
                    if st.button("⛔", key=f"s_{i}"):
                        df.at[i, "status"] = "stopped"
                        save_data(df, f"{DATA_FOLDER}/{selected}")
                        st.rerun()

    # =========================
    # 🔄 إرجاع
    # =========================
    elif choice == "إرجاع تلميذ":
        classes = list_classes()
        selected = st.selectbox("القسم", classes)

        df = load_data(f"{DATA_FOLDER}/{selected}")
        stopped = df[df["status"] == "stopped"]

        for i, row in stopped.iterrows():
            st.write(f"{row['number']} - {row['name']} {row['lastname']}")

            if st.button("🔄", key=f"r_{i}"):
                df.at[i, "status"] = "active"
                save_data(df, f"{DATA_FOLDER}/{selected}")
                st.rerun()

    # =========================
    # 📊 إحصائيات
    # =========================
    elif choice == "إحصائيات الغياب":
        df = load_data(ABSENCE_FILE)

        if df.empty:
            st.warning("لا يوجد بيانات")
        else:
            stats = df.groupby(["name","date"]).size().reset_index(name="total")
            st.dataframe(stats)
            st.bar_chart(stats.groupby("name")["total"].sum())

    # =========================
    # 🔐 حساب
    # =========================
    elif choice == "إضافة حساب":
        role = st.selectbox("الفئة", ["prof","surveillant","directeur"])

        name = st.text_input("الإسم")
        lastname = st.text_input("النسب")
        phone = st.text_input("الهاتف")
        subject = st.text_input("المادة")

        if st.button("إنشاء"):
            login = generate_login(name, lastname)
            password = generate_password()

            df = load_data(USERS_FILE)

            new = {
                "login": login,
                "password": password,
                "role": role,
                "name": name,
                "lastname": lastname,
                "phone": phone,
                "subject": subject
            }

            df = pd.concat([df, pd.DataFrame([new])])
            save_data(df, USERS_FILE)

            st.success(f"✅ {login}")
            st.info(f"🔐 {password}")

# تشغيل
directeur_panel()