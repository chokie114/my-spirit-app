#st.set_page_config(page_title="Wine, Beer & Spirit Lab Master v4.3", layout="wide", initial_sidebar_state="expanded")
import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import streamlit.components.v1 as components
from scipy import stats
import plotly.graph_objects as go # สำหรับกราฟที่ปรับสเกลแกน Y ได้
import base64
from plotly.subplots import make_subplots # สำหรับพล็อต 2 แกน Y
import streamlit.components.v1 as components
import os
from datetime import datetime

import streamlit as st

# โค้ดสำหรับซ่อน Main Menu และ Footer บางส่วน
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 1. การตั้งค่าหน้าจอและซ่อนเมนูที่รองรับทุกอุปกรณ์ (รวม MacBook M4) ---
st.markdown("""
    <style>
    /* ซ่อนปุ่มขีดสามขีด (Main Menu) และ Toolbar ด้านขวาบน */
    #MainMenu {visibility: hidden;}
    [data-testid="stToolbar"] {display: none;}
    
    /* ซ่อน Footer ด้านล่าง */
    footer {visibility: hidden;}
    
    /* แก้ไขปัญหา Sidebar สำหรับ MacBook M4 และ macOS */
    /* เราจะไม่ซ่อน header ทั้งหมด แต่จะทำให้มันโปร่งใสแทน เพื่อให้ปุ่ม Sidebar ยังทำงานได้ */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        color: #31333F !important;
    }

    /* ปรับแต่งปุ่มลูกศร/ปุ่มเปิด Sidebar (>) ให้แสดงผลชัดเจนและกดง่าย */
    [data-testid="stSidebarCollapseButton"] {
        background-color: #f0f2f6 !important;
        border-radius: 8px !important;
        margin-top: 5px !important;
        margin-left: 5px !important;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1) !important;
        display: block !important;
    }

    /* พยายามซ่อนปุ่มมุมขวาล่างที่อาจรบกวนสายตา */
    .viewerBadge_container__1QS1n {display: none !important;}
    </style>
    """, unsafe_allow_html=True)

# --- ฟังก์ชันติดตามการเข้าใช้งาน (Usage Tracker) ---
def track_usage(username="Anonymous"):
    log_file = "usage_log.csv"
    
#--- 1. ตรวจสอบว่ามีไฟล์ Log หรือยัง ถ้าไม่มีให้สร้างพร้อม Header
    if not os.path.exists(log_file):
        df_init = pd.DataFrame(columns=["Timestamp", "User", "Session_ID"])
        df_init.to_csv(log_file, index=False, encoding='utf-8-sig')
    
#--- 2. บันทึกข้อมูลเมื่อมีการเริ่ม Session ใหม่ (ป้องกันการนับซ้ำจากการกดปุ่มในหน้าเดิม)
    if 'session_logged' not in st.session_state:
        try:
            # ดึง Session ID (เฉพาะของ Streamlit)
            from streamlit.runtime.scriptrunner import get_script_run_ctx
            ctx = get_script_run_ctx()
            session_id = ctx.session_id if ctx else "Unknown"
            
            # บันทึกลงไฟล์
            new_entry = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "User": username,
                "Session_ID": session_id
            }
            df_log = pd.read_csv(log_file)
            df_log = pd.concat([df_log, pd.DataFrame([new_entry])], ignore_index=True)
            df_log.to_csv(log_file, index=False, encoding='utf-8-sig')
            
            st.session_state.session_logged = True
        except:
            pass

# --- 3. ส่วนหน้าจอรับชื่อผู้ใช้ (Version: Earth Tone Elegant - 100% Internal) ---
if 'username' not in st.session_state:
    st.markdown("""
        <style>
        /* 1. พื้นหลัง Earth Tone: ไล่เฉดสีน้ำตาลกาแฟเข้มถึงดำ */
        .stApp {
            background: radial-gradient(circle, #3e2723 0%, #1b1111 100%);
            background-attachment: fixed;
        }

        /* 2. กรอบฉลากพรีเมียม (สีครีมงาช้าง) */
        .login-card {
            background-color: #fffaf0; 
            padding: 50px;
            border: 4px double #722f37; /* ขอบเส้นคู่สีแดงไวน์ */
            box-shadow: 0 30px 60px rgba(0,0,0,0.6);
            text-align: center;
            max-width: 620px;
            margin: auto;
            border-top: 10px solid #722f37; /* แถบหนาสีแดงไวน์ด้านบน */
            border-radius: 4px;
        }

        .distillery-title {
            font-family: 'Georgia', serif;
            color: #722f37;
            font-size: 48px;
            font-weight: bold;
            letter-spacing: 4px;
            margin-bottom: 5px;
        }

        /* Label สีน้ำเงินบนแถบสีเหลืองทอง */
        div[data-testid="stForm"] label p {
            color: #1224c9 !important;
            background-color: #e39e10 !important; /* สีทอง Amber Gold */
            padding: 10px 15px;
            border-radius: 5px 5px 0 0;
            font-size: 18px !important;
            font-weight: bold !important;
            margin-bottom: -5px;
            display: block;
            width: 100%;
            text-align: left;
        }

        /* ช่องกรอกข้อมูล (Input) */
        .stTextInput > div > div > input {
            background-color: #ffffff !important;
            color: #2c3e50 !important;
            border: 2px solid #722f37 !important;
            border-radius: 0 0 5px 5px !important;
            height: 55px;
            font-size: 16px;
        }

        /* 3. ปุ่ม ENTER (สถานะปกติ) */
        div[data-testid="stFormSubmitButton"] > button {
            background-color: #722f37 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 4px !important;
            width: 100%;
            height: 60px;
            font-weight: bold;
            font-size: 22px;
            letter-spacing: 3px;
            transition: all 0.2s ease;
            margin-top: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        /* เมื่อเมาส์ชี้ (Hover) */
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #a93226 !important;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }

        /* 4. ไฮไลต์สีทองอำพันเมื่อกด (Active) */
        div[data-testid="stFormSubmitButton"] > button:active {
            background-color: #d4af37 !important; /* สีทอง Amber Gold */
            color: #1b1111 !important; /* ตัวหนังสือสีเข้มตัดกับสีทอง */
            transform: scale(0.96);
            transition: 0s;
        }
        
        .access-tag {
            color: #722f37;
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 5px;
            margin-bottom: 35px;
            text-transform: uppercase;
            border-bottom: 1px solid #d7ccc8;
            padding-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # จัดวาง Layout ให้กึ่งกลาง
    _, mid_col, _ = st.columns([1, 5, 1])

    with mid_col:
        st.markdown('<br><br><br>', unsafe_allow_html=True)
        
        # เริ่มการแสดงผล Card
        st.markdown("""
            <div class="login-card">
                <div class="distillery-subtitle">Wine, Beer & Spirit </div>
                <div class="distillery-title">LAB MASTER</div>
                <div class="distillery-subtitle">ESTABLISHED 2026</div>
                <div class="distillery-subtitle">🥃 version 4.3 🍺</div>
        """, unsafe_allow_html=True)

        with st.form("earth_tone_login"):
            # ช่องกรอกชื่อ (Label สีขาวบนพื้นแดง)
            user_name = st.text_input(
                "USER IDENTIFICATION:", 
                placeholder="ระบุชื่อ, บริษัท หรือ แบรนด์สินค้าของคุณ..."
            )
            
            # ปุ่มเข้าสู่ระบบ (ไฮไลต์ทองเมื่อกด)
            submit = st.form_submit_button("ENTER THE DISTILLERY")
            
            if submit:
                if user_name.strip():
                    st.session_state.username = user_name.strip()
                    track_usage(user_name.strip())
                    st.rerun()
                else:
                    st.error("❌ โปรดระบุข้อมูลผู้ใช้ก่อนเข้าสู่ระบบ")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ข้อความ Footer เล็กๆ
        st.markdown("""
            <p style="text-align:center; color:#d7ccc8; font-size:12px; margin-top:30px; opacity:0.6; letter-spacing:1px;">
                WINE • BEER • SPIRIT ANALYTICS SYSTEM V4.3
            </p>
        """, unsafe_allow_html=True)

    st.stop()
# หยุดการทำงานด้านล่างทั้งหมดจนกว่าจะ Login สำเร็จ
# --- เรียกใช้ฟังก์ชันติดตามการเข้าใช้งาน (Usage Tracker) ---

# การตั้งค่าหน้าจอ (Page Configuration) ---
st.set_page_config(page_title="Wine, Beer & Spirit Lab Master v4.3", layout="wide")

# การปรับแต่ง CSS (Styling) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }
    
    .main-title { 
        color: #722f37; 
        font-size: 85px; 
        font-weight: bold; 
        text-align: center; 
        border-bottom: 5px solid #722f37; 
        padding-bottom: 15px; 
        margin-top: 10px;
        margin-bottom: 40px; 
    }
    
    .datetime-display {
        text-align: right;
        font-size: 18px;
        color: #5d6d7e;
        font-weight: bold;
        margin-bottom: -15px;
    }

    .result-container { background-color: #fdf2e9; padding: 25px; border-radius: 15px; border-left: 8px solid #e67e22; text-align: center; margin-top: 15px; }
    .result-value { font-size: 38px; color: #d35400; font-weight: bold; }
    .param-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 10px; border: 1px solid #d1d8e0; }
    .info-card { background-color: #e8f6f3; padding: 15px; border-radius: 10px; border-left: 5px solid #16a085; margin-bottom: 15px; }
    .highlight-label { color: #2c3e50; font-size: 20px; font-weight: bold; margin-bottom: 5px; }
    .sub-result { font-size: 28px; color: #1e8449; font-weight: bold; margin: 0; }
    
    .st-expanderHeader { font-size: 18px !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ฟังก์ชันคำนวณมาตรฐาน (Core Logic) ---
def calculate_abv(start_val, current_val, unit_type, efficiency=0.92):
    try:
        s = float(start_val)
        c = float(current_val)
        eff = float(efficiency)
    except (ValueError, TypeError):
        return 0.0
        
    if s <= c: return 0.0
        
    if "SG" in str(unit_type):
        # สูตร Alternate ABV สำหรับไวน์
        raw_abv = (76.08 * (s - c) / (1.775 - s)) * (c / 0.794)
        return raw_abv * eff
    elif "Brix" in str(unit_type):
        # สูตร Brix (Corrected for Alcohol)
        raw_abv = (1.646 * s) - (2.703 * c)
        return max(raw_abv * eff, 0.0)
    elif "Bé" in str(unit_type) or "Baumé" in str(unit_type):
        # แปลง Bé เป็น SG ก่อนคำนวณ
        s_sg = 145 / (145 - s)
        c_sg = 145 / (145 - c)
        raw_abv = (76.08 * (s_sg - c_sg) / (1.775 - s_sg)) * (c_sg / 0.794)
        return raw_abv * eff
    return 0.0

def play_sound():
    audio_html = """<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mp3"></audio>"""
    components.html(audio_html, height=0)

# --- 5. ฟังก์ชันจัดการ วัน เดือน พ.ศ. เวลา ---
def get_thai_datetime():
    now = datetime.now()
    thai_days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    thai_months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    day_name = thai_days[now.weekday()]
    month = thai_months[now.month - 1]
    return f"วัน{day_name}ที่ {now.day} {month} พ.ศ. {now.year + 543} | เวลา: {now.strftime('%H:%M:%S')} น."

# --- 6. Sidebar Selection ---
st.sidebar.markdown("# 🍷 เมนูหลัก")

# 🚩 เพิ่มบรรทัดนี้เข้าไปเพื่อให้ตัวแปร yeast_eff ถูกนิยามก่อนนำไปใช้งาน
yeast_eff = st.sidebar.slider(
    "🧬 ประสิทธิภาพยีสต์ (Efficiency)", 
    0.80, 1.00, 0.92, 
    help="ปกติอยู่ที่ 0.90-0.95 เพื่อหักลบส่วนที่ยีสต์ใช้สร้างเซลล์และคาร์บอนไดออกไซด์ที่ระเหยไป"
)

# --- 7. ส่วนควบคุม Sidebar (Sidebar Control) ---
with st.sidebar:
    st.title("🧪 Lab Master Menu")
    
    # กลุ่มที่ 1: ขั้นพื้นฐาน (Basic Tools) ---
    st.markdown("### 🛠️ ขั้นพื้นฐาน (Basic)")
    
    with st.expander("1️⃣ การแปลงหน่วยพื้นฐาน", expanded=False):
        show_temp = st.checkbox("🌡️ 1.1 อุณหภูมิ", value=False)
        show_vol = st.checkbox("💧 1.2 ปริมาตร (แปลงหน่วย)", value=False)
        show_tank_vol = st.checkbox("🛢️ 1.3 ปริมาตรถังหมัก", value=False)
        show_conc = st.checkbox("🧪 1.4 ความเข้มข้น", value=False)
        show_sugar_conv = st.checkbox("🍭 1.5 การแปลงหน่วยน้ำตาล", value=False)
        show_alc = st.checkbox("🥃 1.6 หน่วยแอลกอฮอล์", value=False)

    with st.expander("2️⃣ คำนวณแอลกอฮอล์/หนาแน่น/ขม", expanded=False):
        # 🚩 แก้ไข Error: นิยามตัวแปร show_reading สำหรับหัวข้อ 2.1
        show_reading = st.checkbox("⚖️ 2.1 แปลงค่าความหนาแน่น", value=False)
        show_abv_est = st.checkbox("📈 2.2 ประมาณการ ABV", value=False)
        show_ibu = st.checkbox("🌿 2.3 การคำนวณความขม (IBU)", value=False)
        show_carb = st.checkbox("🫧 2.4 การอัดก๊าซ (Carbonation)", value=False)

    with st.sidebar.expander("3️⃣ การปรับกรดและเคมี", expanded=False):
        show_acid = st.checkbox("🍋 การเติมกรดต่างๆ", value=False)
        show_ta = st.checkbox("🧪 Titratable Acidity (TA)", value=False)

    with st.sidebar.expander("4️⃣ การเติมสารปรุงแต่ง", expanded=False):
        show_so2 = st.checkbox("🛡️ การเติม SO2 (KMS)", value=False)
        show_nutrients = st.checkbox("🧬 สารอาหารและแทนนิน", value=False)

    with st.sidebar.expander("5️⃣ การทำให้ใสและคงตัว", expanded=False):
        show_fining = st.checkbox("✨ การใช้สาร Fining & Carbon", value=False)
        show_stabilize = st.checkbox("🧊 การคงตัว (Sorbic Acid)", value=False)

    with st.sidebar.expander("6️⃣ การปรับหวานและผสม", expanded=False):
        show_pearson = st.checkbox("⚖️ Pearson Square (ปรับความหวาน)", value=False)
        show_dilution = st.checkbox("💧 การเจือจางแอลกอฮอล์ด้วยน้ำ", value=False)

    with st.expander("7️⃣ การประเมินทางประสาทสัมผัส", expanded=False):
        show_sensory = st.checkbox("👅 7. Sensory Evaluation", value=False)

    with st.expander("8️⃣ การคิดต้นทุนและวิเคราะห์", expanded=False):
        show_costing = st.checkbox("💰 8. Batch Costing & Yield", value=False)
    
    # --- 🚩 เส้นแบ่งกลุ่มระหว่าง Basic และ Advance ---
    #st.divider()
    
    # กลุ่มที่ 2: ขั้นสูง (Advance Analysis) ---
    st.markdown("### 🚀 ขั้นสูง (Advance)")
    
    with st.expander("9️⃣ การติดตามการหมัก", expanded=False):
        show_ferment = st.checkbox("📊 8.1 Fermentation Monitoring", value=False)

    with st.sidebar.expander("🔟 การออกแบบและวางแผน", expanded=False):
        show_wine_recipe = st.checkbox("🍷 10.1 การวางแผนไวน์ (Wine Design)", value=False)
        show_beer_recipe = st.checkbox("🍺 10.2 การวางแผนเบียร์ (Beer Design)", value=False)

    with st.expander("1️⃣1️⃣ เคมีน้ำและค่า pH", expanded=False):
        show_water_chem = st.checkbox("💧 11. Water & pH Management", value=False)
    
    with st.sidebar.expander("1️⃣2️⃣ การกลั่นและจุดตัด (Distillation)", expanded=False):
        show_distillation_log = st.checkbox("🔥 12. Distillation Log & Cuts", value=False)

    with st.sidebar.expander("1️⃣3️⃣ การควบคุมคุณภาพ (QC/QA)", expanded=False):
        show_qc_qa = st.checkbox("✅ 13. Quality Control & Report", value=False)
    st.markdown("### 🔑 HELP & CONTACT")
    # ในส่วน Sidebar Info & Help
    #st.sidebar.divider()
    with st.sidebar.expander("ℹ️ ข้อมูลและช่วยเหลือ", expanded=False):
        show_help_contact = st.checkbox("📖 14. Help & Contact", value=False)

    st.divider()

# --- 7. MAIN CONTENT ---
st.markdown(f'<p class="datetime-display">{get_thai_datetime()}</p>', unsafe_allow_html=True)
st.markdown('<p class="main-title">🍷 Wine, Beer, & Spirit Master</p>', unsafe_allow_html=True)

# ==========================================
# CATEGORY 1: การแปลงหน่วยพื้นฐาน
# ==========================================

# --- 1.1 การแปลงอุณหภูมิ (Temperature Conversion) ---
if show_temp:
    st.subheader("🌡️ 1.1 การแปลงอุณหภูมิ (Temperature Conversion)")
    col1, col2 = st.columns(2)
    with col1:
        t_from = st.radio("เลือกหน่วยต้นทาง:", ["Celsius (°C)", "Fahrenheit (°F)"], horizontal=True, key="t_from")
        t_val = st.number_input(f"ระบุค่าอุณหภูมิ ({t_from}):", value=25.0, step=0.1)
    with col2:
        if t_from == "Celsius (°C)":
            t_res = (t_val * 9/5) + 32
            t_to = "Fahrenheit (°F)"
        else:
            t_res = (t_val - 32) * 5/9
            t_to = "Celsius (°C)"
        
        st.markdown(f"""
            <div class="result-container">
                <p class="highlight-label">แปลงเป็น {t_to}</p>
                <p class="result-value">{t_res:.2f} °{t_to[0]}</p>
            </div>
        """, unsafe_allow_html=True)
    st.divider()

# --- 1.2 Volume Conversion
if show_vol:
    st.subheader("💧 1.2 การแปลงปริมาตร (Standard Conversion)")
    vol_factors = {"มิลลิลิตร (mL)": 0.001, "ลิตร (L)": 1.0, "ออนซ์ (oz)": 0.02957, "US Gallon": 3.785, "m³": 1000.0}
    c1, c2 = st.columns(2)
    with c1:
        v_from = st.selectbox("จากหน่วย:", list(vol_factors.keys()), key="cat1_vol_from_unique")
        v_val = st.number_input("ปริมาณ:", value=1.0, key="cat1_vol_val")
    with c2:
        v_to = st.selectbox("เป็นหน่วย:", list(vol_factors.keys()), index=1, key="cat1_vol_to_unique")
        res = (v_val * vol_factors[v_from]) / vol_factors[v_to]
        st.markdown(f'<div class="result-container"><p>{v_to}</p><p class="result-value">{res:,.4f}</p></div>', unsafe_allow_html=True)
    st.divider()

# --- 1.3 Tank Volume Calculation
if show_tank_vol:
    st.subheader("🛢️ 1.3 การหาปริมาตรถังหมัก (Tank Volume Calculation)")
    st.markdown('<div class="info-card">คำนวณปริมาตรถังทรงกระบอกก้นกรวย (Cylinder + Cone Bottom)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        t_dia = st.number_input("เส้นผ่าศูนย์กลางถัง (m):", value=1.0, step=0.1, key="tank_dia_cat1")
        t_h_cyl = st.number_input("ความสูงส่วนทรงกระบอก (m):", value=2.0, step=0.1, key="tank_h_cyl_cat1")
        t_h_cone = st.number_input("ความสูงส่วนทรงกรวย (m):", value=0.5, step=0.1, key="tank_h_cone_cat1")
        t_mode = st.radio("ส่วนที่คำนวณ:", ["รวมทั้งหมด", "ทรงกระบอกอย่างเดียว", "ทรงกรวยอย่างเดียว"], key="tank_mode_cat1")
    
    # Logic
    r = t_dia / 2
    v_cyl = np.pi * (r**2) * t_h_cyl
    v_cone = (1/3) * np.pi * (r**2) * t_h_cone
    
    if t_mode == "ทรงกระบอกอย่างเดียว": final_m3 = v_cyl
    elif t_mode == "ทรงกรวยอย่างเดียว": final_m3 = v_cone
    else: final_m3 = v_cyl + v_cone

    with c2:
        st.markdown(f"""
            <div class="result-container">
                <p class="highlight-label">ปริมาตรรวม</p>
                <p class="result-value">{final_m3:.4f} m³</p>
                <hr style="border: 0.5px solid #e67e22;">
                <p class="highlight-label">คิดเป็นลิตร</p>
                <p class="sub-result" style="color:#d35400; font-size:35px; font-weight:bold;">{final_m3 * 1000:,.2f} L</p>
            </div>
        """, unsafe_allow_html=True)
    st.divider()

# --- 1.4 การแปลงหน่วยความเข้มข้น (Concentration Conversion) ---
if show_conc:
    st.subheader("🧪 1.4 การแปลงหน่วยความเข้มข้นสารเคมี")
    conc_units = [
        "mg/L (Milligrams per Liter)", "ppm (Parts per Million)", 
        "Molarity (M - Mol/L)", "% w/v (Weight/Volume)", 
        "% w/w (Weight/Weight)", "% v/v (Volume/Volume)"
    ]
    c_col1, c_col2 = st.columns([2, 1])
    with c_col1:
        c_from = st.selectbox("หน่วยต้นทาง:", conc_units, key="conc_from")
        c_to = st.selectbox("หน่วยปลายทาง:", conc_units, index=1, key="conc_to")
        c_val = st.number_input(f"ระบุค่าความเข้มข้น ({c_from}):", value=1.0, step=0.1, format="%.4f")
    
    needs_mw = "Molarity" in c_from or "Molarity" in c_to
    needs_density = any(x in [c_from, c_to] for x in ["% w/w", "% v/v"])
    
    with c_col2:
        st.markdown('<div class="param-box">', unsafe_allow_html=True)
        st.caption("⚙️ พารามิเตอร์เพิ่มเติม")
        mw = st.number_input("Molecular Weight (g/mol):", value=1.0, step=0.1) if needs_mw else 1.0
        density = st.number_input("Density (g/mL):", value=1.0, format="%.4f") if needs_density else 1.0
        purity = st.number_input("% Purity (1-100):", value=100.0) / 100.0
        st.markdown('</div>', unsafe_allow_html=True)

    # Logic การแปลงพื้นฐาน (Simplified)
    base_mg_l = 0.0
    if c_from in ["mg/L (Milligrams per Liter)", "ppm (Parts per Million)"]: base_mg_l = c_val
    elif c_from == "Molarity (M - Mol/L)": base_mg_l = c_val * mw * 1000
    elif c_from == "% w/v (Weight/Volume)": base_mg_l = c_val * 10000
    
    base_mg_l = base_mg_l * purity
    
    final_conc = 0.0
    if c_to in ["mg/L (Milligrams per Liter)", "ppm (Parts per Million)"]: final_conc = base_mg_l
    elif c_to == "Molarity (M - Mol/L)": final_conc = base_mg_l / (mw * 1000)
    elif c_to == "% w/v (Weight/Volume)": final_conc = base_mg_l / 10000
    
    st.markdown(f"""
        <div class="result-container">
            <p class="highlight-label">ผลลัพธ์ในหน่วย {c_to}</p>
            <p class="result-value">{final_conc:,.4f}</p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

# --- 1.5 การแปลงหน่วยความเข้มข้นน้ำตาล (Sugar Units Conversion) ---

if show_sugar_conv:
    st.subheader("🍭 1.5 การแปลงหน่วยความเข้มข้นน้ำตาล (Sugar Units)")
    st.markdown("""
        <div class='info-card'>
            <b>เกณฑ์การคำนวณ:</b> ยึดตามมาตรฐาน 1 Brix = 1.04 x Plato 
            (หรือ 1 Plato ≈ 0.96 Brix ในเชิงสัดส่วนความเข้มข้น)
        </div>
    """, unsafe_allow_html=True)
    
    col_u1, col_u2 = st.columns([1, 2])
    
    with col_u1:
        s_unit = st.selectbox("เลือกหน่วยต้นทาง:", ["Specific Gravity (SG)", "Brix (°Bx)", "Baumé (°Bé)", "Plato (°P)"], key="sugar_conv_unit")
        s_val = st.number_input("ระบุค่าที่วัดได้:", 
                               value=1.050 if "SG" in s_unit else (12.0 if "Bx" in s_unit or "P" in s_unit else 7.0), 
                               format="%.3f" if "SG" in s_unit else "%.2f", 
                               key="sugar_conv_val")

    # --- Logic การคำนวณใหม่ ---
    if "SG" in s_unit:
        calc_sg = s_val
        res_brix = (((182.4601 * calc_sg - 775.6821) * calc_sg + 1262.7794) * calc_sg - 669.5622)
        res_plato = res_brix / 1.04
    elif "Brix" in s_unit:
        res_brix = s_val
        res_plato = res_brix / 1.04
        calc_sg = (res_brix / (258.6 - ((res_brix / 258.2) * 227.1))) + 1
    elif "Plato" in s_unit:
        res_plato = s_val
        res_brix = res_plato * 1.04  # ตามโจทย์: 1 Brix = 1.04 Plato
        calc_sg = (res_brix / (258.6 - ((res_brix / 258.2) * 227.1))) + 1
    elif "Baumé" in s_unit:
        calc_sg = 145 / (145 - s_val)
        res_brix = (((182.4601 * calc_sg - 775.6821) * calc_sg + 1262.7794) * calc_sg - 669.5622)
        res_plato = res_brix / 1.04

    res_be = 145 - (145 / calc_sg)

    with col_u2:
        st.markdown(f"""
            <div class="result-container" style="background-color: #fdf2e9; border-left: 8px solid #e67e22;">
                <p class="highlight-label">ผลการเทียบเคียง (Ratio 1:1.04)</p>
                <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
                    <div style="margin:10px;">
                        <p style="margin:0; font-size:14px;">SG</p>
                        <b style="font-size:24px; color:#d35400;">{calc_sg:.3f}</b>
                    </div>
                    <div style="margin:10px;">
                        <p style="margin:0; font-size:14px;">Brix (°Bx)</p>
                        <b style="font-size:24px; color:#d35400;">{max(res_brix, 0.0):.2f}</b>
                    </div>
                    <div style="margin:10px;">
                        <p style="margin:0; font-size:14px;">Baumé (°Bé)</p>
                        <b style="font-size:24px; color:#d35400;">{max(res_be, 0.0):.2f}</b>
                    </div>
                    <div style="margin:10px;">
                        <p style="margin:0; font-size:14px;">Plato (°P)</p>
                        <b style="font-size:24px; color:#d35400;">{max(res_plato, 0.0):.2f}</b>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- 1.6 หน่วยแอลกอฮอล์ (% Alcohol Strength) ---
if show_alc:
    st.subheader("🥃 1.6 การแปลงหน่วยความเข้มข้นแอลกอฮอล์")
    a_col1, a_col2 = st.columns(2)
    with a_col1:
        a_from = st.radio("เลือกหน่วยต้นทาง:", ["% ABV", "US Proof", "UK Proof"], horizontal=True, key="alc_from_unit")
        a_val = st.number_input(f"ระบุค่าแอลกอฮอล์ ({a_from}):", value=40.0)
    with a_col2:
        if a_from == "% ABV": abv = a_val
        elif a_from == "US Proof": abv = a_val / 2
        else: abv = a_val / 1.7512
        
        st.markdown(f"""
            <div class="result-container">
                <p class="highlight-label">การเปรียบเทียบค่า</p>
                <div style="display: flex; justify-content: space-around; align-items: center;">
                    <div style="text-align:center;"><p style="margin:0;">ABV</p><b style="font-size:24px; color:#d35400;">{abv:.2f}%</b></div>
                    <div style="text-align:center;"><p style="margin:0;">US Proof</p><b style="font-size:24px;">{abv*2:.2f}</b></div>
                    <div style="text-align:center;"><p style="margin:0;">UK Proof</p><b style="font-size:24px;">{abv*1.7512:.2f}</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    st.divider()

# ==========================================
# CATEGORY 2: การวัดและการคำนวณผล
# ==========================================

# --- 2.1 การปรับค่า Hydrometer ตามค่าอุณหภูมิ (Hydrometer Reading & Correction) ---
if show_reading:
    st.subheader("🔍 2.1 การปรับค่า Hydrometer ตามค่าอุณหภูมิ")
    st.markdown("<div class='info-card'>ใช้ปรับค่า SG ที่อ่านได้จาก Hydrometer ตามอุณหภูมิจริงของตัวอย่าง</div>", unsafe_allow_html=True)
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        measured_sg = st.number_input("ค่า SG ที่อ่านได้:", value=1.050, format="%.3f", key="cat2_meas_sg")
        sample_temp = st.number_input("อุณหภูมิของตัวอย่าง (°C):", value=25.0, key="cat2_sample_t")
        calibrate_temp = st.number_input("อุณหภูมิที่ Hydrometer ปรับตั้งไว้ (Standard Temp):", value=20.0, key="cat2_cal_t")

        # --- เพิ่มการตรวจสอบ Input Validation ---
        if sample_temp > 40.0:
            st.warning("⚠️ อุณหภูมิสูงเกิน 40°C: ความหนาแน่นของของเหลวอาจเปลี่ยนแปลงไม่เป็นเส้นตรง ค่าคำนวณอาจคลาดเคลื่อน")
        elif sample_temp < 10.0:
            st.warning("⚠️ อุณหภูมิต่ำกว่า 10°C: ความหนืดอาจส่งผลต่อการลอยตัวของ Hydrometer")

    # ฟังก์ชันคำนวณการปรับแก้ SG ตามอุณหภูมิ (Polynomial 3rd order)
    def correct_sg(mg, t, tr):
        def density_formula(temp):
            # สูตรคำนวณความหนาแน่นสัมพัทธ์ของน้ำที่อุณหภูมิต่างๆ
            return 1.00130346 - 0.000134722124 * temp + 0.00000204052596 * (temp**2) - 0.00000000232820948 * (temp**3)
        return mg * (density_formula(t) / density_formula(tr))

    corrected_sg = correct_sg(measured_sg, sample_temp, calibrate_temp)

    with col_r2:
        st.markdown(f"""
            <div class="result-container">
                <p class="highlight-label">ค่า SG ที่ปรับแก้แล้ว (Corrected SG)</p>
                <p class="result-value">{corrected_sg:.3f}</p>
                <p style="color: #7f8c8d; font-size: 14px;">(คำนวณเทียบกับอุณหภูมิปรับตั้ง {calibrate_temp}°C)</p>
            </div>
        """, unsafe_allow_html=True)
    st.divider()

# --- 2.2 การประมาณการแอลกอฮอล์ (Alcohol Estimation) ---
if show_abv_est:
    st.subheader("📈 2.2 การประมาณการณ์ปริมาณแอลกอฮอล์")
    
    # แก้ไขปัญหา NameError โดยระบุชื่อตัวแปรให้ตรงกับจำนวนรายการใน st.tabs
    tab_sg, tab_brix, tab_be, tab_plato = st.tabs([
        "📏 Hydrometer (SG)", 
        "🔦 Refractometer (Brix)", 
        "🍇 Baumé (°Bé)", 
        "🍺 Plato (°P)"
    ])

    # 1. Tab SG
    with tab_sg:
        c1, c2 = st.columns(2)
        with c1:
            og_sg_22 = st.number_input("Original Gravity (OG):", value=1.050, format="%.3f", key="og_sg_cat22")
            fg_sg_22 = st.number_input("Final Gravity (FG):", value=1.010, format="%.3f", key="fg_sg_cat22")
        with c2:
            res = calculate_abv(og_sg_22, fg_sg_22, "SG", yeast_eff)
            st.markdown(f'<div class="result-container"><p>ประมาณการ ABV</p><p class="result-value">{res:.2f} %</p></div>', unsafe_allow_html=True)
        # --- เพิ่มการตรวจสอบ Input Validation ---
        if res > 15.0:
            st.warning("⚠️ แอลกอฮอล์เกิน 15 % ABV : ค่าคำนวณอาจคลาดเคลื่อนจากความเป็นจริง เนื่องจากยีสต์อาจไม่สามารถทนทานได้")
        elif res < 2.0:
            st.warning("⚠️ แอลกอฮอล์ต่ำกว่า 2 % ABV: โอกาสการปนเปื้อนสูง ควรตรวจสอบความสะอาดของอุปกรณ์และวัตถุดิบ")

    # 2. Tab Brix
    with tab_brix:
        c1, c2 = st.columns(2)
        with c1:
            og_bx_22 = st.number_input("Original Brix:", value=13.0, key="og_bx_cat22")
            fg_bx_22 = st.number_input("Final Brix:", value=6.0, key="fg_bx_cat22")
        with c2:
            res = calculate_abv(og_bx_22, fg_bx_22, "Brix", yeast_eff)
            st.markdown(f'<div class="result-container"><p>ประมาณการ ABV</p><p class="result-value">{res:.2f} %</p></div>', unsafe_allow_html=True)
        # --- เพิ่มการตรวจสอบ Input Validation ---
        if res > 15.0:
            st.warning("⚠️ แอลกอฮอล์เกิน 15 % ABV : ค่าคำนวณอาจคลาดเคลื่อนจากความเป็นจริง เนื่องจากยีสต์อาจไม่สามารถทนทานได้")
        elif res < 2.0:
            st.warning("⚠️ แอลกอฮอล์ต่ำกว่า 2 % ABV: โอกาสการปนเปื้อนสูง ควรตรวจสอบความสะอาดของอุปกรณ์และวัตถุดิบ")

    # 3. Tab Baumé
    with tab_be:
        c1, c2 = st.columns(2)
        with c1:
            og_be_22 = st.number_input("Original Baumé (°Bé):", value=7.0, key="og_be_cat22")
            fg_be_22 = st.number_input("Final Baumé (°Bé):", value=1.0, key="fg_be_cat22")
        with c2:
            res = calculate_abv(og_be_22, fg_be_22, "Baumé", yeast_eff)
            st.markdown(f'<div class="result-container"><p>ประมาณการ ABV</p><p class="result-value">{res:.2f} %</p></div>', unsafe_allow_html=True)
        # --- เพิ่มการตรวจสอบ Input Validation ---
        if res > 15.0:
            st.warning("⚠️ แอลกอฮอล์เกิน 15 % ABV : ค่าคำนวณอาจคลาดเคลื่อนจากความเป็นจริง เนื่องจากยีสต์อาจไม่สามารถทนทานได้")
        elif res < 2.0:
            st.warning("⚠️ แอลกอฮอล์ต่ำกว่า 2 % ABV: โอกาสการปนเปื้อนสูง ควรตรวจสอบความสะอาดของอุปกรณ์และวัตถุดิบ")

    # 4. Tab Plato (สำหรับเบียร์)
    with tab_plato:
        st.markdown("<div class='info-card'><b>หน่วย Plato:</b> นิยมใช้ในการทำเบียร์เพื่อบอกความเข้มข้นของน้ำตาลมอลต์และสารอาหารในน้ำ Wort (1 °P ≈ 4 จของ SG)</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            og_p_22 = st.number_input("Original Plato (°P):", value=12.0, key="og_p_cat22")
            fg_p_22 = st.number_input("Final Plato (°P):", value=2.5, key="fg_p_cat22")
            # แปลง Plato เป็น SG: SG = 259 / (259 - Plato)
            og_sg_p = 259 / (259 - og_p_22)
            fg_sg_p = 259 / (259 - fg_p_22)
        with c2:
            res = calculate_abv(og_sg_p, fg_sg_p, "SG", yeast_eff)
            st.markdown(f"""
                <div class="result-container">
                    <p>ประมาณการ ABV (Plato)</p>
                    <p class="result-value">{res:.2f} %</p>
                    <p style='font-size:12px; color:gray;'>เทียบเท่า SG: {og_sg_p:.3f} to {fg_sg_p:.3f}</p>
                </div>
            """, unsafe_allow_html=True)
                    # --- เพิ่มการตรวจสอบ Input Validation ---
        if res > 15.0:
            st.warning("⚠️ แอลกอฮอล์เกิน 15 % ABV : ค่าคำนวณอาจคลาดเคลื่อนจากความเป็นจริง เนื่องจากยีสต์อาจไม่สามารถทนทานได้")
        elif res < 2.0:
            st.warning("⚠️ แอลกอฮอล์ต่ำกว่า 2 % ABV: โอกาสการปนเปื้อนสูง ควรตรวจสอบความสะอาดของอุปกรณ์และวัตถุดิบ")
    st.divider()

# --- 2.3 การคำนวณความขม (IBU Calculator - Tinseth Method) ---
if show_ibu:
    st.subheader("🌱 2.3 การคำนวณความขม (IBU Calculator) ของฮอปส์ในเบียร์")
    
    # --- 1. เพิ่มคู่มือระดับความขม (Bitterness Guide) ---
    with st.expander("📖 คู่มือระดับความขมและสไตล์เบียร์ (Bitterness Guide)"):
        bitter_data = pd.DataFrame({
            "สไตล์เบียร์": [
                "Light Lagers / Wheat Beers", 
                "Pilsners / Amber Ales", 
                "IPAs / Pale Ales", 
                "Double IPAs / Imperial Stouts"
            ],
            "ระดับความขม (IBU)": ["8 – 20", "25 – 45", "50 – 70", "75+"],
            "ความรู้สึก (Bitterness)": [
                "ขมน้อยมาก นุ่มนวล", 
                "ขมปานกลาง สดชื่น", 
                "ขมมาก เน้นฮอปส์", 
                "ขมหนักแน่น เข้มข้น"
            ]
        })
        st.table(bitter_data)

    # ฟังก์ชันช่วยดึงคำอธิบายความขมตามค่า IBU
    def get_bitterness_desc(ibu_val):
        if ibu_val < 20: return "🍺 สไตล์ Light Lagers / Wheat: ขมน้อยมาก นุ่มนวล"
        elif 20 <= ibu_val < 45: return "🍺 สไตล์ Pilsners / Amber Ales: ขมปานกลาง สดชื่น"
        elif 45 <= ibu_val < 75: return "🍺 สไตล์ IPAs / Pale Ales: ขมจัดจ้าน เน้นฮอปส์"
        else: return "🍺 สไตล์ Double IPAs / Imperial Stouts: ขมหนักแน่น เข้มข้น"

    st.markdown("<div class='info-card'>คำนวณค่า IBU โดยใช้สูตร Tinseth Method</div>", unsafe_allow_html=True)
    
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        hop_wt = st.number_input("น้ำหนักฮอปส์ (กรัม):", value=30.0, step=1.0, key="cat23_hop_wt")
        alpha_a = st.number_input("Alpha Acid ของฮอปส์ (%):", value=12.0, step=0.1, key="cat23_alpha")
        boil_t = st.number_input("เวลาที่ต้ม (นาที):", value=60, step=1, key="cat23_time")
        batch_v = st.number_input("ปริมาตรเบียร์สุดท้าย (ลิตร):", value=20.0, step=0.5, key="cat23_vol")
        boil_sg = st.number_input("ค่า SG ขณะต้ม (Boil Gravity):", value=1.050, format="%.3f", key="cat23_boilsg")

    # คำนวณ IBU ตามสูตร Tinseth
    bigness_f = 1.65 * (0.000125 ** (boil_sg - 1))
    time_f = (1 - np.exp(-0.04 * boil_t)) / 4.15
    utilization = bigness_f * time_f
    ibu_res = (alpha_a * hop_wt * utilization * 10) / batch_v

    with col_i2:
        st.markdown(f"""
            <div class="result-container" style="background-color: #fef5e7; border-left: 8px solid #f39c12;">
                <p class="highlight-label">ค่าความขมที่คำนวณได้</p>
                <p class="result-value" style="color:#d35400;">{ibu_res:.2f} IBU</p>
                <hr>
                <p style="font-size:16px; font-weight:bold; color:#a04000;">{get_bitterness_desc(ibu_res)}</p>
                <p style="font-size:14px; color:#7f8c8d; margin-top:10px;">การดึงสารขม (Utilization): {utilization*100:.2f}%</p>
            </div>
        """, unsafe_allow_html=True)
    st.divider()

# --- 2.4 การอัดก๊าซและน้ำตาล Priming (Carbonation Calculator) ---

if show_carb:
    st.subheader("🫧 2.4 การอัดก๊าซ (Carbonation)")
    
    # --- เพิ่มตารางอ้างอิง Mouthfeel & Style ---
    with st.expander("📖 คู่มือระดับความซ่าและสไตล์เบียร์ (Mouthfeel Guide)"):
        guide_data = pd.DataFrame({
            "สไตล์เบียร์": ["British Ales / Stouts", "Lagers / Pilsners", "Wheat Beers (Hefeweizen)", "น้ำอัดลม (Soda)"],
            "ระดับ CO2 (Volumes)": ["1.5 – 2.0", "2.4 – 2.6", "3.0 – 4.5", "3.5 – 5.0"],
            "ความรู้สึก (Mouthfeel)": ["ซ่าน้อย เน้นรสมอลต์", "ซ่าปานกลาง สดชื่น มาตรฐานทั่วไป", "ซ่ามาก ฟองฟูฟ่อง", "ซ่าจัดจ้าน"]
        })
        st.table(guide_data)

    tab_priming, tab_force = st.tabs(["🍬 การเติมน้ำตาลในขวด (Priming)", "🕹️ การอัดแรงดันถัง (Force Carbonation)"])

    # ฟังก์ชันช่วยดึงค่า Mouthfeel ตามระดับ Volumes
    def get_mouthfeel_desc(vols):
        if vols < 2.0: return "🍺 สไตล์ British Ales/Stouts: ซ่าน้อย เน้นรสมอลต์"
        elif 2.0 <= vols < 2.3: return "🍺 สไตล์ Ales ทั่วไป: ซ่ากำลังดี"
        elif 2.3 <= vols < 2.7: return "🍺 สไตล์ Lagers/Pilsners: ซ่าปานกลาง สดชื่น มาตรฐาน"
        elif 2.7 <= vols < 3.0: return "🍺 สไตล์ Strong Ales: ซ่าสูง"
        elif 3.0 <= vols < 4.5: return "🍺 สไตล์ Wheat Beers: ซ่ามาก ฟองฟูฟ่อง"
        else: return "🥤 สไตล์ Soda: ซ่าจัดจ้าน"

    # 2.4.1 Priming Sugar
    with tab_priming:
        st.markdown("<div class='info-card'>คำนวณน้ำตาลสำหรับสร้างก๊าซในขวด (Natural Carbonation)</div>", unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            t_co2_p = st.slider("ระดับ CO2 ที่ต้องการ (Volumes):", 1.5, 5.0, 2.4, key="cat24_target_p")
            # แสดง Mouthfeel ทันทีใต้ Slider
            st.info(get_mouthfeel_desc(t_co2_p))
            
            beer_t_p = st.number_input("อุณหภูมิเบียร์ขณะบรรจุ (°C):", value=20.0, key="cat24_temp_p")
            final_vol = st.number_input("ปริมาตรเบียร์ที่บรรจุ (ลิตร):", value=19.0, key="cat24_vol_p")
            s_type_p = st.selectbox("ประเภทน้ำตาล:", ["Sucrose (Table Sugar)", "Dextrose (Corn Sugar)", "DME (Dimethyl Ether)"], key="cat24_sugar_p")

        existing_co2 = 3.0378 - (0.050062 * beer_t_p) + (0.00026555 * (beer_t_p**2))
        needed_co2 = max(t_co2_p - existing_co2, 0.0)
        sugar_map = {"Sucrose (Table Sugar)": 4.0, "Dextrose (Corn Sugar)": 4.4, "DME (Dimethyl Ether)": 6.3}
        sugar_gram = needed_co2 * final_vol * sugar_map[s_type_p]

        with col_c2:
            st.markdown(f"""
                <div class="result-container" style="background-color: #ebf5fb; border-left: 8px solid #3498db;">
                    <p class="highlight-label">ปริมาณน้ำตาลที่ต้องใช้</p>
                    <p class="result-value" style="color:#2980b9;">{sugar_gram:.2f} กรัม</p>
                    <hr>
                    <p style="margin:0;">CO2 เดิมในเบียร์: {existing_co2:.2f} Vol</p>
                    <p style="margin:0;">ต้องเติมเพิ่มอีก: {needed_co2:.2f} Vol</p>
                </div>
            """, unsafe_allow_html=True)

    # 2.4.2 Force Carbonation
    with tab_force:
        st.markdown("<div class='info-card'>คำนวณแรงดันที่เกจ (PSI/Bar) ตามอุณหภูมิถัง Keg</div>", unsafe_allow_html=True)
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            t_co2_f = st.slider("ระดับ CO2 ที่ต้องการ (Volumes):", 1.5, 5.0, 2.4, key="cat24_target_f")
            # แสดง Mouthfeel ทันทีใต้ Slider
            st.info(get_mouthfeel_desc(t_co2_f))
            
            keg_temp = st.number_input("อุณหภูมิเบียร์ในถัง Keg (°C):", value=4.0, key="cat24_temp_f")
            
        temp_f = (keg_temp * 1.8) + 32
        psi_needed = -14.695 + ( (t_co2_f + 0.003342) / (0.01821 + 0.09011 * np.exp(-0.01 * temp_f)) )
        bar_needed = psi_needed * 0.0689476

        with col_f2:
            st.markdown(f"""
                <div class="result-container" style="background-color: #f4ecf7; border-left: 8px solid #8e44ad;">
                    <p class="highlight-label">แรงดันที่ต้องตั้ง (Regulator Setting)</p>
                    <p class="result-value" style="color:#6c3483;">{max(psi_needed, 0.0):.2f} PSI</p>
                    <p style="font-size:24px; font-weight:bold;">({max(bar_needed, 0.0):.2f} Bar)</p>
                    <hr>
                    <p style="font-size:14px; color:#7f8c8d;">* อิงตามอุณหภูมิ {keg_temp} °C</p>
                </div>
            """, unsafe_allow_html=True)
    st.divider()

# ==========================================
# CATEGORY 3: การปรับกรดและเคมี
# ==========================================

if show_acid:
    st.subheader("🍋 3.1 การเติมกรดต่างๆ (Acids Addition)")
    
    st.markdown('<div class="info-card">คำนวณปริมาณกรดที่ต้องเติมเพื่อเพิ่มความเปรี้ยวหรือปรับค่า pH</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        acid_type = st.selectbox("ชนิดของกรด:", ["Tartaric Acid (กรดทาร์ทาริก)", "Citric Acid (กรดมะนาว)", "Malic Acid (กรดแอปเปิ้ล)", "Lactic Acid (กรดนม)", "Ascorbic Acid (วิตามินซี)", "Sorbic Acid (กรดซอร์บิก)"])
        target_vol = st.number_input("ปริมาตรน้ำไวน์/สุรา (L):", value=100.0, key="acid_vol_v3")
        desired_increase = st.number_input("ปริมาณกรดที่ต้องการเพิ่ม (g/L):", value=1.0, step=0.1)
    with col2:
        total_acid_g = target_vol * desired_increase
        # #Logic: g/L to %w/v (g/100mL) -> g/L / 10
        percent_wv = desired_increase / 10
        # #Logic: g/L to g/100L -> g/L * 100
        equiv_g_hL = desired_increase * 100
        
        st.markdown(f"""
            <div class="result-container">
                <p class="highlight-label">ปริมาณ {acid_type} ที่ต้องเติม</p>
                <p class="result-value">{total_acid_g:.4f} กรัม</p>
                <hr style="border: 0.5px solid #e67e22;">
                <p class="highlight-label">คิดเป็นความเข้มข้น</p>
                <p class="sub-result">{percent_wv:.4f} % w/v</p>
                <p style="color: #7f8c8d; font-size: 14px;">(เทียบเท่า {equiv_g_hL:.2f} g ต่อ 100 ลิตร)</p>
            </div>
        """, unsafe_allow_html=True)
    st.divider()

if show_ta:
    st.subheader("🧪 3.2 Titratable Acidity (TA)")
    
    st.markdown('<div class="info-card">คำนวณค่า TA เทียบเป็นกรดทาร์ทาริกจากการไทเทรต</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        sample_vol = st.number_input("ปริมาตรตัวอย่าง (mL):", value=5.0)
        titrant_vol = st.number_input("ปริมาตร NaOH ที่ใช้ (mL):", value=3.5, step=0.1)
        naoh_m = st.number_input("ความเข้มข้น NaOH (M):", value=0.1, format="%.4f")
    with col2:
        # #Formula: TA (g/L Tartaric) = (V_titrant * M_naoh * 75) / V_sample
        ta_res_gl = (titrant_vol * naoh_m * 75) / sample_vol
        percent_wv = ta_res_gl / 10
        equiv_g_hL = ta_res_gl * 100
        
        st.markdown(f"""
            <div class="result-container">
                <p class="highlight-label">ค่า TA (เทียบเท่า Tartaric Acid)</p>
                <p class="result-value">{ta_res_gl:.4f} g/L</p>
                <hr style="border: 0.5px solid #e67e22;">
                <p class="highlight-label">คิดเป็นความเข้มข้น</p>
                <p class="sub-result">{percent_wv:.4f} % w/v</p>
                <p style="color: #7f8c8d; font-size: 14px;">(เทียบเท่า {equiv_g_hL:.4f} g ต่อ 100 ลิตร)</p>
            </div>
        """, unsafe_allow_html=True)
    st.divider()


# ==========================================
# CATEGORY 4: การเติมสารปรุงแต่ง
# ==========================================

if show_so2:
    st.subheader("🛡️ 4.1 การเติม SO2 (Potassium Metabisulphite - KMS)")
    
    col1, col2 = st.columns(2)
    with col1:
        v_s = st.number_input("ปริมาตรน้ำไวน์ (L):", value=100.0, key="v_so2")
        ppm_target = st.number_input("SO2 ที่ต้องการเพิ่ม (ppm หรือ mg/L):", value=100.00)
        purity = st.number_input("ปริมาณ SO2 ที่ปลดปล่อยจาก KMS (%):", value=57.6)
    with col2:
        kms_g = (v_s * ppm_target) / (purity * 10)
        # ppm to g/L: ppm / 1000
        # g/L to %w/v: (ppm/1000) / 10
        percent_wv = ppm_target / 10000
        equiv_g_hL = ppm_target / 10
        
        st.markdown(f"""
            <div class="result-container">
                <p class="highlight-label">ปริมาณ KMS ที่ต้องเติม</p>
                <p class="result-value">{kms_g:.4f} กรัม</p>
                <hr style="border: 0.5px solid #e67e22;">
                <p class="highlight-label">คิดเป็นความเข้มข้น (SO2)</p>
                <p class="sub-result">{percent_wv:.4f} % w/v</p>
                <p style="color: #7f8c8d; font-size: 14px;">(เทียบเท่า {equiv_g_hL:.4f} g ต่อ 100 ลิตร)</p>
            </div>
        """, unsafe_allow_html=True)
    st.divider()

if show_nutrients:
    st.subheader("🧬 4.2 สารอาหารและแทนนิน (Nutrients & Tannin)")
    
    col1, col2 = st.columns(2)
    with col1:
        add_type = st.radio("ชนิดสาร:", ["DAP (Diammonium Phosphate)", "Enological Tannin"])
        v_n = st.number_input("ปริมาตรของเหลว (L):", value=100.0, key="v_nut")
        rate = st.number_input("อัตราส่วนการใช้ (กรัม ต่อ 100 ลิตร):", value=100.0)
    with col2:
        total_n = (v_n / 100) * rate
        percent_wv = rate / 1000 # (rate g / 100,000 mL) * 100
        
        st.markdown(f"""
            <div class="result-container">
                <p class="highlight-label">ปริมาณ {add_type} ที่ต้องเติม</p>
                <p class="result-value">{total_n:.4f} กรัม</p>
                <hr style="border: 0.5px solid #e67e22;">
                <p class="highlight-label">คิดเป็นความเข้มข้น</p>
                <p class="sub-result">{percent_wv:.4f} % w/v</p>
                <p style="color: #7f8c8d; font-size: 14px;">(เทียบเท่า {rate:.4f} g ต่อ 100 ลิตร)</p>
            </div>
        """, unsafe_allow_html=True)
    st.divider()

# ==========================================
# CATEGORY 5: การทำให้ใสและคงตัว (Fining & Stabilization)
# ==========================================

if show_fining:
    st.subheader("✨ 5.1 การทำให้ใสและกำจัดสี/กลิ่น (Fining & Carbon)")
    
    col1, col2 = st.columns(2)
    with col1:
        fining_agent = st.selectbox("ชนิดของสาร:", ["Gelatin (เจลาติน)", "Activated Carbon (คาร์บอน)", "Bentonite", "Egg White"])
        v_fining = st.number_input("ปริมาตรของเหลว (L):", value=100.0, key="v_fining")
        rate_fining = st.number_input("อัตราส่วนการใช้ (กรัม ต่อ 100 ลิตร):", value=10.0, step=1.0)
    with col2:
        total_fining_g = (v_fining / 100) * rate_fining
        percent_wv = rate_fining / 1000
        st.markdown(f"""
            <div class="result-container">
                <p class="highlight-label">ปริมาณ {fining_agent} ที่ต้องใช้</p>
                <p class="result-value">{total_fining_g:.4f} กรัม</p>
                <hr style="border: 0.5px solid #e67e22;">
                <p class="highlight-label">คิดเป็นความเข้มข้น</p>
                <p class="sub-result">{percent_wv:.4f} % w/v</p>
                <p style="color: #7f8c8d; font-size: 14px;">(เทียบเท่า {rate_fining:.2f} g ต่อ 100 ลิตร)</p>
            </div>
        """, unsafe_allow_html=True)
    st.divider()

if show_stabilize:
    st.subheader("🧊 5.2 การคงตัวทางเคมี (Sorbic Acid / Potassium Sorbate)")
    
    st.markdown('<div class="info-card">ใช้สำหรับป้องกันการหมักซ้ำ (Re-fermentation) ในไวน์ที่มีน้ำตาลหลงเหลืออยู่</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        v_stab = st.number_input("ปริมาตรน้ำไวน์ (L):", value=100.0, key="v_stab")
        target_sorbic = st.number_input("Sorbic Acid ที่ต้องการ (ppm หรือ mg/L):", value=200.0, step=10.0)
        # Sorbic acid is usually added as Potassium Sorbate which is ~75% sorbic acid
        sorbate_purity = st.number_input("ความบริสุทธิ์ของ Sorbate (โดยทั่วไป 75%):", value=75.0)
    with col2:
        # grams = (Vol * ppm) / (Purity * 10)
        total_sorbate_g = (v_stab * target_sorbic) / (sorbate_purity * 10)
        percent_wv = target_sorbic / 10000
        st.markdown(f"""
            <div class="result-container">
                <p class="highlight-label">ปริมาณ Potassium Sorbate ที่ต้องใช้</p>
                <p class="result-value">{total_sorbate_g:.4f} กรัม</p>
                <hr style="border: 0.5px solid #e67e22;">
                <p class="highlight-label">คิดเป็นความเข้มข้น (Sorbic Acid)</p>
                <p class="sub-result">{percent_wv:.4f} % w/v</p>
                <p style="color: #7f8c8d; font-size: 14px;">(เทียบเท่า {target_sorbic/10:.2f} g ต่อ 100 ลิตร)</p>
            </div>
        """, unsafe_allow_html=True)
    st.divider()

# ==========================================
# CATEGORY 6: การปรับหวาน การผสม และการเจือจาง
# ==========================================

if show_pearson:
    st.subheader("⚖️ 6.1 การคำนวณสัดส่วนการผสม (Pearson Square)")
    
    st.markdown('<div class="info-card">ใช้สำหรับหาปริมาณของ 2 ชนิดที่มีความเข้มข้นต่างกัน เช่น ความหวาน เพื่อให้ได้ค่าที่ต้องการ</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        high_val = st.number_input("ค่าความหวานน้ำตาลเข้มข้น (เช่น น้ำตาลแห้ง 100% Brix ):", value=100.0)
        low_val = st.number_input("ค่าความหวานเริ่มต้น (เช่น ส่าเหล้า 10%):", value=10.0)
        target_val = st.number_input("ค่าความหวานที่ต้องการ (Target):", value=18.0)
        total_desired_vol = st.number_input("ปริมาตรรวมที่ต้องการผลิต (L):", value=100.0)
    with col2:
        if high_val > target_val > low_val:
            parts_high = target_val - low_val
            parts_low = high_val - target_val
            total_parts = parts_high + parts_low
            
            vol_high = (parts_high / total_parts) * total_desired_vol
            vol_low = (parts_low / total_parts) * total_desired_vol
            
            st.markdown(f"""
                <div class="result-container">
                    <p class="highlight-label">สัดส่วนการผสมเพื่อให้ได้ {total_desired_vol} L</p>
                    <p class="sub-result" style="color:#c0392b;">ต้องใช้น้ำตาลเพิ่ม: {vol_high:.4f} kg</p>
                    <p class="sub-result" style="color:#2980b9;">ปริมาตรรวม: {vol_low:.4f} L</p>
                    <hr style="border: 0.5px solid #e67e22;">
                    <p style="color: #7f8c8d; font-size: 14px;">ผสม {vol_high:.4f} L และ {vol_low:.4f} L เข้าด้วยกัน</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("ค่าเป้าหมายที่ต้องการต้องมีค่าสูงกว่าค่าความหวานเริ่มต้นและต่ำกว่าค่าความหวานน้ำตาลเข้มข้น")
    st.divider()


if show_dilution:
    st.subheader("💧 6.2 การเจือจางแอลกอฮอล์ด้วยน้ำ (Dilution) ด้วยสูตร C1*V1 = C2*V2")
    st.markdown("""
            <div class="info-card">
                <b>หมายเหตุ:</b> การเจือจางนี้ใช้ได้กับสารละลายทั่วๆไปกับน้ำเท่านั้น<br><br>
            </div>
        """, unsafe_allow_html=True)
     
    col1, col2 = st.columns(2)
    with col1:
        c1 = st.number_input("ความเข้มข้นแอลกอฮอล์เริ่มต้น (%, C1):", value=70.0, key="c1")
        v1 = st.number_input("ปริมาตรเริ่มต้น (L, V1):", value=10.0, key="v1")
        c2 = st.number_input("ความเข้มข้นแอลกอฮอล์ที่ต้องการ (%, C2):", value=40.0, key="c2")
    with col2:
        if c2 < c1:
            # Formula: V2 = (C1 * V1) / C2
            v2 = (c1 * v1) / c2
            water_added = v2 - v1
            st.markdown(f"""
                <div class="result-container">
                    <p class="highlight-label">ปริมาณน้ำที่ต้องเติม (V2 - V1)</p>
                    <p class="result-value">{water_added:.4f} ลิตร</p>
                    <hr style="border: 0.5px solid #e67e22;">
                    <p class="highlight-label">ปริมาตรรวมหลังเจือจาง (V2)</p>
                    <p class="sub-result">{v2:.4f} ลิตร</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("ความเข้มข้นปลายทางต้องน้อยกว่าเริ่มต้น")

# ==========================================
# CATEGORY 7: การประเมินทางประสาทสัมผัส (Sensory Evaluation)
# ==========================================
if show_sensory:
    st.subheader("👅 7. การประเมินทางประสาทสัมผัส (Sensory Evaluation)")
    
    tab71, tab72 = st.tabs(["🍷 7.1 การประเมินทั่วไป/ไวน์", "🍺 7.2 การประเมินเบียร์ (BJCP Standard)"])

    # --- 7.1 การประเมินทางประสาทสัมผัสทั่วไป (Revised with Radar Chart) ---
    with tab71:
        st.markdown("#### 7.1 การประเมินทางประสาทสัมผัสทั่วไป")
        st.info("ตัวชี้วัด: การดู (Appearance), การดมกลิ่น (Aroma), รสสัมผัส (Palate), รสสัมผัสหลังกลืน (Finish)")
        
        with st.expander("⚙️ ตั้งค่าการประเมินทั่วไป", expanded=True):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                n_eval_gen = st.number_input("จำนวนผู้ประเมิน (คน):", min_value=1, value=5, step=1, key="gen_n_eval")
                n_samp_gen = st.number_input("จำนวนตัวอย่าง (ตัวอย่าง):", min_value=1, value=3, step=1, key="gen_n_samp")
            with col_s2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 เริ่มสร้างแบบประเมินทั่วไป", key="reset_gen_sensory"):
                    codes = random.sample(range(100, 999), n_samp_gen)
                    st.session_state['gen_codes'] = [str(c) for c in codes]
                    cats_gen = ["การดู (Appearance)", "การดมกลิ่น (Aroma)", "รสสัมผัส (Palate)", "รสสัมผัสหลังกลืน (Finish)"]
                    data_gen = []
                    for s in st.session_state['gen_codes']:
                        for e in range(1, n_eval_gen + 1):
                            row = {"ตัวอย่าง": s, "ผู้ประเมินที่": e}
                            for c in cats_gen: row[c] = 0.0
                            data_gen.append(row)
                    st.session_state['gen_master_df'] = pd.DataFrame(data_gen)
                    st.rerun()

        if 'gen_master_df' in st.session_state:
            edited_gen = st.data_editor(st.session_state['gen_master_df'], hide_index=True, use_container_width=True, key="gen_editor")
            
            if st.button("📊 ประมวลผลกราฟทั่วไป", key="btn_gen_chart"):
                cats_gen = ["การดู (Appearance)", "การดมกลิ่น (Aroma)", "รสสัมผัส (Palate)", "รสสัมผัสหลังกลืน (Finish)"]
                
                # 1. คำนวณค่าเฉลี่ย
                gen_summary = []
                for scode in st.session_state['gen_codes']:
                    sdata = edited_gen[edited_gen['ตัวอย่าง'] == scode]
                    sres = {"ตัวอย่าง": scode}
                    for c in cats_gen:
                        sres[c] = round(np.mean(sdata[c]), 2)
                    sres["คะแนนรวมเฉลี่ย"] = round(sum(sres[c] for c in cats_gen), 2)
                    gen_summary.append(sres)
                
                sum_gen_df = pd.DataFrame(gen_summary)
                st.markdown("### 📈 ตารางสรุปคะแนนเฉลี่ย")
                st.dataframe(sum_gen_df, use_container_width=True)

                # 2. พล็อตกราฟใยแมงมุม (Radar Chart)
                g_list = sum_gen_df.to_dict('records')
                chunks = [g_list[i:i + 3] for i in range(0, len(g_list), 3)]
                
                for idx, chunk in enumerate(chunks):
                    st.write(f"**📈 กราฟวิเคราะห์ประสาทสัมผัส ชุดที่ {idx+1}**")
                    fig = go.Figure()
                    for sample in chunk:
                        r_vals = [sample[c] for c in cats_gen]
                        r_vals.append(r_vals[0])
                        fig.add_trace(go.Scatterpolar(
                            r=r_vals,
                            theta=cats_gen + [cats_gen[0]],
                            fill='toself',
                            name=f"Batch {sample['ตัวอย่าง']}"
                        ))
                    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=500)
                    st.plotly_chart(fig, use_container_width=True)

                best_gen = sum_gen_df.loc[sum_gen_df['คะแนนรวมเฉลี่ย'].idxmax(), 'ตัวอย่าง']
                st.success(f"🏆 ตัวอย่างที่มีคะแนนสูงสุดคือ: **{best_gen}**")

    # --- 7.2 สำหรับเบียร์โดยเฉพาะ (BJCP) ---
    with tab72:
        st.markdown("#### 🍺 7.2 การประเมินเบียร์ (BJCP Standard)")
        st.info("ตัวชี้วัด: ฟอง (Head), สี (Color), กลิ่นมอลต์ (Malt), กลิ่นฮอปส์ (Hops)")
        
        with st.expander("⚙️ ตั้งค่าการประเมินเบียร์", expanded=True):
            cb1, cb2 = st.columns(2)
            with cb1:
                n_eval_beer = st.number_input("จำนวนผู้ประเมิน (คน):", min_value=1, value=3, key="beer_n_eval")
                n_samp_beer = st.number_input("จำนวนตัวอย่างเบียร์:", min_value=1, value=3, key="beer_n_samp")
            with cb2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 เริ่มต้นการประเมินเบียร์", key="reset_beer_sensory"):
                    bcodes = random.sample(range(100, 999), n_samp_beer)
                    st.session_state['beer_codes'] = [str(c) for c in bcodes]
                    bjcp_cats = ["ฟอง (Head/Foam)", "สี (Color/Clarity)", "กลิ่นมอลต์ (Malt)", "กลิ่นฮอปส์ (Hops)"]
                    data_beer = []
                    for s in st.session_state['beer_codes']:
                        for e in range(1, n_eval_beer + 1):
                            row = {"ตัวอย่าง": s, "ผู้ประเมินที่": e}
                            for c in bjcp_cats: row[c] = 0.0
                            data_beer.append(row)
                    st.session_state['beer_master_df'] = pd.DataFrame(data_beer)
                    st.rerun()

        if 'beer_master_df' in st.session_state:
            edited_beer = st.data_editor(st.session_state['beer_master_df'], hide_index=True, use_container_width=True, key="beer_editor")
            
            if st.button("📊 ประมวลผลกราฟ BJCP", key="btn_beer_chart"):
                bjcp_cats = ["ฟอง (Head/Foam)", "สี (Color/Clarity)", "กลิ่นมอลต์ (Malt)", "กลิ่นฮอปส์ (Hops)"]
                
                beer_summary = []
                for scode in st.session_state['beer_codes']:
                    sdata = edited_beer[edited_beer['ตัวอย่าง'] == scode]
                    sres = {"ตัวอย่าง": scode}
                    for c in bjcp_cats:
                        sres[c] = round(np.mean(sdata[c]), 2)
                    sres["คะแนนรวมเฉลี่ย"] = round(sum(sres[c] for c in bjcp_cats), 2)
                    beer_summary.append(sres)
                
                sum_beer_df = pd.DataFrame(beer_summary)
                st.dataframe(sum_beer_df, use_container_width=True)

                # 2. พล็อตกราฟใยแมงมุม (Radar Chart)
                blist = sum_beer_df.to_dict('records')
                chunks = [blist[i:i + 3] for i in range(0, len(blist), 3)]
                
                for idx, chunk in enumerate(chunks):
                    st.write(f"**📈 กราฟวิเคราะห์ BJCP ชุดที่ {idx+1}**")
                    fig = go.Figure()
                    for sample in chunk:
                        r_vals = [sample[c] for c in bjcp_cats]
                        r_vals.append(r_vals[0])
                        fig.add_trace(go.Scatterpolar(
                            r=r_vals,
                            theta=bjcp_cats + [bjcp_cats[0]],
                            fill='toself',
                            name=f"Batch {sample['ตัวอย่าง']}"
                        ))
                    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=500)
                    st.plotly_chart(fig, use_container_width=True)

                best_beer = sum_beer_df.loc[sum_beer_df['คะแนนรวมเฉลี่ย'].idxmax(), 'ตัวอย่าง']
                st.success(f"🏆 Batch ที่ดีที่สุดคือ: **{best_beer}**")

    st.divider()

# ==========================================
# CATEGORY 8: การคิดต้นทุนและบันทึกการผลิต (Production Batch Costing)
# ==========================================
if show_costing:
    st.subheader("💰 8. การคิดต้นทุนและวิเคราะห์ผลผลิต (Batch Costing & Yield)")
    
    # --- 8.1 ส่วนบันทึกต้นทุนวัตถุดิบ (Batch Costing) ---
    st.markdown("#### 🛒 8.1 ต้นทุนวัตถุดิบ (Ingredient Costs)")
    
    # กำหนดค่าเริ่มต้นสำหรับตารางต้นทุน
    if 'cost_items' not in st.session_state:
        st.session_state['cost_items'] = pd.DataFrame([
            {"รายการ": "น้ำตาล", "ปริมาณ": 0.0, "หน่วย": "kg", "ราคาต่อหน่วย": 0.0},
            {"รายการ": "ยีสต์", "ปริมาณ": 0.0, "หน่วย": "g", "ราคาต่อหน่วย": 0.0},
            {"รายการ": "ผลไม้/วัตถุดิบหลัก", "ปริมาณ": 0.0, "หน่วย": "kg", "ราคาต่อหน่วย": 0.0},
            {"รายการ": "สารเคมี", "ปริมาณ": 0.0, "หน่วย": "kg", "ราคาต่อหน่วย": 0.0},
            {"รายการ": "อื่นๆ", "ปริมาณ": 0.0, "หน่วย": "unit", "ราคาต่อหน่วย": 0.0}, 
            {"รายการ": "น้ำ", "ปริมาณ": 0.0, "หน่วย": "L", "ราคาต่อหน่วย": 0.0},         
        ])

    cost_df = st.data_editor(
        st.session_state['cost_items'],
        column_config={
            "รายการ": st.column_config.TextColumn("ชื่อวัตถุดิบ", width="medium"),
            "ปริมาณ": st.column_config.NumberColumn("ปริมาณ", format="%.2f"),
            "หน่วย": st.column_config.SelectboxColumn("หน่วย", options=["kg", "g", "L", "mL", "unit"]),
            "ราคาต่อหน่วย": st.column_config.NumberColumn("ราคา/หน่วย (บาท)", format="%.2f"),
        },
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="batch_cost_editor"
    )

    # คำนวณต้นทุนวัตถุดิบรวม
    cost_df['รวม (บาท)'] = cost_df['ปริมาณ'] * cost_df['ราคาต่อหน่วย']
    total_material_cost = cost_df['รวม (บาท)'].sum()

    # --- 8.2 ส่วนวิเคราะห์ผลผลิตและการสูญเสีย (Yield Recovery) ---
    st.divider()
    st.markdown("#### 📉 9.2 การวิเคราะห์ผลผลิต (Yield Recovery)")
    
    col_y1, col_y2 = st.columns([2, 1])
    
    with col_y1:
        st.markdown("<div class='info-card'>บันทึกปริมาตรที่วัดได้จริงในแต่ละขั้นตอน (ลิตร)</div>", unsafe_allow_html=True)
        v_initial = st.number_input("1. ปริมาตรเริ่มต้น (Initial Volume):", min_value=0.0, value=100.0, step=1.0, key="yield_v1")
        v_racking = st.number_input("2. หลังการถ่ายกาก (Post-Racking):", min_value=0.0, value=v_initial * 0.95, step=1.0, key="yield_v2")
        v_filtering = st.number_input("3. หลังการกรอง (Post-Filtering):", min_value=0.0, value=v_racking * 0.98, step=1.0, key="yield_v3")
        v_bottling = st.number_input("4. ปริมาตรที่บรรจุขวดได้ (Final Bottling):", min_value=0.0, value=v_filtering * 0.99, step=1.0, key="yield_v4")

    # คำนวณค่าทางสถิติของ Yield
    total_loss_L = v_initial - v_bottling
    total_loss_pct = (total_loss_L / v_initial * 100) if v_initial > 0 else 0
    recovery_rate = (v_bottling / v_initial * 100) if v_initial > 0 else 0
    cost_per_liter = (total_material_cost / v_bottling) if v_bottling > 0 else 0

    with col_y2:
        st.markdown(f"""
            <div class="result-container" style="background-color: #f4f6f7; border-left: 8px solid #2c3e50;">
                <p class="highlight-label">📊 สรุปต้นทุนและ Yield</p>
                <p style="margin:0;">ต้นทุนวัตถุดิบรวม</p>
                <b style="font-size:28px; color:#2c3e50;">{total_material_cost:,.2f} ฿</b>
                <hr>
                <p style="margin:0;">ต้นทุนต่อลิตร (Final Product)</p>
                <b style="font-size:32px; color:#722f37;">{cost_per_liter:,.2f} ฿/L</b>
                <hr>
                <p style="margin:0;">% ผลผลิต (Recovery Rate)</p>
                <b style="font-size:28px; color:#27ae60;">{recovery_rate:.2f}%</b>
                <p style="margin:0; font-size:14px; color:#e67e22;">สูญเสียรวม: {total_loss_pct:.2f}% ({total_loss_L:,.2f} L)</p>
            </div>
        """, unsafe_allow_html=True)

    # --- 8.3 รายละเอียดการสูญเสียรายขั้นตอน ---
    with st.expander("🔍 ดูรายละเอียดการสูญเสียรายขั้นตอน"):
        loss_racking = v_initial - v_racking
        loss_filtering = v_racking - v_v_filtering if 'v_v_filtering' in locals() else v_racking - v_filtering
        loss_bottling = v_filtering - v_bottling
        
        step_data = pd.DataFrame({
            "ขั้นตอน": ["Racking (การถ่ายกาก)", "Filtering (การกรอง)", "Bottling (การบรรจุ)"],
            "ปริมาตรที่หายไป (L)": [loss_racking, loss_filtering, loss_bottling],
            "% สูญเสียเทียบจุดเริ่มต้น": [
                (loss_racking/v_initial*100), 
                (loss_filtering/v_initial*100), 
                (loss_bottling/v_initial*100)
            ]
        })
        st.table(step_data.style.format({"ปริมาตรที่หายไป (L)": "{:.2f}", "% สูญเสียเทียบจุดเริ่มต้น": "{:.2f}%"}))

    st.divider()

# ==========================================
# CATEGORY 9: การติดตามการหมัก (Fermentation Monitoring)
# ==========================================
if show_ferment:
    st.subheader("📊 9.1 การติดตามการหมักและคาดการณ์แอลกอฮอล์")
    
    with st.expander("📝 1. ตั้งค่าการวัดและเป้าหมาย", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            unit = st.radio("เลือกหน่วยที่ใช้งาน:", ["SG", "Brix (%)", "Baumé (°Bé)", "Plato (°P)"], horizontal=True, key="f_unit")
            batch_id = st.text_input("รหัส Batch:", value="B001")
        
        is_sg = "SG" in unit
        is_be = "Bé" in unit
        is_plato = "Plato" in unit
        
        # ปรับค่า Default ตามหน่วยที่เลือก
        if is_sg: def_og, def_tg = 1.050, 1.010
        elif is_be: def_og, def_tg = 7.0, 1.0
        elif is_plato: def_og, def_tg = 12.0, 2.5
        else: def_og, def_tg = 13.0, 6.0 # Brix
        
        with c2:
            # ใช้ Dynamic Key เพื่อให้ค่า Default เปลี่ยนตามหน่วยทันที
            og_val = st.number_input(f"ค่าเริ่มต้น ({unit}):", 
                                     value=def_og, 
                                     format="%.3f" if is_sg else "%.2f", 
                                     key=f"f_og_val_{unit}")
            
            target_val = st.number_input(f"ค่าเป้าหมาย ({unit}):", 
                                         value=def_tg, 
                                         format="%.3f" if is_sg else "%.2f", 
                                         key=f"f_tg_val_{unit}")
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🆕 เริ่ม Batch ใหม่"):
                today = datetime.now()
                st.session_state['f_data'] = pd.DataFrame([
                    {"Day": i, "Date": (today + timedelta(days=i)).strftime('%Y-%m-%d'), "Value": None} 
                    for i in range(21)
                ])
                st.session_state['alert_played'] = False
                if "f_editor" in st.session_state: del st.session_state["f_editor"]
                st.rerun()

    if 'f_data' in st.session_state:
        # ส่วนบันทึกข้อมูล
        edited = st.data_editor(st.session_state['f_data'], hide_index=True, use_container_width=True, key="f_editor")
        
        # เตรียมข้อมูลสำหรับการคำนวณ
        temp_df = edited.copy()
        temp_df['Value'] = pd.to_numeric(temp_df['Value'], errors='coerce')
        valid_df = temp_df.dropna(subset=['Value']).copy()
        
        if not valid_df.empty:
            # คำนวณ ABV รายวัน (ใช้ Ratio 1.04 สำหรับหน่วย Plato)
            if is_plato:
                valid_df['ABV'] = valid_df['Value'].apply(lambda x: calculate_abv(og_val * 1.04, x * 1.04, "Brix", yeast_eff))
            else:
                valid_df['ABV'] = valid_df['Value'].apply(lambda x: calculate_abv(og_val, x, unit, yeast_eff))
            
            current_val = valid_df['Value'].iloc[-1]
            current_abv = valid_df['ABV'].iloc[-1]
            sugar_break = og_val - ((og_val - target_val) / 3)

            # --- ส่วนการพล็อตกราฟ ---
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Scatter(x=valid_df['Day'], y=valid_df['Value'], name=unit, line=dict(color='#722f37', width=4), mode='lines+markers'), secondary_y=False)
            fig.add_trace(go.Scatter(x=valid_df['Day'], y=valid_df['ABV'], name="ABV (%)", line=dict(color='#2e86c1', width=3, dash='dot'), mode='lines+markers'), secondary_y=True)
            
            fmt = ".3f" if is_sg else ".2f"
            fig.add_hline(y=sugar_break, line_dash="dash", line_color="orange", annotation_text=f"1/3 Break ({sugar_break:{fmt}})", secondary_y=False)
            fig.add_hline(y=target_val, line_dash="dot", line_color="green", annotation_text=f"Target ({target_val:{fmt}})", secondary_y=False)
            
            y1_min = min(target_val, valid_df['Value'].min()) * 0.98
            y1_max = max(og_val, valid_df['Value'].max()) * 1.02
            
            fig.update_layout(title=f"Fermentation Analysis: {batch_id}", template="plotly_white", height=550)
            fig.update_yaxes(title_text=unit, range=[y1_min, y1_max], secondary_y=False)
            fig.update_yaxes(title_text="Alcohol Prediction (% ABV)", secondary_y=True)
            
            st.plotly_chart(fig, use_container_width=True)

            # --- สรุปสถานะ ---
            st.markdown("### 🏁 8.6 สรุปสถานะปัจจุบัน")
            col_a, col_b, col_c, col_d = st.columns(4)
            progress = ((og_val - current_val) / (og_val - target_val)) * 100 if (og_val - target_val) != 0 else 0
            
            suffix = "" if is_sg else (" °Bé" if is_be else "%")
            val_fmt = ".3f" if is_sg else ".2f"

            with col_a: st.metric("ค่าปัจจุบัน", f"{current_val:{val_fmt}}{suffix}")
            with col_b: st.metric("จุด 1/3 Break", f"{sugar_break:{val_fmt}}{suffix}")
            with col_c: st.metric("ความคืบหน้า", f"{min(progress, 100.0):.2f}%")
            with col_d: st.metric(f"แอลกอฮอล์ (Eff {int(yeast_eff*100)}%)", f"{current_abv:.2f}%")

    st.divider()

# ฟังก์ชันส่วนกลางสำหรับคำนวณผลกระทบของ Adjunct (ใช้ทั้งไวน์และเบียร์)
# --- [Helper Function] วางไว้ก่อนเข้า Category 10 ---
def get_adj_impact_v2(weight_g, vol_L, adj_type):
    """คำนวณผลกระทบของวัตถุดิบเสริมต่อแอลกอฮอล์และค่า Gravity Units"""
    potentials = {
        "น้ำตาลทราย/Dextrose": 380,
        "น้ำผึ้ง (Honey)": 290,
        "มอลต์สกัด (DME/LME)": 300,
        "ข้าว/ธัญพืช": 250,
        "ผลไม้ (Fruit/Puree)": 45,
        "ไม่มี": 0
    }
    p_val = potentials.get(adj_type, 0)
    # คำนวณ SG Points ที่เพิ่มขึ้น (GU เพิ่มเติม)
    added_gu = (p_val * (weight_g / 1000)) / vol_L if vol_L > 0 else 0
    added_abv = added_gu * 0.131
    return added_gu, added_abv

# ==========================================
# CATEGORY 10.1: การวางแผนไวน์ (Wine Design)
# ==========================================
if show_wine_recipe:
    st.subheader("🍷 10.1 การวางแผนและออกแบบสูตรไวน์")
    tw1, tw2, tw3 = st.tabs(["🍇 10.1.1 Brix & Juice", "🍯 10.1.2 Adjuncts", "🔮 10.1.3 Character Prediction"])

    with tw1:
        st.markdown("#### 🍇 10.1.1 การวางแผนการใช้น้ำผลไม้ และ Brix")
        with st.expander("📖 คู่มือมาตรฐาน Brix สำหรับการทำไวน์"):
            st.write("""
            | ประเภทไวน์ | Brix เป้าหมาย | คาดการณ์ ABV | ผลลัพธ์รสชาติ |
            | :--- | :--- | :--- | :--- |
            | Light White | 20 - 21 | 11.5 - 12.5% | บางเบา, ดื่มง่าย |
            | Standard Red | 22 - 24 | 13.0 - 14.2% | สมดุล, บอดี้กลาง |
            | Full-Bodied | 25+ | 15.0% + | หนักแน่น, ร้อนแรง |
            """)
        cw1, cw2 = st.columns(2)
        with cw1:
            w_vol = st.number_input("ปริมาตรน้ำผลไม้ (L):", value=10.0, key="w_v101")
            w_cur = st.number_input("ค่า Brix ปัจจุบัน:", value=12.0, key="w_c101")
            w_tgt = st.number_input("ค่า Brix เป้าหมาย:", value=22.0, key="w_t101")
        w_sugar_g = (w_tgt - w_cur) * w_vol * 10
        w_base_abv = w_tgt * 0.59
        with cw2:
            st.markdown(f"""<div class="result-container" style="border-left:8px solid #e67e22; background:#fdf2e9;">
                <p class="highlight-label">สรุปแผนการหมักไวน์</p>
                <p>น้ำตาลที่ต้องเติม: <b>{max(w_sugar_g, 0.0):,.2f} กรัม</b></p>
                <p>ABV พื้นฐานจาก Brix: <b>{w_base_abv:.2f}%</b></p>
            </div>""", unsafe_allow_html=True)

    with tw2:
        st.markdown("#### 🍯 10.1.2 วัตถุดิบเสริม (Wine Adjuncts)")
        with st.expander("📖 คู่มือผลกระทบของวัตถุดิบเสริมต่อไวน์"):
            st.write("""
            * **น้ำตาลทราย / น้ำผึ้ง:** เพิ่ม ABV สูง แต่จะทำให้บอดี้ 'Dry' (บางลง)
            * **ผลไม้สด / Puree:** เพิ่มความซับซ้อนของกลิ่น และเพิ่มเนื้อสัมผัส (Body)
            * **มอลต์สกัด:** เพิ่มความหวานคงเหลือ และบอดี้หนาขึ้น
            """)
        wa1, wa2 = st.columns(2)
        with wa1:
            w_adj_t = st.selectbox("เลือกวัตถุดิบเสริม:", ["ไม่มี", "น้ำตาลทราย/Dextrose", "น้ำผึ้ง (Honey)", "ผลไม้ (Fruit/Puree)", "มอลต์สกัด (DME/LME)"], key="w_at102")
            w_adj_w = st.number_input("น้ำหนักเสริม (กรัม):", value=0.0, step=100.0, key="w_aw102")
        _, w_add_abv = get_adj_impact_v2(w_adj_w, w_vol, w_adj_t)
        with wa2:
            st.metric("แอลกอฮอล์ที่จะเพิ่มขึ้น", f"+{w_add_abv:.2f}% ABV")

    with tw3:
        st.markdown("#### 🔮 10.1.3 การคาดการณ์ลักษณะของไวน์ (Wine Prediction)")
        w_total_abv = w_base_abv + w_add_abv
        with st.expander("📖 ตารางวิเคราะห์บอดี้และคุณภาพไวน์"):
            st.write("""
            | % ABV รวม | ความรู้สึก (Mouthfeel) | ระดับบอดี้ (Body) |
            | :--- | :--- | :--- |
            | < 11% | บางเบา (Light) | Light Body |
            | 11% - 13.5% | สมดุล/นุ่มนวล | Medium Body |
            | > 13.5% | หนักแน่น (Full) | Full Body |
            """)
        if w_total_abv > 13.5: wb_res, wb_clr = "Full Body (หนักแน่น)", "#c0392b"
        elif w_total_abv >= 11: wb_res, wb_clr = "Medium Body (สมดุล)", "#e67e22"
        else: wb_res, wb_clr = "Light Body (บางเบา)", "#3498db"
        
        st.markdown(f"**ลักษณะบอดี้รวมคาดการณ์:** <b style='color:{wb_clr}; font-size:20px;'>{wb_res}</b>", unsafe_allow_html=True)
        st.info(f"📊 **แอลกอฮอล์รวมทั้งสิ้น:** {w_total_abv:.2f}% ABV (พื้นฐาน {w_base_abv:.2f}% + เสริม {w_add_abv:.2f}%)")
        if w_adj_t in ["น้ำตาลทราย/Dextrose", "น้ำผึ้ง (Honey)"] and w_adj_w > 0:
            st.warning("⚠️ **คำแนะนำ:** การใช้น้ำตาลเสริมจะทำให้ไวน์มีเนื้อสัมผัสน้อยลง (Dry Finish)")

# ==========================================
# CATEGORY 10.2: การวางแผนเบียร์ (Beer Planning)
# ==========================================
if show_beer_recipe:
    st.subheader("🍺 10.2 การวางแผนและออกแบบสูตรเบียร์")
    
    tab21, tab22, tab23, tab24 = st.tabs([
        "🌾 10.2.1 Plato & Efficiency", 
        "🍯 10.2.2 Adjuncts", 
        "🔥 10.2.3 Strike Water", 
        "🔮 10.2.4 Character Prediction"
    ])

    # --- 10.2.1 วางแผน Plato ---
    with tab21:
        st.markdown("#### 🌾 10.2.1 การวางแผนการใช้ Plato และ Efficiency")
        with st.expander("📖 คู่มือความเข้มข้น Plato สำหรับเบียร์"):
            st.write("""
            | Plato (°P) | สไตล์เบียร์ | ABV คาดการณ์ |
            | :--- | :--- | :--- |
            | 10 - 11 | Light Lager | 4.0 - 4.5% |
            | 12 - 14 | Pale Ale / IPA | 5.0 - 6.0% |
            | 16+ | Stout / Double IPA | 7.5% + |
            """)
        cb1, cb2 = st.columns(2)
        with cb1:
            b_v = st.number_input("ปริมาตรเป้าหมาย (L):", value=20.0, key="b_v102")
            b_p_val = st.number_input("ค่า Plato ที่ต้องการ (°P):", value=12.0, key="b_p102")
            b_eff_val = st.slider("Efficiency (%):", 50, 95, 75, key="b_e102") / 100
            b_r_ratio = st.number_input("Water/Grain Ratio (L/kg):", value=3.0, key="b_r102")
        
        b_malt_needed = (b_v * b_p_val * 1.04) / (300 * b_eff_val)
        b_base_abv = b_p_val * 0.42 # ABV พื้นฐานจากมอลต์

        with cb2:
            st.markdown(f"""<div class="result-container" style="border-left:8px solid #d35400; background:#fef5e7;">
                <p class="highlight-label">สรุปแผนการใช้มอลต์</p>
                <p>มอลต์ที่ต้องใช้: <b>{b_malt_needed:.2f} kg</b></p>
                <p>ABV พื้นฐานจากมอลต์: <b>{b_base_abv:.2f}%</b></p>
            </div>""", unsafe_allow_html=True)

    # --- 10.2.2 วัตถุดิบเสริม (Adjuncts) ---
    with tab22:
        st.markdown("#### 🍯 10.2.2 วัตถุดิบเสริมเบียร์ (Beer Adjuncts)")
        ba1, ba2 = st.columns(2)
        with ba1:
            # ใช้ชื่อให้ตรงกับ potentials dictionary เพื่อป้องกัน Bug
            b_adj_select = st.selectbox("เลือกวัตถุดิบเสริม:", 
                                      ["ไม่มี", "น้ำตาลทราย/Dextrose", "น้ำผึ้ง (Honey)", "มอลต์สกัด (DME/LME)", "ข้าว/ธัญพืช"], 
                                      key="b_at102")
            b_adj_weight = st.number_input("น้ำหนักเสริม (กรัม):", value=0.0, step=100.0, key="b_aw102")
        
        # คำนวณผลกระทบจริง
        b_add_gu, b_add_abv = get_adj_impact_v2(b_adj_weight, b_v, b_adj_select)
        
        with ba2:
            st.metric("ABV ที่เพิ่มขึ้น", f"+{b_add_abv:.2f}%")
            st.metric("GU (Gravity Units) ที่เพิ่มขึ้น", f"+{b_add_gu:.2f}")

    # --- 10.2.3 Strike Water ---
    with tab23:
        st.markdown("#### 🔥 10.2.3 อุณหภูมิน้ำต้ม (Strike Water)")
        cs1, cs2 = st.columns(2)
        with cs1:
            bt_t_mash = st.number_input("อุณหภูมิ Mash เป้าหมาย (°C):", value=67.0, key="b_stt102")
            bt_g_temp = st.number_input("อุณหภูมิมอลต์ (°C):", value=25.0, key="b_stg102")
        
        b_strike_temp = (0.2 / b_r_ratio) * (bt_t_mash - bt_g_temp) + bt_t_mash
        with cs2:
            st.markdown(f'<div class="result-container" style="border-left:8px solid #2c3e50; background:#f4f6f7;">'
                        f'<p class="highlight-label">Strike Water Temp</p>'
                        f'<b style="font-size:32px;">{b_strike_temp:.2f} °C</b></div>', unsafe_allow_html=True)

    # --- 10.2.4 การคาดการณ์ลักษณะของผลิตภัณฑ์ (Revised with Units) ---
    with tab24:
        st.markdown("#### 🔮 10.2.4 การคาดการณ์ลักษณะของผลิตภัณฑ์")
        
        # คำนวณค่ารวมใหม่ (ป้องกัน Bug แอลกอฮอล์ไม่เปลี่ยน)
        total_gu_beer = (b_p_val * 4) + b_add_gu
        total_abv_beer = b_base_abv + b_add_abv
        
        cp1, cp2 = st.columns(2)
        with cp1:
            st.markdown("**1. วิเคราะห์สมดุลรสชาติ (Flavor Balance)**")
            # ดึงค่าความขม
            b_bu_val = ibu_res if 'ibu_res' in locals() else st.number_input("ระบุค่าความขม (BU/IBU): [ดูหัวข้อ 2.3 ประกอบ]", value=20.00, key="b_bu_u_predict")
            
            # คำนวณ Ratio
            b_bugu_ratio = b_bu_val / total_gu_beer if total_gu_beer > 0 else 0
            
            # --- ส่วนที่เพิ่มหน่วย (Units) ---
            st.write(f"🔹 ค่าความขม (**BU**): **{b_bu_val:.2f} IBU**")
            st.write(f"🔹 ค่าหน่วยน้ำตาลรวม (**GU**): **{total_gu_beer:.2f} Points**")
            st.markdown(f"🎯 **Flavor Balance (BU:GU): {b_bugu_ratio:.2f}**")
            
            if b_bugu_ratio > 0.8: 
                st.error("👉 รสชาติ: ขมจัดจ้าน (Hop Forward)")
            elif b_bugu_ratio >= 0.45: 
                st.success("👉 รสชาติ: สมดุลพอดี (Balanced)")
            else: 
                st.info("👉 รสชาติ: หวานนุ่มนวล (Malt Forward)")

        with cp2:
            st.markdown("**2. วิเคราะห์มิติของบอดี้ (Body Analysis)**")
            if bt_t_mash < 65.5: 
                bb_desc, bb_c = "Light & Dry (บางเบา)", "#3498db"
            elif bt_t_mash <= 67.5: 
                bb_desc, bb_c = "Medium & Balanced (สมดุล)", "#27ae60"
            else: 
                bb_desc, bb_c = "Full & Malty (หนาแน่น)", "#e67e22"
            
            st.markdown(f"ความรู้สึกในปาก: <b style='color:{bb_c}; font-size:18px;'>{bb_desc}</b>", unsafe_allow_html=True)
            st.write(f"📊 แอลกอฮอล์รวมคาดการณ์: **{total_abv_beer:.2f}% ABV**")
            
            if b_adj_select in ["น้ำตาลทราย/Dextrose", "น้ำผึ้ง (Honey)"] and b_adj_weight > 0:
                st.warning("⚠️ **Note:** การใช้ส่วนเสริมกลุ่มน้ำตาลจะทำให้บอดี้จริงบางลง")

    st.divider()

# ==========================================
# CATEGORY 11: เคมีน้ำและค่า pH (Water Chemistry & pH)
# ==========================================
if show_water_chem:
    st.subheader("🧪 11. เคมีน้ำและค่า pH (Water & pH Management)")
    
    tab_mineral, tab_ph = st.tabs(["🧂 11.1 การปรับแร่ธาตุ (Minerals) สำหรับเบียร์", "🧪 11.2 การปรับค่า pH"])

    # --- 11.1 การปรับแร่ธาตุและมิติของน้ำ ---
    with tab_mineral:
        st.markdown("<div class='info-card'><b>Water Dimension Guide:</b> ปรับสัดส่วน Sulfate/Chloride เพื่อคุม Body และความขม</div>", unsafe_allow_html=True)
        
        with st.expander("📖 ตารางคู่มือนักปรุงน้ำ (Water Dimension Reference)"):
            st.write("""
            | Ratio (SO4:Cl) | มิติรสชาติ | ความรู้สึก (Mouthfeel) |
            | :--- | :--- | :--- |
            | > 2.0 | **Very Hoppy** | ขมคมชัด, มีชีวิตชีวา, สดชื่น (Crisp/Sharp) |
            | 1.0 - 1.5 | **Balanced** | กลมกล่อม, มาตรฐาน |
            | 0.5 - 0.9 | **Malty** | นุ่มนวล, ชูรสมอลต์ (Smooth) |
            | < 0.5 | **Full Body** | หนาแน่น, อิ่มในปาก (Round) |
            """)

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            v_water = st.number_input("ปริมาณน้ำ (L):", value=20.0, key="c11_vol_m")
            gyp = st.number_input("Gypsum (CaSO4) - เพิ่มความขม:", value=0.0, step=0.1, key="c11_gyp")
            cacl = st.number_input("Calcium Chloride - เพิ่มความนุ่ม:", value=0.0, step=0.1, key="c11_cacl")
            eps = st.number_input("Epsom Salt (MgSO4):", value=0.0, step=0.1, key="c11_eps")

        # คำนวณ ppm และ Ratio
        ca = ((gyp * 232.8) + (cacl * 272.7)) / v_water if v_water > 0 else 0
        so4 = ((gyp * 557.9) + (eps * 389.7)) / v_water if v_water > 0 else 0
        cl = (cacl * 482.2) / v_water if v_water > 0 else 0
        rat = so4 / cl if cl > 0 else (5.0 if so4 > 0 else 0)

        # การประเมินมิติ
        if rat > 2.0: dim, clr = "🔥 มิติความขม: ขมคมชัด (Hoppy)", "#e67e22"
        elif 1.0 <= rat <= 2.0: dim, clr = "⚖️ มิติสมดุล: กลมกล่อม (Balanced)", "#27ae60"
        elif 0.5 <= rat < 1.0: dim, clr = "☁️ มิติความนุ่ม: ดื่มลื่น (Smooth)", "#3498db"
        else: dim, clr = "🍯 มิติ Full Body: หนาแน่น (Round)", "#8e44ad"

        with col_m2:
            st.markdown(f"""
                <div class="result-container" style="border-left: 8px solid {clr};">
                    <p class="highlight-label">📊 ผลการประเมินมิติของน้ำ</p>
                    <p style="color:{clr}; font-size:20px; font-weight:bold;">{dim}</p>
                    <hr>
                    <p>Ratio SO4:Cl = <b>{rat:.2f}</b></p>
                    <p style="font-size:14px;">Ca: {ca:.2f} | SO4: {so4:.2f} | Cl: {cl:.2f} (ppm)</p>
                </div>
            """, unsafe_allow_html=True)

    # --- 11.2 การปรับค่า pH และวิเคราะห์รสชาติ ---
    with tab_ph:
        st.markdown("<div class='info-card'><b>pH Management:</b> การคุมความเปรี้ยวและสุขภาพของยีสต์</div>", unsafe_allow_html=True)
        with st.expander("📖 รสชาติจากชนิดของกรด (Acid Flavor Analysis)"):
            st.write("""
            | กรด | มิติรสชาติ | ความรู้สึก (Mouthfeel) |
            | :--- | :--- | :--- |
            | Lactic Acid (88%) | นุ่ม (Creamy Sourness) | ถ้าใช้มากเกินไปอาจรู้สึกเหมือนผลิตภัณฑ์นม |
            | Phosphoric Acid (75%) | กลาง ๆ (Neutral)| ไม่เปลี่ยนกลิ่นรสของเครื่องดื่ม นิยมากที่สุดในระดับสากล |
            | Citric Acid | ผลไม้ (Bright/Citrus) | ช่วยชูรสชาติของไวน์ผลไม้ หรือ IPA ที่เน้น Fruity แต่ถ้าใช้ใน Stout อาจทำให้รสชาติ "ตีกัน" กับความคั่วของมอลต์|
             """)    
            st.write("""   
            |💡 ข้อควรจำสำหรับการปรับ pH|
            | :--- |
            |สำหรับเบียร์: ช่วงที่เหมาะสมในขั้นตอน Mash คือ 5.2−5.4 เพื่อการทำงานของเอนไซม์ที่ดีที่สุด|
            |สำหรับไวน์: การปรับ pH ให้ต่ำลง (ประมาณ 3.2−3.6) ด้วย Citric Acid จะช่วยให้ไวน์มีรสชาติที่ "มีชีวิตชีวา" (Vibrant) และช่วยป้องกันแบคทีเรียได้ดีกว่ากรดชนิดอื่น|
            """)

        cp1, cp2 = st.columns(2)
        with cp1:
            cur_ph = st.number_input("pH ปัจจุบัน:", value=5.8, format="%.2f", key="c11_ph_c")
            tgt_ph = st.number_input("pH เป้าหมาย:", value=5.2, format="%.2f", key="c11_ph_t")
            acid_type = st.selectbox("ชนิดของกรด:", ["Lactic Acid 88%", "Phosphoric Acid 75%", "Citric Acid"], key="c11_acid")

        diff = max(cur_ph - tgt_ph, 0)
        amt = diff * v_water * (0.05 if "Lactic" in acid_type else (0.04 if "Phos" in acid_type else 0.035))
        unit = "g/ml" if "Citric" in acid_type else "ml"

        if "Lactic" in acid_type: impact = "🥛 <b>Lactic:</b> ให้ความเปรี้ยวนุ่มนวล เหมาะกับเบียร์ Lager/Ale"
        elif "Phos" in acid_type: impact = "💎 <b>Phosphoric:</b> สะอาดและเป็นกลางที่สุด ไม่กระทบรสชาติ"
        else: impact = "🍋 <b>Citric:</b> เพิ่มความสดชื่นแบบผลไม้ เหมาะกับไวน์และ IPA"

        with cp2:
            st.markdown(f"""
                <div class="result-container" style="border-left: 8px solid #e74c3c;">
                    <p class="highlight-label">ปริมาณที่ต้องเติม</p>
                    <p class="result-value" style="color:#c0392b;">{amt:.2f} {unit}</p>
                    <hr>
                    <p style="font-size:15px;">{impact}</p>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

# ==========================================
# CATEGORY 12: การกลั่นขั้นสูง (Advanced Distillation)
# ==========================================
if show_distillation_log:
    st.subheader("🥃 12. การกลั่นและการคาดการณ์ผลลัพธ์ (Simulation & Log)")
    
    # 🚩 ส่วนกลาง: ตั้งค่า Wash Setup ก่อนเข้า Tab เพื่อป้องกัน NameError
    st.markdown("<div class='info-card'><b>Step 1: Wash Setup</b> - ระบุข้อมูลน้ำหมักก่อนเริ่มกลั่น</div>", unsafe_allow_html=True)
    c_set1, c_set2 = st.columns(2)
    with c_set1:
        d_wash_v = st.number_input("ปริมาตรน้ำหมักในหม้อ (L):", value=20.0, key="d_setup_v")
        d_wash_a = st.number_input("ดีกรีน้ำหมัก (% ABV):", value=10.0, key="d_setup_a")
    
    # คำนวณแอลกอฮอล์บริสุทธิ์ (LPA) เป็นค่ากลางที่ทุก Tab เรียกใช้ได้
    total_lpa = (d_wash_v * d_wash_a) / 100
    
    with c_set2:
        st.markdown(f"""
            <div class="result-container" style="border-left: 8px solid #722f37; background:#f4f6f7;">
                <p class="highlight-label">แอลกอฮอล์ที่มีอยู่ในระบบ</p>
                <p class="result-value" style="color:#722f37;">{total_lpa:.2f} L (Pure Alcohol)</p>
                <p style="font-size:14px; color:gray;">*นี่คือขีดจำกัดสูงสุดที่จะกลั่นได้ (100% Efficiency)</p>
            </div>
        """, unsafe_allow_html=True)

    t12_sim, t12_log, t12_guide = st.tabs(["🔮 12.1 จำลองการกลั่น", "📝 12.2 บันทึกจริง", "📖 12.3 คู่มือ"])

    # --- 12.1 Simulation (Plate Logic) ---
    with t12_sim:
        cs1, cs2 = st.columns(2)
        with cs1:
            still_type = st.radio("ประเภทเครื่องกลั่น:", ["Pot Still (หม้อต้ม)", "Column Still (หอกลั่น)"], key="c12_type")
            num_plates = 1
            if still_type == "Column Still (หอกลั่น)":
                num_plates = st.slider("จำนวนชั้น Plate (หรือความสูงเทียบเท่า):", 1, 20, 4)
        
        # คาดการณ์ประสิทธิภาพตามประเภทหม้อและจำนวนชั้น
        if still_type == "Pot Still (หม้อต้ม)":
            est_abv = 65.0
            yield_factor = 0.50 # ดึง Hearts ได้ 50% ของ LPA
            desc = "🍯 <b>Pot Still:</b> เน้นกลิ่นรสวัตถุดิบสูง แต่แยกแอลกอฮอล์ไม่คม"
        else:
            # คาดการณ์ ABV ตามจำนวน Plate (75% + 2.5% ต่อ Plate)
            est_abv = min(75 + (num_plates * 2.5), 96.0)
            # ประสิทธิภาพการดึงสุราดี (Yield) จะสูงขึ้นตามความคมของคอลัมน์
            yield_factor = min(0.60 + (num_plates * 0.02), 0.85)
            desc = f"💎 <b>Column Still ({num_plates} Plates):</b> แยกแอลกอฮอล์ได้คมชัดมาก"

        est_vol = (total_lpa * yield_factor) / (est_abv / 100)

        with cs2:
            st.markdown(f"""
                <div class="result-container" style="border-left: 8px solid #722f37;">
                    <p class="highlight-label">ผลการคาดการณ์ (Expected Output)</p>
                    <p>ดีกรีเฉลี่ยช่วงตัว (Hearts): <b>{est_abv:.1f}% ABV</b></p>
                    <p>ปริมาณสุราดีที่น่าจะได้: <b style="font-size:24px;">{est_vol:.2f} ลิตร</b></p>
                    <hr>
                    <p style="font-size:14px; color:#555;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)

    # --- 12.2 Actual Log (FIXED NameError) ---
    with t12_log:
        st.markdown("#### 📝 บันทึกปริมาณที่เก็บได้จริง")
        cl1, cl2, cl3 = st.columns(3)
        with cl1:
            act_h_v = st.number_input("Heads (L):", value=0.1, key="log_h_v")
            act_h_a = st.number_input("Heads ABV (%):", value=80.0, key="log_h_a")
        with cl2:
            act_hrt_v = st.number_input("Hearts (L):", value=1.0, key="log_hrt_v")
            act_hrt_a = st.number_input("Hearts ABV (%):", value=70.0, key="log_hrt_a")
        with cl3:
            act_t_v = st.number_input("Tails (L):", value=0.5, key="log_t_v")
            act_t_a = st.number_input("Tails ABV (%):", value=35.0, key="log_t_a")
        
        actual_pure_hearts = (act_hrt_v * act_hrt_a) / 100
        # ใช้ total_lpa จากส่วนกลาง ไม่ Error แน่นอนครับ
        actual_yield = (actual_pure_hearts / total_lpa) * 100 if total_lpa > 0 else 0
        
        st.divider()
        st.metric("ประสิทธิภาพการดึงสุราดีจริง (Heart Yield)", f"{actual_yield:.1f} %")
        st.info(f"คุณดึงแอลกอฮอล์ดีออกมาได้ {actual_pure_hearts:.2f} L จากที่มีอยู่ทั้งหมด {total_lpa:.2f} L")
    st.divider()

# --- 12.3 คู่มือนักกลั่นมือโปร ---
    with t12_guide:
        st.markdown("#### 📖 คู่มือเทคนิคการตัด (The Art of Distillation Cuts)")
        
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            with st.expander("📍 การจัดการ Heads (หัวเหล้า)", expanded=True):
                st.write("""
                - **Methanol Warning:** ส่วนแรกสุดที่ออกมาระเหยได้ที่อุณหภูมิต่ำ มีพิษร้ายแรง
                - **เทคนิค:** ให้ตัดทิ้งประมาณ 150-250 ml ต่อปริมาณน้ำหมัก 20 ลิตร (หรือ 1-3%)
                - **กลิ่น:** หากกลิ่นเหมือนน้ำยาล้างเล็บจางหายไป และเริ่มได้กลิ่นหอม 'ตัวเหล้า' จึงเริ่มเก็บ
                """)
            
            with st.expander("📍 การจัดการ Hearts (ตัวเหล้า/สุราดี)"):
                st.write("""
                - **คุณภาพ:** เป็นแอลกอฮอล์บริสุทธิ์ที่มีสารให้ความหอม (Congeners) ที่ดีที่สุด
                - **ดีกรี:** Pot Still มักเก็บในช่วง 80% - 60% / Column Still เก็บช่วง 95% - 85%
                - **สัมผัส:** ต้องมีความนุ่มนวล ไม่บาดคอ และไม่มีกลิ่นแปลกปลอม
                """)

        with col_g2:
            with st.expander("📍 การจัดการ Tails (หางเหล้า)"):
                st.write("""
                - **Fusel Oils:** สารประกอบหนักที่ทำให้สุราขุ่นและมีรสขม
                - **จุดตัด:** เมื่อ ABV ลดลงต่ำกว่า 55-50% หรือเริ่มมีกลิ่นเหมือนกระดาษเปียก
                - **ประโยชน์:** หางเหล้ายังมีแอลกอฮอล์เหลืออยู่ ให้นำไปผสมน้ำหมักรอบถัดไป (Feints Run)
                """)

            st.info("💡 **Pro Tip:** อุปกรณ์การกลั่นเหล้าที่ดีที่สุดคือการใช้ 'จมูกและลิ้น' ร่วมกับ 'เทอร์โมมิเตอร์วัดอุณหภูมิ' ห้ามเชื่อตัวเลขเพียงจากอุณหภูมิเพียงอย่างเดียว")

    st.divider()

# ==========================================
# CATEGORY 13: การควบคุมคุณภาพและรายงาน (QC/QA & Report) - v4.9
# ==========================================
if show_qc_qa:
    st.subheader("🛡️ 13. การควบคุมคุณภาพและการจัดทำรายงาน (QC/QA)")
    
    tab13_sensory, tab13_check, tab13_report = st.tabs([
        "👅 13.1 การประเมินรสชาติ (Sensory)", 
        "📋 13.2 รายการตรวจสอบ (QA Checklist)", 
        "📑 13.3 พิมพ์รายงาน (Report)"
    ])

    # --- 13.1 การประเมินรสชาติ (Sensory) ---
    with tab13_sensory:
        st.markdown("<div class='info-card'><b>Sensory Evaluation:</b> บันทึกผลการทดสอบเชิงลึก</div>", unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            q_prod_name = st.text_input("ชื่อผลิตภัณฑ์:", value="Spirit Batch A", key="qc_prod_name")
            q_lot = st.text_input("Lot / Batch No.:", value=datetime.now().strftime("%Y%m%d-01"), key="qc_lot")
            q_abv = st.number_input("ดีกรีที่วัดได้จริง (% ABV):", value=40.0, step=0.1, key="qc_abv")
        with col_s2:
            q_color = st.text_input("ลักษณะสี (Color/Clarity):", value="ใสประกาย ไม่มีตะกอน", key="qc_color")
            q_aroma = st.text_area("ลักษณะกลิ่น (Aroma Profile):", value="หอมกลิ่นผลไม้สุก ไม่มีกลิ่นฉุน", key="qc_aroma")

        st.markdown("##### 👅 รายละเอียดรสชาติ")
        ts1, ts2 = st.columns(2)
        with ts1:
            s_sweet = st.select_slider("ความหวาน:", ["Very Dry", "Dry", "Balanced", "Sweet"], value="Balanced", key="s_sweet")
            s_sweet_note = st.text_input("โน้ตรสหวาน:", placeholder="เช่น หวานนวล...", key="s_sweet_note")
            s_acid = st.select_slider("ความเปรี้ยว:", ["Low", "Balanced", "Bright", "Tart"], value="Balanced", key="s_acid")
            s_acid_note = st.text_input("โน้ตรสเปรี้ยว:", placeholder="เช่น เปรี้ยวสดชื่น...", key="s_acid_note")
        with ts2:
            s_body = st.select_slider("บอดี้:", ["Light", "Medium", "Full", "Heavy"], value="Medium", key="s_body")
            s_body_note = st.text_input("โน้ตบอดี้:", placeholder="เช่น นุ่มเคลือบปาก...", key="s_body_note")
            s_finish = st.select_slider("รสสัมผัสหลังดื่ม:", ["Short", "Clean", "Medium", "Long"], value="Medium", key="s_finish")
            s_finish_note = st.text_input("โน้ต Finish:", placeholder="เช่น หอมยาวนาน...", key="s_finish_note")

    # --- 13.2 QA Checklist ---
    with tab13_check:
        st.markdown("#### 📋 รายการตรวจสอบคุณภาพขั้นสุดท้าย")
        cq1, cq2 = st.columns(2)
        with cq1:
            q_ph = st.checkbox("ค่า pH อยู่ในช่วงมาตรฐาน", key="q_ph")
            q_cuts = st.checkbox("ไม่มีกลิ่น Heads/Tails ปนเปื้อน", key="q_cuts")
            q_clean = st.checkbox("ภาชนะฆ่าเชื้อแล้ว", key="q_clean")
        with cq2:
            q_label = st.checkbox("ความเรียบร้อยของฉลาก", key="q_label")
            q_stamp = st.checkbox("การติดแสตมป์สรรพสามิต", key="q_stamp")
            q_box = st.checkbox("กล่องบรรจุภัณฑ์สมบูรณ์", key="q_box")

    # --- 13.3 พิมพ์รายงาน (REPORT SYSTEM) ---
    with tab13_report:
        st.markdown("#### 📑 ระบบจัดทำรายงานคุณภาพ")
        
        # ส่วนเตรียมข้อมูลรายงาน
        rep_name = st.text_input("💾 ตั้งชื่อไฟล์รายงาน (เช่น QC_Batch01):", value=f"QC_Report_{q_lot}", key="rep_file_name")
        
        # ฟังก์ชันสร้างเนื้อหา Text
        report_txt = f"""--------------------------------------------------
รายงานผลการตรวจสอบคุณภาพ (Quality Report)
--------------------------------------------------
ชื่อผลิตภัณฑ์: {q_prod_name}
Lot Number: {q_lot}
วันที่ผลิต: {datetime.now().strftime("%d/%m/%Y %H:%M")}
ดีกรีที่วัดได้: {q_abv}% ABV
ลักษณะสี: {q_color}
ลักษณะกลิ่น: {q_aroma}

การประเมินรสชาติ (Sensory):
- ความหวาน: {s_sweet} ({s_sweet_note})
- ความเปรี้ยว: {s_acid} ({s_acid_note})
- บอดี้: {s_body} ({s_body_note})
- รสสัมผัสหลังดื่ม: {s_finish} ({s_finish_note})

สถานะ QA:
- ค่า pH: {"ผ่าน" if q_ph else "ไม่ผ่าน"}
- การตัดหัว/หาง: {"ผ่าน" if q_cuts else "ไม่ผ่าน"}
- ความสะอาด: {"ผ่าน" if q_clean else "ไม่ผ่าน"}
- ฉลาก: {"ผ่าน" if q_label else "ไม่ผ่าน"}
- แสตมป์: {"ผ่าน" if q_stamp else "ไม่ผ่าน"}
- กล่องบรรจุ: {"ผ่าน" if q_box else "ไม่ผ่าน"}
--------------------------------------------------"""

        st.text_area("Preview รายงาน:", value=report_txt, height=350)

        # ปุ่มควบคุม (Export & Print)
        pcol1, pcol2, pcol3, pcol4, pcol5 = st.columns(5)
        
        with pcol1:
            # 📊 Save as Excel (CSV Format)
            excel_rows = [{"รายงานผลการตรวจสอบคุณภาพ": line} for line in report_txt.split('\n')]
            df_excel = pd.DataFrame(excel_rows)
            csv_data = df_excel.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📊 Save Excel", data=csv_data, file_name=f"{rep_name}.csv")

        with pcol2:
            # 📕 Save as PDF (Safe Import)
            try:
                from fpdf import FPDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=11)
                for line in report_txt.split('\n'):
                    # กรองตัวอักษรไทยออกชั่วคราว (เนื่องจาก PDF มาตรฐานไม่รองรับไทย)
                    safe_line = line.encode('latin-1', 'ignore').decode('latin-1')
                    pdf.cell(200, 8, txt=safe_line, ln=True)
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
                st.download_button("📕 Save PDF", data=pdf_bytes, file_name=f"{rep_name}.pdf")
            except ImportError:
                st.info("💡 ติดตั้ง PDF: 'pip install fpdf'")

        with pcol3:
            # 🖨️ Native Print (เรียกหน้าต่างพิมพ์ของเบราว์เซอร์)
            if st.button("🖨️ Print Report"):
                # จัดรูปแบบ JavaScript ให้ปลอดภัยจาก Backslash Error
                js_content = report_txt.replace('\n', '<br>').replace("'", "\\'")
                components.html(f"""
                    <script>
                    var win = window.open('', '', 'height=700,width=850');
                    win.document.write('<html><head><title>Print Report</title>');
                    win.document.write('<style>body {{ font-family: monospace; padding: 30px; line-height: 1.4; }}</style>');
                    win.document.write('</head><body>');
                    win.document.write('<h3>Quality Control Report</h3>');
                    win.document.write('<p>{js_content}</p>');
                    win.document.write('</body></html>');
                    win.document.close();
                    setTimeout(function(){{ win.print(); win.close(); }}, 500);
                    </script>
                """, height=0)

        with pcol4:
            if st.button("📝 Edit"):
                st.info("แก้ไขข้อมูลใน Tab 13.1 และ 13.2")

        with pcol5:
            if st.button("🧹 Clear"):
                keys = [k for k in st.session_state.keys() if k.startswith(('qc_', 's_', 'q_'))]
                for k in keys: del st.session_state[k]
                st.rerun()

    st.divider()

# ==========================================
# CATEGORY 14: ข้อมูลช่วยเหลือและการติดต่อ (Help & Contact)
# ==========================================
if show_help_contact:
    st.subheader("📖 14. ข้อมูลช่วยเหลือและการติดต่อ")
    
    t14_1, t14_2, t14_3 = st.tabs([
        "📚 14.1 คู่มือการใช้งาน (Help)", 
        "📞 14.2 ติดต่อผู้พัฒนา (Contact)", 
        "💬 14.3 เสนอแนะ (Feedback)"
    ])

    # --- 14.1 คู่มือการใช้งาน (Help) ---
    with t14_1:
        st.markdown("### 📚 สารบัญและคำอธิบายการใช้งาน (Contents)")
        
        # ฟังก์ชันสร้างรูปแบบการอธิบายที่เหมือนกัน
        def help_item_layout(title, origin, objective, usage):
            with st.expander(title):
                st.markdown(f"""
                <div style="background-color: #fcfcfc; padding: 15px; border-radius: 5px;">
                    <p><b>📍 ที่มา:</b> {origin}</p>
                    <p><b>🎯 วัตถุประสงค์:</b> {objective}</p>
                    <p><b>🛠️ วิธีการใช้งาน:</b> {usage}</p>
                </div>
                """, unsafe_allow_html=True)
                st.divider()
        def help_layout(title, origin, objective, usage):
            help_item_layout(title, origin, objective, usage)   

# --- หมวด 1-3: พื้นฐานและการวิเคราะห์ ---
        help_layout("1. การแปลงหน่วย (Unit Conversion)", 
                    "มาตรฐานมาตรวิทยาสากล (SI Units)", 
                    "แปลงค่าอุณหภูมิ ปริมาตร และความเข้มข้นให้เป็นหน่วยมาตรฐานเดียวกัน", 
                    "เลือก Tab หน่วยที่ต้องการแปลง กรอกตัวเลขในช่อง Input ระบบจะคำนวณผลลัพธ์ทุกหน่วยที่เกี่ยวข้องทันที")

        help_layout("2. การคำนวณแอลกอฮอล์ (Alcohol Analysis)", 
                    "กฎของสมดุลมวล (Mass Balance) และตารางความหนาแน่น", 
                    "คำนวณการเจือจาง การเสริมแอลกอฮอล์ และหาค่า ABV จากอุปกรณ์วัด", 
                    "ระบุค่าปริมาตรหรือดีกรีตั้งต้น และกรอกค่าเป้าหมายที่ต้องการ ระบบจะแจ้งปริมาณน้ำหรือแอลกอฮอล์ที่ต้องเติม")

        help_layout("3. การวิเคราะห์ทางเคมี (Chemical Analysis)", 
                    "วิธีการไทเทรตมาตรฐาน (Titration Methods)", 
                    "หาค่า Titratable Acidity (TA) และ Free/Total SO2", 
                    "เตรียมตัวอย่างตามปริมาณที่กำหนด ไทเทรตด้วยสารละลายมาตรฐาน แล้วกรอกปริมาตรที่ใช้ลงในโปรแกรม")

        # --- หมวด 4-6: กระบวนการหมักและการปรับปรุง ---
        help_layout("4. น้ำตาลและการหมัก (Sugar & Fermentation)", 
                    "ทฤษฎี Chaptalization และการสกัดน้ำตาล", 
                    "ปรับปรุงค่าความหวาน (Brix/Plato) ให้เหมาะสมกับเป้าหมายแอลกอฮอล์", 
                    "ระบุค่า Brix ปัจจุบันและเป้าหมาย ระบบจะคำนวณปริมาณน้ำตาลหรือน้ำที่ต้องเติมเพื่อปรับค่า")

        help_layout("5. ยีสต์และสารอาหาร (Yeast & Nutrients)", 
                    "มาตรฐาน Pitching Rate และความต้องการไนโตรเจน (YAN)", 
                    "คำนวณปริมาณยีสต์ที่ต้องใช้และการเติมสารอาหารให้การหมักสมบูรณ์", 
                    "กรอกปริมาณน้ำหมักและดีกรีเป้าหมาย ระบบจะแนะนำปริมาณยีสต์และโดสของสารอาหาร (DAP/Nutrient)")

        help_layout("6. การทำให้ใสและเสถียร (Fining & Stabilization)", 
                    "หลักการดูดซับทางประจุ (Adsorption) และความร้อน (Thermodynamics)", 
                    "คำนวณการใช้สารช่วยใส (Bentonite/Gelatin) และการป้องกันไวน์คืนตัว", 
                    "เลือกชนิดสารช่วยใสและระบุปริมาณน้ำหมัก ระบบจะคำนวณน้ำหนักสารที่ต้องเตรียมตามความเข้มข้นที่แนะนำ")

        # --- หมวด 7-9: การตรวจสอบและบริหารจัดการ ---
        help_layout("7. การประเมินเบื้องต้น (Basic Sensory)", 
                    "มาตรฐานการชิมแบบ Hedonic Scale", 
                    "บันทึกความพึงพอใจเบื้องต้นในระหว่างการทดลอง", 
                    "ลากสไลเดอร์เพื่อประเมินคะแนนในด้านต่างๆ และบันทึกข้อสังเกตสั้นๆ")

        help_layout("8. การติดตามการหมัก (Fermentation Monitoring)", 
                    "ทฤษฎี Gravity Decay Monitoring", 
                    "สร้างกราฟติดตามการลดลงของน้ำตาลเพื่อดูสุขภาพของยีสต์", 
                    "บันทึกค่า Brix/SG ตามวันเวลาที่วัดจริง ระบบจะพล็อตแนวโน้มความเร็วการหมักให้โดยอัตโนมัติ")

        help_layout("9. การคิดต้นทุน (Costing & Inventory)", 
                    "หลักการบัญชีต้นทุนการผลิต (Production Costing)", 
                    "คำนวณต้นทุนวัตถุดิบ บรรจุภัณฑ์ และต้นทุนต่อขวด", 
                    "กรอกราคาสื้อวัตถุดิบและปริมาณที่ใช้จริง ระบบจะสรุปต้นทุนรวมและจุดคุ้มทุนเบื้องต้น")

        # --- หมวด 10-13: การผลิตขั้นสูงและ QC ---
        help_layout("10. การออกแบบสูตร (Recipe Design)", 
                    "Flavor Balancing (BU:GU) และ Character Prediction", 
                    "วางแผนการผลิตไวน์และเบียร์แบบแยกส่วน พร้อมวิเคราะห์บอดี้", 
                    "เลือกประเภทเครื่องดื่ม ใส่ค่า Brix/Plato และ IBU ระบบจะวิเคราะห์สมดุลรสชาติและบอดี้คาดการณ์")

        help_layout("11. การปรับปรุงน้ำ (Water & pH)", 
                    "เคมีของน้ำและการควบคุมเอนไซม์ (Water Chemistry)", 
                    "ปรับค่า pH ของน้ำ Mash หรือน้ำหมักให้เหมาะสมกับเอนไซม์และยีสต์", 
                    "ระบุ pH ปัจจุบันและเป้าหมาย พร้อมเลือกชนิดของกรด ระบบจะคำนวณปริมาณกรดที่ต้องเติม")

        help_layout("12. บันทึกการกลั่น (Distillation Log)", 
                    "ทฤษฎีสมดุลไอ (VLE) และ Plate Efficiency", 
                    "คาดการณ์ปริมาณสุราดี (Hearts) และบันทึกจุดตัดการกลั่น (Cuts)", 
                    "ระบุคุณสมบัติน้ำหมักและประเภทหม้อกลั่น บันทึกปริมาณที่เก็บได้จริงเพื่อประเมินประสิทธิภาพ (Yield)")

        help_layout("13. การคุมคุณภาพและรายงาน (QC/QA)", 
                    "มาตรฐาน ISO/GMP และหลักการ Sensory Analysis มืออาชีพ", 
                    "บันทึกการตรวจสอบคุณภาพเชิงลึก ตรวจสอบความเรียบร้อย และออกรายงาน", 
                    "บันทึกผลการชิมละเอียด ตรวจ Checklist กฎหมาย และกดปุ่มพิมพ์รายงานในรูปแบบที่ต้องการ")
      

    # --- 14.2 ข้อมูลการติดต่อ (Contact) ---
    with t14_2:
        st.markdown("### 📞 ติดต่อสอบถาม / สนับสนุน (Contact Information)")
              
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #722f37;">
                <p><b>👤 ผู้พัฒนา:</b> รศ.ดร.โชคชัย วนภู</p>
                <p><b>📧 Email:</b> <a href="mailto:chokie.w@gmail.com">chokie.w@gmail.com</a></p>
                <p><b>💬 Line ID:</b> chokiew</p>
                <p><b>📞 โทร:</b> 081-593-9309</p>
            </div>
            """, unsafe_allow_html=True)
        with cc2:
            st.info("🕒 **เวลาทำการ:** จันทร์ - ศุกร์ (09:00 - 17:00 น.)")
            st.write("โปรแกรม Wine, Beer, & Spirit Master นี้ จัดสร้างขึ้นเพื่อส่งเสริม สนับสนุน ผู้ประกอบการและผู้ผลิตไวน์ เบียร์ และสุรา โดยไม่คิดมูลค่าใดๆ เป็น Freeware ที่ยินดีให้ทุกท่านได้ใช้ฟรี และยินดีที่จะให้คำปรึกษาด้านเทคนิคการใช้งานโปรแกรม การคำนวณทางแล็บ และการผลิตสุราอย่างมืออาชีพ")


    # --- 14.3 ข้อเสนอแนะและ Admin Only ---
    with t14_3:
        st.markdown("### 💬 ข้อเสนอแนะ (Feedback)")
        
        fb_name = st.text_input("ชื่อของคุณ:", key="fb_user")
        fb_msg = st.text_area("เขียนบันทึกหรือข้อเสนอแนะ:", height=150, key="fb_text")
        
        if st.button("🚀 ส่งข้อความผ่าน Email"):
            if fb_msg:
                target_mail = "chokie.w@gmail.com"
                subject = f"Feedback from {fb_name}"
                body = fb_msg.replace('\n', '%0D%0A')
                mailto_link = f"mailto:{target_mail}?subject={subject}&body={body}"
                st.markdown(f'<a href="{mailto_link}" target="_blank" style="text-decoration:none;"><div style="background-color:#28a745; color:white; padding:10px; text-align:center; border-radius:5px;">เปิดโปรแกรมส่ง Email</div></a>', unsafe_allow_html=True)
            else:
                st.error("กรุณากรอกข้อความก่อนส่ง")

        st.divider()

        # --- ปุ่ม Admin Only (ซ่อนไว้ที่มุมขวาล่างของส่วนเนื้อหา) ---
        # ใช้ CSS เพื่อจัดตำแหน่งปุ่มและใส่ฟังก์ชันความลับ
        st.markdown("<br><br>", unsafe_allow_html=True)
        col_empty, col_admin = st.columns([6, 1])
        
        with col_admin:
            # ใช้ปุ่มที่ดูไม่เด่นมากเพื่อความเป็นส่วนตัว
            if st.button("🔑 Admin Only"):
                st.session_state.show_admin_panel = not st.session_state.get('show_admin_panel', False)

        # ส่วนแสดงสถิติ (จะปรากฏเมื่อกดปุ่ม Admin Only และผ่านรหัสผ่าน)
        if st.session_state.get('show_admin_panel'):
            st.markdown("---")
            st.markdown("#### 🔒 ส่วนของผู้ดูแลระบบ (Admin Only)")
            admin_pass = st.text_input("ระบุรหัสผ่านเข้าใช้งาน:", type="password")
            
            if admin_pass == "Honey3705": # <--- เปลี่ยนรหัสผ่านตรงนี้
                if os.path.exists("usage_log.csv"):
                    df_usage = pd.read_csv("usage_log.csv")
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("จำนวนครั้งที่เปิดใช้", f"{len(df_usage)} ครั้ง")
                    with c2:
                        st.metric("จำนวนผู้ใช้ที่ไม่ซ้ำ", f"{df_usage['User'].nunique()} คน")
                    with c3:
                        if not df_usage.empty:
                            st.write(f"ใช้งานล่าสุด: \n{df_usage['Timestamp'].iloc[-1]}")
                    
                    st.markdown("**ประวัติการเข้าใช้งาน:**")
                    st.dataframe(df_usage.tail(15), use_container_width=True)
                    
                    if st.button("🧹 ล้างประวัติทั้งหมด"):
                        os.remove("usage_log.csv")
                        st.success("ล้างข้อมูลเรียบร้อยแล้ว")
                        st.rerun()
                else:
                    st.info("ยังไม่มีข้อมูลสถิติบันทึกไว้")
            elif admin_pass != "":
                st.error("❌ รหัสผ่านไม่ถูกต้อง")

    st.divider()

# --- Footer ---
if not any([show_temp, show_vol, show_conc, show_alc, show_reading, show_abv_est, show_acid, show_ta, show_so2, show_nutrients, show_fining, show_stabilize, show_pearson, show_dilution, show_sensory]):
    st.warning("⚠️ โปรดเลือกหมวดหมู่ที่ต้องการจาก Sidebar")

# --- Footer ---
st.sidebar.caption("v4.3 | Wine, Beer, & Spirit Master®️ | Pro Monitoring Edition | By Chokchai Wanapu ©2026")