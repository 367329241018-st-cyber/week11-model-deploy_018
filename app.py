"""
app.py
------
เว็บแอป Streamlit สำหรับโหลดโมเดล Machine Learning ที่ฝึกไว้แล้ว (ไฟล์ .pkcls)
และใช้ทำนายผลการจำแนกโรค Covid จากข้อมูล/ฟีเจอร์ที่เกี่ยวข้องกับภาพ X-ray

หมายเหตุสำคัญ:
- ผมไม่สามารถเข้าถึงไฟล์ .pkcls จริงในโฟลเดอร์ Google Drive ของคุณได้
  (Google Drive โหลดรายชื่อไฟล์ด้วย JavaScript และเป็นไฟล์ส่วนตัวของคุณ)
- ดังนั้นชื่อคอลัมน์ (features) ในโค้ดนี้เป็น "ตัวอย่างสมมติ" เท่านั้น
  คุณต้องแก้ไขให้ตรงกับคอลัมน์จริงที่ใช้ตอนฝึกโมเดล (ดูคำอธิบายท้ายไฟล์)
- Streamlit อ่านไฟล์จาก Google Drive โดยตรงไม่ได้ ต้องดาวน์โหลดไฟล์ .pkcls
  มาไว้ในเครื่อง/เซิร์ฟเวอร์ก่อน แล้วให้ผู้ใช้เลือกไฟล์ผ่านหน้าเว็บ (st.file_uploader)
  หรือระบุพาธไฟล์ในเครื่องก็ได้ (ดูตัวเลือกในแอป)
"""

import streamlit as st
import pandas as pd
import joblib
import io
import os

# ============================================================
# 2. ตั้งค่าหน้าเว็บและหัวข้อแอป
# ============================================================
st.set_page_config(page_title="จำแนกโรค Covid จากภาพ X-ray", layout="centered")
st.title("โปรแกรมจำแนกโรค Covid จากภาพ X-ray")
st.write("กรอกข้อมูล/ค่าฟีเจอร์ที่เกี่ยวข้อง แล้วกดปุ่ม 'ทำนายผล' เพื่อดูผลการจำแนก")

# ============================================================
# 1. ส่วนเลือก/โหลดโมเดล (*.pkcls) ด้วย joblib
# ============================================================
st.header("1) เลือกโมเดลที่จะใช้")

# ให้ผู้ใช้เลือกวิธีโหลดโมเดลได้ 2 แบบ: อัปโหลดไฟล์ หรือ ระบุพาธไฟล์ในเครื่อง
model_source = st.radio(
    "เลือกวิธีโหลดโมเดล",
    ("อัปโหลดไฟล์โมเดล (.pkcls)", "ระบุพาธไฟล์ในเครื่อง/เซิร์ฟเวอร์"),
)

model = None  # ตัวแปรเก็บโมเดลที่โหลดสำเร็จ

if model_source == "อัปโหลดไฟล์โมเดล (.pkcls)":
    # ผู้ใช้อัปโหลดไฟล์โมเดลผ่านหน้าเว็บโดยตรง
    uploaded_model_file = st.file_uploader(
        "อัปโหลดไฟล์โมเดล (.pkcls)", type=["pkcls"]
    )
    if uploaded_model_file is not None:
        try:
            # โหลดโมเดลด้วย joblib จาก bytes ที่อัปโหลดมา
            model = joblib.load(io.BytesIO(uploaded_model_file.getvalue()))
            st.success(f"โหลดโมเดล '{uploaded_model_file.name}' สำเร็จ")
        except Exception as e:
            st.error(f"โหลดโมเดลไม่สำเร็จ: {e}")

else:
    # กรณีดาวน์โหลดไฟล์จาก Google Drive มาไว้ในเครื่อง/เซิร์ฟเวอร์แล้ว
    # เช่น อยู่ในโฟลเดอร์ ./models/ ให้ระบุพาธแล้วกดโหลด
    default_dir = "./models"
    if os.path.isdir(default_dir):
        # แสดงรายชื่อไฟล์ .pkcls ที่พบในโฟลเดอร์ ./models ให้เลือกจาก dropdown
        pkcls_files = [f for f in os.listdir(default_dir) if f.endswith(".pkcls")]
        if pkcls_files:
            selected_file = st.selectbox("เลือกไฟล์โมเดลจากโฟลเดอร์ models", pkcls_files)
            model_path = os.path.join(default_dir, selected_file)
        else:
            st.warning("ไม่พบไฟล์ .pkcls ในโฟลเดอร์ ./models")
            model_path = st.text_input("หรือระบุพาธไฟล์โมเดลเต็ม (.pkcls)")
    else:
        model_path = st.text_input("ระบุพาธไฟล์โมเดลเต็ม (.pkcls)")

    if model_path and os.path.isfile(model_path):
        try:
            model = joblib.load(model_path)
            st.success(f"โหลดโมเดลจาก '{model_path}' สำเร็จ")
        except Exception as e:
            st.error(f"โหลดโมเดลไม่สำเร็จ: {e}")
    elif model_path:
        st.error("ไม่พบไฟล์ตามพาธที่ระบุ กรุณาตรวจสอบอีกครั้ง")

st.divider()

# ============================================================
# 3. ส่วนกรอกค่าตัวแปรต้น (features)
# ============================================================
# *** สำคัญ: คอลัมน์ด้านล่างนี้เป็น "ตัวอย่างสมมติ" เท่านั้น ***
# กรุณาแก้ไข ชื่อคอลัมน์ / ชนิดข้อมูล / ตัวเลือก ให้ตรงกับ
# features จริงที่ใช้ตอนฝึกโมเดลของคุณ (ดูคำอธิบายท้ายไฟล์)

st.header("2) กรอกข้อมูลผู้ป่วย (Features)")

with st.form("prediction_form"):
    # --- ตัวแปรตัวเลข (ใช้ st.number_input) ---
    age = st.number_input("อายุ (ปี)", min_value=0, max_value=120, value=30, step=1)
    temperature = st.number_input(
        "อุณหภูมิร่างกาย (°C)", min_value=30.0, max_value=45.0, value=37.0, step=0.1
    )

    # --- ตัวแปรหมวดหมู่ (ใช้ st.selectbox) ---
    gender = st.selectbox("เพศ", ["ชาย", "หญิง"])
    cough = st.selectbox("อาการไอ", ["มี", "ไม่มี"])
    fever = st.selectbox("อาการไข้", ["มี", "ไม่มี"])
    shortness_of_breath = st.selectbox("อาการเหนื่อยหอบ", ["มี", "ไม่มี"])
    xray_result = st.selectbox(
        "ผลอ่านภาพ X-ray เบื้องต้น (จากรังสีแพทย์)",
        ["ปกติ", "พบฝ้าขาว (Opacity)", "สงสัย Pneumonia"],
    )

    # ปุ่มกดส่งฟอร์มเพื่อทำนายผล (ข้อ 4)
    submitted = st.form_submit_button("ทำนายผล")

# ============================================================
# 4. เมื่อกดปุ่ม 'ทำนายผล' -> จัดรูปแบบข้อมูลให้ตรงกับตอนฝึกโมเดล
# ============================================================
if submitted:
    if model is None:
        st.error("กรุณาเลือก/โหลดโมเดลก่อนทำการทำนายผล")
    else:
        # ---------------------------------------------------
        # 4.1 สร้าง DataFrame จากค่าที่ผู้ใช้กรอก โดยใช้ชื่อคอลัมน์
        #     "ดิบ" เหมือนกับข้อมูลก่อนทำ preprocessing ตอนฝึกโมเดล
        # ---------------------------------------------------
        raw_input = pd.DataFrame(
            {
                "age": [age],
                "temperature": [temperature],
                "gender": [gender],
                "cough": [cough],
                "fever": [fever],
                "shortness_of_breath": [shortness_of_breath],
                "xray_result": [xray_result],
            }
        )

        # ---------------------------------------------------
        # 4.2 แปลงข้อความภาษาไทยให้เป็นรหัส/ภาษาอังกฤษแบบเดียว
        #     กับตอนเตรียมข้อมูลฝึกโมเดล (ถ้าตอนฝึกใช้ค่าอื่น
        #     ให้แก้ mapping ตรงนี้ให้ตรงกัน)
        # ---------------------------------------------------
        mapping = {
            "มี": "yes",
            "ไม่มี": "no",
            "ชาย": "male",
            "หญิง": "female",
        }
        for col in ["gender", "cough", "fever", "shortness_of_breath"]:
            raw_input[col] = raw_input[col].map(mapping)

        # ---------------------------------------------------
        # 4.3 ทำ One-Hot Encoding ให้เหมือนกับตอนฝึกโมเดล
        #     *** สำคัญมาก ***
        #     ต้องใช้ pd.get_dummies() แล้ว "reindex" คอลัมน์ให้ตรง
        #     ลำดับ/ชื่อคอลัมน์เดียวกับตอนฝึกโมเดลทุกประการ
        #     แนะนำให้บันทึกรายชื่อคอลัมน์ตอนฝึก (เช่น model_columns.pkl)
        #     ไว้คู่กับโมเดล แล้วโหลดมาใช้ reindex ตรงนี้
        # ---------------------------------------------------
        categorical_cols = ["gender", "cough", "fever", "shortness_of_breath", "xray_result"]
        encoded_input = pd.get_dummies(raw_input, columns=categorical_cols)

        # *** ตัวอย่างรายชื่อคอลัมน์ทั้งหมดตอนฝึกโมเดล (ต้องแก้ให้ตรงของจริง) ***
        # วิธีที่ดีที่สุดคือบันทึกลิสต์นี้จากตอน train แล้วโหลดมาใช้ เช่น:
        #   model_columns = joblib.load("model_columns.pkcls")
        model_columns = [
            "age",
            "temperature",
            "gender_male",
            "gender_female",
            "cough_yes",
            "cough_no",
            "fever_yes",
            "fever_no",
            "shortness_of_breath_yes",
            "shortness_of_breath_no",
            "xray_result_ปกติ",
            "xray_result_พบฝ้าขาว (Opacity)",
            "xray_result_สงสัย Pneumonia",
        ]

        # เติมคอลัมน์ที่ขาดหาย (เช่น ตัวเลือกที่ผู้ใช้ไม่ได้เลือก) ด้วยค่า 0
        # และจัดเรียงลำดับคอลัมน์ให้ตรงกับตอนฝึกโมเดลทุกประการ
        final_input = encoded_input.reindex(columns=model_columns, fill_value=0)

        # ---------------------------------------------------
        # 4.4 ส่งเข้าโมเดลเพื่อทำนายผล
        # ---------------------------------------------------
        try:
            prediction = model.predict(final_input)[0]

            # ถ้าโมเดลรองรับ predict_proba ให้แสดงความน่าจะเป็นด้วย
            proba_text = ""
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(final_input)[0]
                proba_text = f" (ความมั่นใจ: {max(proba) * 100:.2f}%)"

            # ---------------------------------------------------
            # 5. แสดงผลการทำนายให้อ่านเข้าใจง่าย
            # ---------------------------------------------------
            # *** แก้ label ตรงนี้ให้ตรงกับค่าที่โมเดลของคุณทำนายออกมาจริง
            #     เช่น 0/1 หรือ "Covid"/"Normal" เป็นต้น ***
            label_map = {
                0: "ไม่พบเชื้อ Covid-19 (Normal)",
                1: "พบความเสี่ยงเป็น Covid-19",
            }
            result_text = label_map.get(prediction, str(prediction))

            st.success(f"ผลการทำนาย: {result_text}{proba_text}")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดระหว่างการทำนายผล: {e}")
            st.info(
                "สาเหตุที่พบบ่อย: จำนวน/ชื่อ/ลำดับคอลัมน์ของข้อมูลไม่ตรงกับ "
                "ตอนฝึกโมเดล กรุณาตรวจสอบ model_columns ให้ตรงกับของจริง"
            )
