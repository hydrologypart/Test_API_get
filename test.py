import streamlit as st
import socket
import requests

HOST = "hyd-app-db.rid.go.th"

st.title("ทดสอบการเชื่อมต่อ RID API")
st.write("กำลังตรวจสอบการเชื่อมต่อ API...")

try:
    ip = socket.gethostbyname(HOST)
    st.write("DNS IP:", ip)

    with socket.create_connection((HOST, 443), timeout=10) as sock:
        st.success("TCP 443: สำเร็จ")
        st.write("ปลายทาง:", sock.getpeername())

except Exception as e:
    st.error(f"เชื่อมต่อไม่สำเร็จ: {type(e).__name__}: {e}")
