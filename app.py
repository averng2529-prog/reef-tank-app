import streamlit as st
import json
import os
from datetime import datetime

# ตั้งค่าหน้าตาของแอป
st.set_page_config(
    page_title="Reef Tank Manager",
    page_icon="🪸",
    layout="wide",
    initial_sidebar_state="expanded"
)

FILENAME = "reef_tank_data.json"

def load_data():
    if not os.path.exists(FILENAME):
        default_data = {
            "parameters_log": [],
            "livestock": [],
            "maintenance_schedule": [
                {"task": "เปลี่ยนน้ำ 10%", "frequency_days": 7, "last_done": ""},
                {"task": "วัดค่าน้ำประจำสัปดาห์", "frequency_days": 7, "last_done": ""},
                {"task": "ทำความสะอาดถ้วย Skimmer", "frequency_days": 3, "last_done": ""},
                {"task": "เปลี่ยนคาร์บอน / ตัวกรอง", "frequency_days": 30, "last_done": ""}
            ]
        }
        with open(FILENAME, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data
    
    try:
        with open(FILENAME, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        st.error("เกิดข้อผิดพลาดในการโหลดไฟล์ข้อมูล")
        return {"parameters_log": [], "livestock": [], "maintenance_schedule": []}

def save_data(data):
    with open(FILENAME, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

st.title("🪸 Reef Tank Manager")
st.caption("ระบบบันทึกและจัดการตู้ปลาทะเลส่วนตัว")

# เมนูหลักด้านข้าง
menu = st.sidebar.radio("เมนูใช้งาน", ["📊 สรุปภาพรวม", "💧 บันทึกค่าน้ำ", "🐠 จัดการสิ่งมีชีวิต", "📅 ตารางการดูแล"])

# --- PAGE 1: สรุปภาพรวม ---
if menu == "📊 สรุปภาพรวม":
    st.subheader("📌 ค่าน้ำล่าสุด")
    if data["parameters_log"]:
        latest = data["parameters_log"][-1]
        st.info(f"🗓️ บันทึกล่าสุดเมื่อ: {latest['date']}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ความเค็ม (Salinity)", f"{latest['salinity_ppt']} ppt")
        c2.metric("อุณหภูมิ (Temp)", f"{latest['temp_c']} °C")
        c3.metric("ค่า KH", f"{latest['kh_dkh']} dKH")
        c4.metric("แคลเซียม (Ca)", f"{latest['calcium_ppm']} ppm")
        
        c5, c6, c7, _ = st.columns(4)
        c5.metric("แมกนีเซียม (Mg)", f"{latest['magnesium_ppm']} ppm")
        c6.metric("ไนเตรท (NO3)", f"{latest['nitrate_ppm']} ppm")
        c7.metric("ฟอสเฟต (PO4)", f"{latest['phosphate_ppm']} ppm")
    else:
        st.warning("ยังไม่มีข้อมูลบันทึกค่าน้ำ")

    st.divider()
    st.subheader("🐟 สิ่งมีชีวิตในตู้")
    st.write(f"จำนวนทั้งหมด: **{len(data['livestock'])}** รายการ")
    if data["livestock"]:
        st.dataframe(data["livestock"], use_container_width=True)

# --- PAGE 2: บันทึกค่าน้ำ ---
elif menu == "💧 บันทึกค่าน้ำ":
    st.subheader("📝 บันทึกค่าน้ำใหม่")
    with st.form("param_form"):
        col1, col2 = st.columns(2)
        with col1:
            sal = st.number_input("ความเค็ม (ppt)", value=35.0, step=0.5)
            temp = st.number_input("อุณหภูมิ (°C)", value=25.5, step=0.1)
            kh = st.number_input("ค่า KH (dKH)", value=8.3, step=0.1)
            ca = st.number_input("Calcium (ppm)", value=420, step=5)
        with col2:
            mg = st.number_input("Magnesium (ppm)", value=1350, step=10)
            no3 = st.number_input("Nitrate NO3 (ppm)", value=5.0, step=0.5)
            po4 = st.number_input("Phosphate PO4 (ppm)", value=0.03, step=0.01)
            
        submitted = st.form_submit_button("💾 บันทึกข้อมูลค่าน้ำ")
        if submitted:
            new_entry = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "salinity_ppt": sal, "temp_c": temp, "kh_dkh": kh,
                "calcium_ppm": ca, "magnesium_ppm": mg,
                "nitrate_ppm": no3, "phosphate_ppm": po4
            }
            data["parameters_log"].append(new_entry)
            save_data(data)
            st.success("บันทึกค่าน้ำสำเร็จ!")
            st.rerun()

# --- PAGE 3: จัดการสิ่งมีชีวิต ---
elif menu == "🐠 จัดการสิ่งมีชีวิต":
    st.subheader("➕ เพิ่มสิ่งมีชีวิตใหม่")
    with st.form("livestock_form"):
        name = st.text_input("ชื่อสิ่งมีชีวิต / ปะการัง")
        cat = st.selectbox("ประเภท", ["ปลา", "ปะการังแข็ง (SPS)", "ปะการังแข็ง (LPS)", "ปะการังอ่อน (Softie)", "กุ้ง/หอย/ทำความสะอาด", "อื่นๆ"])
        date_added = st.date_input("วันที่นำลงตู้")
        
        sub = st.form_submit_button("➕ เพิ่มเข้าตู้")
        if sub and name:
            data["livestock"].append({
                "name": name, "category": cat, "date_added": str(date_added)
            })
            save_data(data)
            st.success(f"เพิ่ม {name} เรียบร้อยแล้ว!")
            st.rerun()

# --- PAGE 4: ตารางการดูแล ---
elif menu == "📅 ตารางการดูแล":
    st.subheader("📋 รายการที่ต้องดูแลและบำรุงรักษา")
    today = datetime.now()
    
    for idx, item in enumerate(data["maintenance_schedule"]):
        cols = st.columns([3, 2, 2])
        cols[0].write(f"**{item['task']}** (ทุกๆ {item['frequency_days']} วัน)")
        
        last = item["last_done"]
        if not last:
            cols[1].warning("ยังไม่ได้บันทึก")
        else:
            last_dt = datetime.strptime(last, "%Y-%m-%d")
            passed = (today - last_dt).days
            if passed >= item["frequency_days"]:
                cols[1].error(f"⚠️ เกินกำหนด ({passed} วันที่แล้ว)")
            else:
                cols[1].success(f"✅ ทำแล้ว ({passed} วันที่แล้ว)")
                
        if cols[2].button("บันทึกว่าทำแล้ว", key=f"done_{idx}"):
            data["maintenance_schedule"][idx]["last_done"] = today.strftime("%Y-%m-%d")
            save_data(data)
            st.rerun()