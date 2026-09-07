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


# ------------------------------------------------------------
# แสดงภาพ X-ray
# ------------------------------------------------------------

if image_file is not None:

    st.success(
        f"อัปโหลดภาพ '{image_file.name}' สำเร็จ"
    )

    st.image(
        image_file,
        caption="ภาพ X-ray ที่อัปโหลด",
    )

else:

    st.info(
        "กรุณาอัปโหลดภาพ X-ray เพื่อแสดงภาพ"
    )


# ============================================================
# 4. กรอกค่าตัวแปร Features
# ============================================================

st.divider()

st.header("3) กรอกข้อมูลผู้ป่วย (Features)")


# ------------------------------------------------------------
# ตรวจสอบว่ามีโมเดลหรือไม่
# ------------------------------------------------------------

if model is None:

    st.info(
        "กรุณาเลือกหรืออัปโหลดโมเดลก่อน "
        "เพื่อให้ระบบสร้างฟอร์มกรอกข้อมูลให้อัตโนมัติ"
    )

else:

    # --------------------------------------------------------
    # ตรวจสอบว่าเป็นโมเดล Orange หรือไม่
    # --------------------------------------------------------

    if not hasattr(model, "domain"):

        st.error(
            "โมเดลที่โหลดมาไม่มี attribute 'domain' "
            "อาจไม่ใช่โมเดลจาก Orange หรือไฟล์เสียหาย"
        )

    else:

        domain = model.domain

        user_inputs = {}


        # ====================================================
        # สร้างแบบฟอร์มตาม Features ของโมเดล
        # ====================================================

        with st.form("prediction_form"):

            st.write(
                "กรอกข้อมูลตาม Features ที่โมเดลต้องการ"
            )

            # ------------------------------------------------
            # วนตาม Features ของโมเดล
            # ------------------------------------------------

            for attr in domain.attributes:

                # --------------------------------------------
                # Feature เป็นตัวเลข
                # --------------------------------------------

                if attr.is_continuous:

                    user_inputs[attr.name] = st.number_input(
                        attr.name,
                        value=0.0,
                        format="%.4f"
                    )

                # --------------------------------------------
                # Feature เป็นหมวดหมู่
                # --------------------------------------------

                elif attr.is_discrete:

                    user_inputs[attr.name] = st.selectbox(
                        attr.name,
                        list(attr.values)
                    )

                # --------------------------------------------
                # Feature ชนิดอื่น
                # --------------------------------------------

                else:

                    user_inputs[attr.name] = st.text_input(
                        attr.name
                    )


            # ------------------------------------------------
            # ปุ่มทำนาย
            # ------------------------------------------------

            submitted = st.form_submit_button(
                "ทำนายผล"
            )


        # ====================================================
        # 5. ทำนายผล
        # ====================================================

        if submitted:

            try:

                # --------------------------------------------
                # แปลงข้อมูลให้ตรงกับ Orange
                # --------------------------------------------

                row = [
                    attr.to_val(
                        user_inputs[attr.name]
                    )
                    for attr in domain.attributes
                ]


                # --------------------------------------------
                # สร้าง Orange Table
                # --------------------------------------------

                input_domain = Domain(
                    domain.attributes
                )

                input_table = Table.from_list(
                    input_domain,
                    [row]
                )


                # --------------------------------------------
                # ส่งข้อมูลเข้าโมเดล
                # --------------------------------------------

                value, probs = model(
                    input_table,
                    model.ValueProbs
                )


                # --------------------------------------------
                # หาค่าผลลัพธ์
                # --------------------------------------------

                predicted_index = int(
                    value[0]
                )

                confidence = float(
                    max(probs[0])
                ) * 100


                # --------------------------------------------
                # แปลงหมายเลขเป็นชื่อ Class
                # --------------------------------------------

                predicted_label = (
                    domain.class_var.values[
                        predicted_index
                    ]
                )


                # =================================================
                # 6. แสดงผล
                # =================================================

                st.divider()

                st.header("4) ผลการทำนาย")


                st.success(
                    f"ผลการทำนาย: {predicted_label}"
                )

                st.info(
                    f"ความมั่นใจ: {confidence:.2f}%"
                )


            except Exception as e:

                st.error(
                    f"เกิดข้อผิดพลาดระหว่างการทำนายผล: {e}"
                )

                st.info(
                    "ตรวจสอบว่าเลือกไฟล์โมเดล (.pkcls) "
                    "ที่ถูกต้อง และค่าที่กรอกอยู่ในรูปแบบ "
                    "หรือตัวเลือกที่โมเดลรู้จัก"
                )


# ============================================================
# หมายเหตุ
# ============================================================

st.divider()

st.caption(
    "หมายเหตุ: ระบบนี้ใช้สำหรับการศึกษาและการสาธิต "
    "ไม่ควรใช้ผลการทำนายแทนการวินิจฉัยโดยแพทย์"
)
