import streamlit as st  
import pandas as pd  
import datetime  
import os  
  
# =========================  
# 📁 نفس DATA ديال المدير  
# =========================  
DATA_FOLDER = "data"  
ABSENCE_FILE = f"{DATA_FOLDER}/absence.csv"  
  
# =========================  
# 📁 ملف القسم  
# =========================  
def get_class_file(level, class_num):  
    level = level.replace(" ", "_")  
    return f"{DATA_FOLDER}/{level}_{class_num}.csv"  
  
# =========================  
# 📥 تحميل التلاميذ  
# =========================  
def load_students(level, class_num):  
    file = get_class_file(level, class_num)  
  
    if os.path.exists(file):  
        return pd.read_csv(file, encoding="utf-8-sig")  
    return pd.DataFrame()  
  
# =========================  
# 💾 حفظ الغياب (FIX CSV ERROR)  
# =========================  
def save_absence(data):  
    columns = ["name","lastname","level","class","date","day","session","period"]  
  
    if os.path.exists(ABSENCE_FILE):  
        try:  
            df = pd.read_csv(ABSENCE_FILE, encoding="utf-8-sig")  
        except:  
            df = pd.DataFrame(columns=columns)  
    else:  
        df = pd.DataFrame(columns=columns)  
  
    df = pd.concat([df, pd.DataFrame(data)])  
    df.to_csv(ABSENCE_FILE, index=False, encoding="utf-8-sig")  
  
# =========================  
# 👨‍🏫 واجهة الأستاذ  
# =========================  
def prof_panel():  
    st.title("👨‍🏫 نظام الغياب")  
  
    # ===== اختيار =====  
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
  
    # ===== عرض =====  
    if st.button("عرض التلاميذ"):  
        students = load_students(level, class_num)  
  
        if students.empty:  
            st.warning("❌ لا يوجد هذا القسم أو لا يوجد تلاميذ")  
        else:  
            st.session_state["students"] = students.reset_index(drop=True)  
            st.session_state["absents"] = []  
  
    # ===== عرض اللائحة =====  
    if "students" in st.session_state:  
  
        # 🔒 تأمين session  
        if "absents" not in st.session_state:  
            st.session_state["absents"] = []  
  
        st.subheader("📋 لائحة التلاميذ")  
  
        for i, row in st.session_state["students"].iterrows():  
  
            is_absent = i in st.session_state["absents"]  
            bg_color = "#ffcccc" if is_absent else "#ffffff"  
  
            col1, col2 = st.columns([4,1])  
  
            # 🎨 الاسم مع اللون  
            with col1:  
                st.markdown(  
                    f"""  
                    <div style="  
                        background-color:{bg_color};  
                        padding:10px;  
                        border-radius:10px;  
                        margin-bottom:5px;  
                        border:1px solid #ddd;  
                    ">  
                        👤 {row['name']} {row['lastname']}  
                    </div>  
                    """,  
                    unsafe_allow_html=True  
                )  
  
            # 🔴 زر الغياب (مرة وحدة فقط)  
            with col2:  
                if not is_absent:  
                    if st.button("🔴", key=f"a_{i}"):  
                        st.session_state["absents"].append(i)  
                        st.rerun()  
                else:  
                    st.button("✔️", key=f"done_{i}", disabled=True)  
  
        # ===== حفظ =====  
        if st.button("💾 حفظ الغياب"):  
            data = []  

            class_id = f"{level.replace(' ', '')}{class_num}"
  
            for i in st.session_state["absents"]:  
                student = st.session_state["students"].loc[i]  
  
                data.append({  
                    "name": student["name"],  
                    "lastname": student["lastname"],  
                    "level": level,  
                    "class": class_id,  
                    "date": today,  
                    "day": day_name,  
                    "session": session,  
                    "period": period  
                })  
  
            save_absence(data)  
            st.success("✅ تم حفظ الغياب")  
  
# تشغيل  
prof_panel()