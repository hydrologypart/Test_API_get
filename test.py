import streamlit as st
import requests
import time
import json
import socket

st.set_page_config(
    page_title="ทดสอบ RID Overflow API",
    page_icon="🌊",
    layout="wide"
)

st.title("🌊 ทดสอบ API ระดับน้ำล้นตลิ่ง")
st.write("ตรวจสอบการเชื่อมต่อจาก Render ไปยังกรมชลประทาน")

API_URL = (
    "https://hyd-app-db.rid.go.th/"
    "webservice/getWaterLevelListReportOverflowWaterLevel.ashx"
)

HOST = "hyd-app-db.rid.go.th"

# -----------------------------
# ส่วนเลือกวันที่และเวลา
# -----------------------------

date = st.text_input(
    "วันที่ (วัน/เดือน/ปี พ.ศ.)",
    value="05/10/2569",
    help="ตัวอย่าง 05/10/2569"
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

# -----------------------------
# ปุ่มดึงข้อมูล
# -----------------------------

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

    start_time = time.time()
    response = None

    st.info("กำลังตรวจสอบการเชื่อมต่อจาก Render...")

    # -----------------------------
    # 1. ตรวจสอบ DNS
    # -----------------------------

    st.subheader("1. ตรวจสอบ DNS")

    try:
        ip_address = socket.gethostbyname(HOST)
        st.success(f"ค้นหา IP สำเร็จ: {ip_address}")

    except Exception as e:
        st.error("ไม่สามารถค้นหา IP ของเซิร์ฟเวอร์ API ได้")
        st.code(repr(e))
        st.stop()

    # -----------------------------
    # 2. ตรวจสอบ TCP พอร์ต 443
    # -----------------------------

    st.subheader("2. ตรวจสอบการเชื่อมต่อพอร์ต 443")

    try:
        with socket.create_connection((HOST, 443), timeout=10):
            st.success("เชื่อมต่อพอร์ต 443 สำเร็จ")

    except Exception as e:
        st.error(
            "Render ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ปลายทาง "
            "ผ่านพอร์ต 443 ได้"
        )
        st.code(repr(e))
        st.info(
            "ปัญหาเกิดก่อนรับข้อมูลจาก API "
            "จึงควรตรวจสอบเส้นทางเครือข่ายหรือเซิร์ฟเวอร์ปลายทาง"
        )
        st.stop()

    # -----------------------------
    # 3. เรียก API ด้วย POST
    # -----------------------------

    st.subheader("3. เรียก API")

    try:
        with st.spinner("กำลังส่งคำขอและรอข้อมูลจากกรมชลประทาน..."):

            response = requests.post(
                API_URL,
                data=data,
                headers=headers,
                timeout=(45, 60)
            )

        elapsed = round(time.time() - start_time, 2)

        st.success("ได้รับการตอบกลับจากเซิร์ฟเวอร์แล้ว")

        col1, col2, col3 = st.columns(3)
        col1.metric("HTTP Status", response.status_code)
        col2.metric("เวลาที่ใช้", f"{elapsed} วินาที")
        col3.metric("ขนาดข้อมูล", f"{len(response.content):,} bytes")

        response.raise_for_status()

        result = response.json()

        if not isinstance(result, dict):
            st.error("รูปแบบข้อมูลที่ได้รับไม่ใช่ JSON object")
            st.code(response.text[:5000])
            st.stop()

        # -----------------------------
        # 4. แสดงผลข้อมูลทั้งหมดที่ API ส่งกลับ
        # -----------------------------

        rows = result.get("rows", [])

        st.subheader("4. ผลการดึงข้อมูล")

        col1, col2 = st.columns(2)
        col1.metric(
            "จำนวน records ที่ API แจ้ง",
            result.get("records", 0)
        )
        col2.metric(
            "จำนวนแถวที่ได้รับจริง",
            len(rows)
        )

        st.write("วันที่:", date)
        st.write("เวลา:", hour)

        if rows:
            st.success("ดึงข้อมูลสถานีได้แล้ว")

            st.subheader("ข้อมูลสถานีทั้งหมด")

            # แสดงข้อมูลทุกแถวที่ API ส่งกลับมา
            if all(isinstance(row, dict) for row in rows):
                st.dataframe(
                    rows,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.json(rows)

            # ปุ่มดาวน์โหลดข้อมูลเป็น JSON
            json_data = json.dumps(
                result,
                ensure_ascii=False,
                indent=2
            )

            st.download_button(
                label="ดาวน์โหลดข้อมูลทั้งหมด (JSON)",
                data=json_data,
                file_name=f"RID_Overflow_{date.replace('/', '-')}_{hour.replace(':', '-')}.json",
                mime="application/json"
            )

        else:
            st.warning(
                "เชื่อมต่อสำเร็จ แต่ไม่มีข้อมูลสำหรับวันที่และเวลาที่เลือก"
            )

        with st.expander("ดู JSON ดิบจาก API"):
            st.code(
                json.dumps(result, ensure_ascii=False, indent=2),
                language="json"
            )

    except requests.exceptions.ConnectTimeout as e:
        elapsed = round(time.time() - start_time, 2)
        st.error(
            f"หมดเวลาระหว่างพยายามเชื่อมต่อ API "
            f"({elapsed} วินาที)"
        )
        st.code(repr(e))

    except requests.exceptions.ReadTimeout as e:
        elapsed = round(time.time() - start_time, 2)
        st.error(
            f"เชื่อมต่อได้แล้ว แต่รอ API ส่งข้อมูลนานเกินกำหนด "
            f"({elapsed} วินาที)"
        )
        st.code(repr(e))

    except requests.exceptions.Timeout as e:
        st.error("การเรียก API ใช้เวลานานเกินกำหนด")
        st.code(repr(e))

    except requests.exceptions.ConnectionError as e:
        st.error("เกิดปัญหาการเชื่อมต่อระหว่างเรียก API")
        st.code(repr(e))

    except requests.exceptions.HTTPError as e:
        st.error("API ตอบกลับด้วย HTTP Error")
        st.code(repr(e))

        if response is not None:
            st.code(response.text[:3000])

    except (ValueError, json.JSONDecodeError) as e:
        st.error("ได้รับข้อมูลกลับมา แต่แปลง JSON ไม่สำเร็จ")
        st.code(repr(e))

        if response is not None:
            st.code(response.text[:3000])

    except Exception as e:
        st.error("เกิดข้อผิดพลาดที่ไม่คาดหมาย")
        st.code(repr(e))
