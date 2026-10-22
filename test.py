
import streamlit as st
import requests
import time
import json

# =========================================
# ตั้งค่าหน้าเว็บ
# =========================================
st.set_page_config(
    page_title="ทดสอบ RID Overflow API",
    page_icon="🌊",
    layout="wide"
)

st.title("🌊 ทดสอบ API ระดับน้ำล้นตลิ่ง")
st.write("ทดสอบการเชื่อมต่อจาก Render ไปยังกรมชลประทาน")

API_URL = (
    "https://hyd-app-db.rid.go.th/"
    "webservice/getWaterLevelListReportOverflowWaterLevel.ashx"
)

# =========================================
# ช่องกรอกข้อมูล
# =========================================
date = st.text_input(
    "วันที่ (วัน/เดือน/ปี พ.ศ.)",
    value="01/09/2569",
    help="ตัวอย่าง 01/09/2569"
)

hour = st.selectbox(
    "เวลา",
    [
        "00:00:00",
        "06:00:00",
        "12:00:00",
        "16:00:00",
        "18:00:00"
    ],
    index=1
)

# =========================================
# ปุ่มเรียก API
# =========================================
if st.button("ดึงข้อมูลจาก API", type="primary"):

    data = {
        "DW[HourlyTime]": hour,
        "DW[TimeCurrent]": date.strip(),
        "_search": "false",
        "nd": str(int(time.time() * 1000)),
        "rows": "1000",
        "page": "1",
        "sidx": "indexcount",
        "sord": "asc"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*"
    }

    st.info("กำลังเชื่อมต่อ API จากเซิร์ฟเวอร์ Render...")

    start_time = time.time()

    try:
        response = requests.post(
            API_URL,
            data=data,
            headers=headers,
            timeout=(15, 60)
        )

        elapsed = round(time.time() - start_time, 2)

        st.subheader("1. ผลการเชื่อมต่อ")

        col1, col2, col3 = st.columns(3)

        col1.metric("HTTP Status", response.status_code)
        col2.metric("เวลาตอบกลับ", f"{elapsed} วินาที")
        col3.metric("ขนาดข้อมูล", f"{len(response.content):,} bytes")

        st.write("วันที่:", date)
        st.write("เวลา:", hour)

        response.raise_for_status()

        # แปลงข้อมูล JSON
        result = response.json()

        st.subheader("2. ผลการดึงข้อมูล")

        if not isinstance(result, dict):
            st.error("รูปแบบข้อมูลที่ API ตอบกลับไม่ใช่ JSON object")
            st.code(response.text[:5000])

        else:
            rows = result.get("rows", [])

            col1, col2 = st.columns(2)
            col1.metric(
                "จำนวน records ที่ API แจ้ง",
                result.get("records", 0)
            )
            col2.metric(
                "จำนวนแถวที่ได้รับจริง",
                len(rows)
            )

            if rows:
                st.success("ดึงข้อมูลจาก API ได้แล้ว")

                # แสดงข้อมูลทุกสถานีโดยไม่กรองน้ำล้นตลิ่ง
                st.subheader("3. ข้อมูลสถานีทั้งหมด")

                st.dataframe(
                    rows,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.warning(
                    "เชื่อมต่อ API สำเร็จ แต่ไม่มีข้อมูล "
                    "สำหรับวันที่และเวลาที่เลือก"
                )

            with st.expander("ดู JSON ดิบจาก API"):
                st.code(
                    json.dumps(
                        result,
                        ensure_ascii=False,
                        indent=2
                    ),
                    language="json"
                )

    except requests.exceptions.Timeout as e:
        elapsed = round(time.time() - start_time, 2)
        st.error(f"API ตอบกลับไม่ทันเวลา ({elapsed} วินาที)")
        st.code(repr(e))

    except requests.exceptions.ConnectionError as e:
        st.error("Render เชื่อมต่อไปยัง API ไม่สำเร็จ")
        st.code(repr(e))

    except requests.exceptions.HTTPError as e:
        st.error("API ตอบกลับด้วย HTTP Error")
        st.code(repr(e))
        st.code(response.text[:3000])

    except (ValueError, json.JSONDecodeError) as e:
        st.error("ได้รับข้อมูลกลับมา แต่แปลง JSON ไม่สำเร็จ")
        st.code(repr(e))
        st.code(response.text[:3000])

    except Exception as e:
        st.error("เกิดข้อผิดพลาดที่ไม่คาดหมาย")
        st.code(repr(e))
