"""
app.py
------
เว็บแอป Streamlit สำหรับโหลดโมเดลที่ฝึกไว้แล้วจากโปรแกรม Orange
(ไฟล์ .pkcls) และใช้ทำนายผลการจำแนกโรค Covid จากภาพ X-ray

*** อัปเดตสำคัญ ***
จากการทดสอบจริงพบว่าไฟล์ .pkcls ที่ export มาจากโปรแกรม "Orange"
(Orange Data Mining / Orange3) ไม่ใช่โมเดล scikit-learn ธรรมดา
แต่เป็นอ็อบเจกต์ของไลบรารี Orange3 ซึ่งมีโครงสร้างข้อมูลของตัวเอง
เรียกว่า Orange.data.Table/Domain

ข้อดีคือ: โมเดลของ Orange จะ "เก็บชื่อและชนิดของทุกฟีเจอร์" ไว้ใน
model.domain อยู่แล้ว ทำให้แอปนี้สามารถ "สร้างฟอร์มกรอกข้อมูล
อัตโนมัติ" ให้ตรงกับโมเดลที่โหลดเข้ามาได้เลย โดยไม่ต้องเขียน
ชื่อคอลัมน์ตายตัวในโค้ด (ต่างจากเวอร์ชันก่อนหน้า)
"""

import streamlit as st
import joblib
import io
import os
import Orange

# ต้องติดตั้งไลบรารี Orange3 (ดู requirements.txt) จึงจะ import ได้
from Orange.data import Domain, Table

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

model_source = st.radio(
    "เลือกวิธีโหลดโมเดล",
    ("อัปโหลดไฟล์โมเดล (.pkcls)", "ระบุพาธไฟล์ในเครื่อง/เซิร์ฟเวอร์"),
)

model = None  # ตัวแปรเก็บโมเดล Orange ที่โหลดสำเร็จ

if model_source == "อัปโหลดไฟล์โมเดล (.pkcls)":
    uploaded_model_file = st.file_uploader(
        "อัปโหลดไฟล์โมเดล (.pkcls)", type=["pkcls"]
    )
    if uploaded_model_file is not None:
        try:
            model = joblib.load(io.BytesIO(uploaded_model_file.getvalue()))
            st.success(f"โหลดโมเดล '{uploaded_model_file.name}' สำเร็จ")
        except Exception as e:
            st.error(f"โหลดโมเดลไม่สำเร็จ: {e}")

else:
    default_dir = "./models"
    if os.path.isdir(default_dir):
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
# 3. ส่วนกรอกค่าตัวแปรต้น (features) -- สร้างอัตโนมัติจาก model.domain
# ============================================================
st.header("2) กรอกข้อมูลผู้ป่วย (Features)")

if model is None:
    st.info("กรุณาเลือก/อัปโหลดโมเดลก่อน เพื่อให้ระบบสร้างฟอร์มกรอกข้อมูลให้อัตโนมัติ")
else:
    # ตรวจสอบว่าเป็นโมเดล Orange จริง (ต้องมี attribute .domain)
    if not hasattr(model, "domain"):
        st.error(
            "โมเดลที่โหลดมาไม่มี attribute 'domain' "
            "อาจไม่ใช่โมเดลจาก Orange หรือไฟล์เสียหาย"
        )
    else:
        domain = model.domain
        user_inputs = {}  # เก็บค่าที่ผู้ใช้กรอก key = ชื่อฟีเจอร์

        with st.form("prediction_form"):
            # วนลูปตามฟีเจอร์ทุกตัวที่โมเดลนี้ใช้ตอนฝึกจริง (domain.attributes)
            for attr in domain.attributes:
                if attr.is_continuous:
                    # ฟีเจอร์ตัวเลข -> ใช้ st.number_input
                    user_inputs[attr.name] = st.number_input(
                        attr.name, value=0.0, format="%.4f"
                    )
                elif attr.is_discrete:
                    # ฟีเจอร์หมวดหมู่ -> ใช้ st.selectbox พร้อมตัวเลือกจริงจาก
                    # ตอนฝึกโมเดล (attr.values)
                    user_inputs[attr.name] = st.selectbox(attr.name, list(attr.values))
                else:
                    # ชนิดอื่น (เช่น string/time) -> ใช้ text_input เป็นค่าเริ่มต้น
                    user_inputs[attr.name] = st.text_input(attr.name)

            submitted = st.form_submit_button("ทำนายผล")

        # ========================================================
        # 4. เมื่อกดปุ่ม 'ทำนายผล' -> จัดรูปแบบข้อมูลให้ตรงกับตอนฝึกโมเดล
        # ========================================================
        if submitted:
            try:
                # ---------------------------------------------------
                # 4.1 แปลงค่าที่ผู้ใช้กรอกให้เป็นรหัสตัวเลขตามที่ Orange
                #     ใช้ภายใน (attr.to_val ทำหน้าที่แปลงให้อัตโนมัติ
                #     ทั้งฟีเจอร์ตัวเลขและฟีเจอร์หมวดหมู่ / ทำหน้าที่
                #     เทียบเท่า one-hot / label encoding ตอนฝึกโมเดล)
                # ---------------------------------------------------
                row = [
                    attr.to_val(user_inputs[attr.name]) for attr in domain.attributes
                ]

                # ---------------------------------------------------
                # 4.2 สร้าง Orange.data.Table จาก domain ของโมเดล (ไม่รวม
                #     class variable เพราะเราไม่รู้คำตอบล่วงหน้า)
                # ---------------------------------------------------
                input_domain = Domain(domain.attributes)
                input_table = Table.from_list(input_domain, [row])

                # ---------------------------------------------------
                # 4.3 ส่งเข้าโมเดลเพื่อทำนายผล พร้อมความน่าจะเป็น
                #     model.ValueProbs คือค่าคงที่ของ Orange.base.Model
                #     ที่บอกให้คืนทั้ง "คำตอบ" และ "ความน่าจะเป็น"
                # ---------------------------------------------------
                value, probs = model(input_table, model.ValueProbs)
                predicted_index = int(value[0])
                confidence = float(max(probs[0])) * 100

                # ---------------------------------------------------
                # 5. แสดงผลการทำนายให้อ่านเข้าใจง่าย
                #    ใช้ domain.class_var.values เพื่อแปลงรหัสกลับเป็น
                #    ชื่อคลาสจริง (เช่น "Covid" / "Normal") ตามที่ตั้งไว้
                #    ตอนฝึกโมเดล -- ไม่ต้องเดา label เอง
                # ---------------------------------------------------
                predicted_label = domain.class_var.values[predicted_index]
                st.success(
                    f"ผลการทำนาย: {predicted_label} "
                    f"(ความมั่นใจ: {confidence:.2f}%)"
                )

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดระหว่างการทำนายผล: {e}")
                st.info(
                    "ตรวจสอบว่าเลือกไฟล์โมเดล (.pkcls) ที่ถูกต้อง และค่าที่กรอก "
                    "อยู่ในรูปแบบ/ตัวเลือกที่โมเดลรู้จัก"
                )
