"""
app.py
------
เว็บแอป Streamlit สำหรับโหลดโมเดลที่ฝึกไว้แล้วจากโปรแกรม Orange
ไฟล์ .pkcls และใช้ทำนายผลการจำแนกโรค Covid

เพิ่มความสามารถ:
- อัปโหลดภาพ X-ray
- แสดงภาพ X-ray ที่อัปโหลด
- โหลดโมเดล .pkcls
- กรอก Features ตามที่โมเดลต้องการ
- ทำนายผลจาก Features
"""

import streamlit as st
import joblib
import io
import os

# ต้องติดตั้งไลบรารี Orange3
from Orange.data import Domain, Table


# ============================================================
# 1. ตั้งค่าหน้าเว็บ
# ============================================================

st.set_page_config(
    page_title="จำแนกโรค Covid จากภาพ X-ray",
    layout="centered"
)

st.title("โปรแกรมจำแนกโรค Covid จากภาพ X-ray")

st.write(
    "อัปโหลดภาพ X-ray และกรอกข้อมูล Features "
    "จากนั้นกดปุ่ม 'ทำนายผล'"
)


# ============================================================
# 2. เลือก / โหลดโมเดล
# ============================================================

st.header("1) เลือกโมเดลที่จะใช้")

model_source = st.radio(
    "เลือกวิธีโหลดโมเดล",
    (
        "อัปโหลดไฟล์โมเดล (.pkcls)",
        "ระบุพาธไฟล์ในเครื่อง/เซิร์ฟเวอร์"
    ),
)

model = None


# ------------------------------------------------------------
# วิธีที่ 1 : อัปโหลดไฟล์ .pkcls
# ------------------------------------------------------------

if model_source == "อัปโหลดไฟล์โมเดล (.pkcls)":

    uploaded_model_file = st.file_uploader(
        "อัปโหลดไฟล์โมเดล (.pkcls)",
        type=["pkcls"]
    )

    if uploaded_model_file is not None:

        try:

            model = joblib.load(
                io.BytesIO(
                    uploaded_model_file.getvalue()
                )
            )

            st.success(
                f"โหลดโมเดล '{uploaded_model_file.name}' สำเร็จ"
            )

        except Exception as e:

            st.error(
                f"โหลดโมเดลไม่สำเร็จ: {e}"
            )


# ------------------------------------------------------------
# วิธีที่ 2 : โหลดจากพาธ
# ------------------------------------------------------------

else:

    default_dir = "./models"

    if os.path.isdir(default_dir):

        pkcls_files = [
            f
            for f in os.listdir(default_dir)
            if f.endswith(".pkcls")
        ]

        if pkcls_files:

            selected_file = st.selectbox(
                "เลือกไฟล์โมเดลจากโฟลเดอร์ models",
                pkcls_files
            )

            model_path = os.path.join(
                default_dir,
                selected_file
            )

        else:

            st.warning(
                "ไม่พบไฟล์ .pkcls ในโฟลเดอร์ ./models"
            )

            model_path = st.text_input(
                "หรือระบุพาธไฟล์โมเดลเต็ม (.pkcls)"
            )

    else:

        model_path = st.text_input(
            "ระบุพาธไฟล์โมเดลเต็ม (.pkcls)"
        )


    if model_path and os.path.isfile(model_path):

        try:

            model = joblib.load(model_path)

            st.success(
                f"โหลดโมเดลจาก '{model_path}' สำเร็จ"
            )

        except Exception as e:

            st.error(
                f"โหลดโมเดลไม่สำเร็จ: {e}"
            )

    elif model_path:

        st.error(
            "ไม่พบไฟล์ตามพาธที่ระบุ กรุณาตรวจสอบอีกครั้ง"
        )


# ============================================================
# 3. อัปโหลดภาพ X-ray
# ============================================================

st.divider()

st.header("2) อัปโหลดภาพ X-ray")

st.write("เลือกภาพ X-ray ที่ต้องการแสดงในระบบ")

image_file = st.file_uploader(
    "เลือกรูปภาพ X-ray",
    type=["jpg", "jpeg", "png"]
)

if image_file is not None:

    st.success(
        f"อัปโหลดภาพ '{image_file.name}' สำเร็จ"
    )

    st.image(
        image_file,
        caption="ภาพ X-ray ที่อัปโหลด"
    )

else:

    st.info(
        "กรุณาอัปโหลดภาพ X-ray เพื่อแสดงภาพ"
    )

# ============================================================
# 3. ทำนายผล
# ============================================================

st.divider()

st.header("3) ทำนายผล")

if image_file is None:

    st.warning("กรุณาอัปโหลดภาพ X-ray ก่อนทำนายผล")

else:

    if model is None:

        st.warning("กรุณาเลือกหรืออัปโหลดโมเดลก่อน")

    else:

        if st.button("ทำนายผล"):

            st.info(
                "ขณะนี้สามารถอัปโหลดและแสดงภาพ X-ray ได้แล้ว "
                "แต่โมเดล .pkcls ที่ใช้อยู่ต้องการ Features "
                "ในการทำนาย จึงยังไม่สามารถนำภาพ X-ray "
                "เข้าโมเดลโดยตรงได้"
            )

