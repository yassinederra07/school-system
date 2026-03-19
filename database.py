import pandas as pd
import os

FILE = "users.csv"
SYSTEM_FILE = "system_state.txt"  # 📌 ملف حالة النظام

# =========================
# 📥 تحميل المستخدمين
# =========================
def load_users():
    if os.path.exists(FILE):
        df = pd.read_csv(FILE)

        # ➕ إضافة colonne status إلا ماكانتش
        if "status" not in df.columns:
            df["status"] = "active"
            df.to_csv(FILE, index=False)

        return df
    else:
        df = pd.DataFrame(columns=[
            "login",
            "password",
            "role",
            "name",
            "lastname",
            "phone",
            "subject",
            "status"   # 📌 مهم
        ])
        df.to_csv(FILE, index=False)
        return df


# =========================
# 💾 حفظ مستخدم
# =========================
def save_user(login, password, role, name, lastname, phone, subject):
    df = load_users()

    new_user = {
        "login": login,
        "password": password,
        "role": role,
        "name": name,
        "lastname": lastname,
        "phone": phone,
        "subject": subject,
        "status": "active"  # 📌 الحالة الافتراضية
    }

    df = pd.concat([df, pd.DataFrame([new_user])])
    df.to_csv(FILE, index=False)


# =========================
# 🔌 حالة النظام
# =========================
def get_system_status():
    if not os.path.exists(SYSTEM_FILE):
        return "on"  # النظام شغال افتراضيا

    with open(SYSTEM_FILE, "r") as f:
        return f.read().strip()


def set_system_status(status):
    with open(SYSTEM_FILE, "w") as f:
        f.write(status)