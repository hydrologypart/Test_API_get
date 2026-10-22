
import streamlit as st
import socket
import requests
import time

HOST = "hyd-app-db.rid.go.th"

URL = (
    "https://hyd-app-db.rid.go.th/webservice/"
    "getWaterLevelListReportMonitorWaterLevel.ashx"
)

st.title("ทดสอบการเชื่อมต่อ RID API")
st.write("ทดสอบจาก Streamlit Community Cloud")

if st.button("ทดสอบการเชื่อมต่อและดึงข้อมูล"):
    # 1. DNS
    try:
        ip = socket.gethostbyname(HOST)
        st.write("DNS IP:", ip)
    except Exception as e:
        st.error(f"DNS ERROR: {e}")
        st.stop()

    # 2. TCP
    try:
        with socket.create_connection(
            (HOST, 443), timeout=10
        ) as sock:
            st.success("TCP 443: สำเร็จ")
            st.write("ปลายทาง:", sock.getpeername())
    except Exception as e:
        st.error(f"TCP ERROR: {type(e).__name__}: {e}")

    # 3. POST API
    data = {
        "DW[HourlyTime]": "06:00:00",
        "DW[TimeCurrent]": "05/10/2569",
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

    try:
        with st.spinner("กำลังส่งคำขอ POST ไปยัง RID API..."):
            response = requests.post(
                URL,
                data=data,
                headers=headers,
                timeout=(15, 30)
            )

        st.write("HTTP Status:", response.status_code)

        if response.ok:
            result = response.json()
            rows = result.get("rows", [])

            st.success("เรียก API สำเร็จ")
            st.metric(
                "จำนวน records",
                result.get("records", len(rows))
            )
            st.write("ตัวอย่างข้อมูล:")
            st.json(rows[:5])
        else:
            st.error("API ตอบกลับด้วย HTTP Status ที่ไม่ใช่ 2xx")
            st.code(response.text[:1000])

    except Exception as e:
        st.error(f"POST ERROR: {type(e).__name__}: {e}")
