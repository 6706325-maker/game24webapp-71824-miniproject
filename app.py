import streamlit as st
import random
import json
import os
import math
import re

# --- ฐานข้อมูลและระบบ Rank ---
DB_FILE = "users_db.json"

def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_users(users):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def get_rank_info(xp):
    if xp < 50: return "Bronze 🥉", 1, "#CD7F32"
    elif xp < 150: return "Silver 🥈", 2, "#C0C0C0"
    elif xp < 300: return "Gold 🥇", 3, "#FFD700"
    else: return "Platinum 💎", 4, "#E5E4E2"

# --- ฟังก์ชันคำนวณ Factorial และแปลงเครื่องหมายมือถือ ---
def solve_expression(exp):
    # รองรับเครื่องหมายจากมือถือ
    exp = exp.replace('×', '*').replace('÷', '/')
    
    # แปลง n! เป็น math.factorial(n)
    def repl_factorial(match):
        num = int(match.group(1))
        return f"math.factorial({num})"
    
    exp = re.sub(r'(\d+)!', repl_factorial, exp)
    
    # จำกัดฟังก์ชัน math ไว้ใช้แค่ factorial เพื่อความปลอดภัย
    allowed_names = {"math": math}
    return eval(exp, {"__builtins__": None}, allowed_names)

# --- หน้าเว็บ ---
st.set_page_config(page_title="24 Game Challenge", page_icon="🔢")

if 'user' not in st.session_state:
    st.session_state.user = None
if 'numbers' not in st.session_state:
    st.session_state.numbers = None

if st.session_state.user is None:
    st.title("🔢 24 Game: Online Challenge")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    users = load_users()

    with tab1:
        u_login = st.text_input("ชื่อผู้ใช้")
        p_login = st.text_input("รหัสผ่าน", type="password")
        if st.button("Log In"):
            if u_login in users and users[u_login]['password'] == p_login:
                st.session_state.user = u_login
                st.rerun()
            else: st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    with tab2:
        u_reg = st.text_input("สร้างชื่อผู้ใช้")
        p_reg = st.text_input("สร้างรหัสผ่าน", type="password")
        if st.button("Sign Up"):
            if u_reg in users: st.warning("ชื่อนี้มีอยู่แล้ว")
            elif u_reg and p_reg:
                users[u_reg] = {"password": p_reg, "xp": 0}
                save_users(users)
                st.success("สมัครสมาชิกสำเร็จ!")

else:
    users = load_users()
    current_user = st.session_state.user
    xp = users[current_user].get('xp', 0)
    rank_name, level, rank_color = get_rank_info(xp)

    st.sidebar.markdown(f"### 👤 <span style='color:{rank_color}'>{current_user}</span>", unsafe_allow_html=True)
    st.sidebar.write(f"**Rank:** {rank_name} | **XP:** {xp}")
    if st.sidebar.button("ออกจากระบบ"):
        st.session_state.user = None
        st.session_state.numbers = None
        st.rerun()

    st.title("🎮 เกม 24 (Factorial Edition)")
    
    if st.session_state.numbers is None:
        st.session_state.numbers = [random.randint(1, 9) for _ in range(4)]

    st.write("เลขของคุณคือ:")
    cols = st.columns(4)
    for i in range(4):
        cols[i].markdown(f"<h1 style='text-align: center; background-color: #262730; color: white; border-radius: 10px;'>{st.session_state.numbers[i]}</h1>", unsafe_allow_html=True)

    user_ans = st.text_input("พิมพ์สมการ (ใช้เลขทั้ง 4 ตัว):", placeholder="ตัวอย่าง: 4! หรือ (5+1)*4")

    if st.button("ตรวจสอบคำตอบ", type="primary"):
        try:
            # ดึงเฉพาะตัวเลขที่ผู้ใช้พิมพ์ออกมา
            input_digits = sorted([int(d) for d in re.findall(r'\d+', user_ans)])
            given_digits = sorted(st.session_state.numbers)

            if any(user_ans.count(str(n)) > given_digits.count(n) for n in set(given_digits)):
                st.error("❌ ไม่สามารถใช้ตัวเลขซ้ำได้ (เกินจำนวนที่กำหนด)")
            elif input_digits != given_digits:
                st.error("❌ ใช้ได้เพียงตัวเลขที่กำหนดให้เท่านั้น")
            else:
                result = solve_expression(user_ans)
                if result == 24:
                    st.balloons()
                    st.success(f"ถูกต้อง! {user_ans} = 24 (+10 XP)")
                    users[current_user]['xp'] += 10
                    save_users(users)
                    st.session_state.numbers = None
                    st.button("เล่นข้อต่อไป")
                else:
                    st.error(f"❌ ผลลัพธ์ไม่เท่ากับ 24 (ได้ {result})")
        except Exception as e:
            st.warning("รูปแบบสมการไม่ถูกต้อง (เช่น ลืมใส่เครื่องหมาย หรือใช้วงเล็บไม่ครบ)")

    if st.button("ข้าม/สุ่มใหม่"):
        st.session_state.numbers = None
        st.rerun()
