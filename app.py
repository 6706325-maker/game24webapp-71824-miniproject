import streamlit as st
import random
import json
import os

# --- การจัดการฐานข้อมูลจำลอง (JSON) ---
DB_FILE = "users_db.json"

def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

# --- ระบบ Level & Rank ---
def get_rank_info(xp):
    if xp < 50: return "Bronze 🥉", 1, "#CD7F32"
    elif xp < 150: return "Silver 🥈", 2, "#C0C0C0"
    elif xp < 300: return "Gold 🥇", 3, "#FFD700"
    else: return "Platinum 💎", 4, "#E5E4E2"

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="24 Game Challenge", page_icon="🔢")

if 'user' not in st.session_state:
    st.session_state.user = None
if 'numbers' not in st.session_state:
    st.session_state.numbers = None

# --- หน้า Login / Register ---
if st.session_state.user is None:
    st.title("🔢 24 Game: Online Challenge")
    tab1, tab2 = st.tabs(["เข้าสู่ระบบ (Login)", "สมัครสมาชิก (Sign Up)"])
    users = load_users()

    with tab1:
        u_login = st.text_input("ชื่อผู้ใช้")
        p_login = st.text_input("รหัสผ่าน", type="password")
        if st.button("Log In"):
            if u_login in users and users[u_login]['password'] == p_login:
                st.session_state.user = u_login
                st.rerun()
            else:
                st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    with tab2:
        u_reg = st.text_input("สร้างชื่อผู้ใช้")
        p_reg = st.text_input("สร้างรหัสผ่าน", type="password")
        if st.button("Sign Up"):
            if u_reg in users:
                st.warning("ชื่อนี้มีอยู่ในระบบแล้ว")
            elif u_reg and p_reg:
                users[u_reg] = {"password": p_reg, "xp": 0}
                save_users(users)
                st.success("สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ")
            else:
                st.error("กรุณากรอกข้อมูลให้ครบถ้วน")

# --- หน้าเล่นเกม (หลังจาก Login) ---
else:
    users = load_users()
    current_user = st.session_state.user
    xp = users[current_user].get('xp', 0)
    rank_name, level, rank_color = get_rank_info(xp)

    # Sidebar
    st.sidebar.markdown(f"### 👤 ผู้เล่น: <span style='color:{rank_color}'>{current_user}</span>", unsafe_allow_html=True)
    st.sidebar.write(f"**Rank:** {rank_name}")
    st.sidebar.write(f"**XP:** {xp}")
    if st.sidebar.button("ออกจากระบบ"):
        st.session_state.user = None
        st.session_state.numbers = None
        st.rerun()

    st.title("🎮 เกมคณิตศาสตร์ 24")
    
    if st.session_state.numbers is None:
        st.session_state.numbers = [random.randint(1, 9) for _ in range(4)]

    st.write("ใช้เลขทั้ง 4 ตัวนี้ให้ได้ผลลัพธ์เท่ากับ 24:")
    cols = st.columns(4)
    for i in range(4):
        cols[i].markdown(f"<h1 style='text-align: center; background-color: #262730; color: white; border-radius: 10px;'>{st.session_state.numbers[i]}</h1>", unsafe_allow_html=True)

    user_ans = st.text_input("ใส่สมการของคุณ (เช่น (5+1)*4):", placeholder="ใช้เครื่องหมาย + - * / ( )")

    if st.button("ตรวจสอบคำตอบ", type="primary"):
        try:
            digits_in_ans = sorted([int(s) for s in user_ans if s.isdigit()])
            if digits_in_ans != sorted(st.session_state.numbers):
                st.error("❌ ต้องใช้เลขที่กำหนดให้ครบ 4 ตัว")
            else:
                result = eval(user_ans)
                if result == 24:
                    st.balloons()
                    st.success(f"ถูกต้อง! {user_ans} = 24 (+10 XP)")
                    users[current_user]['xp'] += 10
                    save_users(users)
                    st.session_state.numbers = None
                    st.button("เล่นข้อต่อไป")
                else:
                    st.error(f"ยังไม่ถูก! {user_ans} = {result}")
        except:
            st.warning("สมการไม่ถูกต้อง")

    if st.button("ข้ามข้อนี้"):
        st.session_state.numbers = None
        st.rerun()
