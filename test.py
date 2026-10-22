
import requests
import time

url = "https://hyd-app-db.rid.go.th/webservice/getWaterLevelListReportOverflowWaterLevel.ashx"

data = {
    "DW[HourlyTime]": "06:00:00",
    "DW[TimeCurrent]": "01/09/2569",
    "_search": "false",
    "nd": str(int(time.time() * 1000)),
    "rows": "1000",
    "page": "1",
    "sidx": "indexcount",
    "sord": "asc"
}

start = time.time()

try:
    print("เริ่มเชื่อมต่อ API...")

    response = requests.post(
        url,
        data=data,
        timeout=60
    )

    elapsed = time.time() - start

    print("HTTP Status:", response.status_code)
    print("เวลาที่ใช้:", round(elapsed, 2), "วินาที")
    print("ข้อมูลตอบกลับ:", response.text[:1000])

    response.raise_for_status()

    result = response.json()
    print("จำนวนสถานี:", result.get("records"))
    print("จำนวนแถวที่ได้รับ:", len(result.get("rows", [])))

except requests.exceptions.Timeout:
    print("ERROR: API ตอบกลับช้าเกิน 60 วินาที")

except requests.exceptions.ConnectionError as e:
    print("ERROR: เชื่อมต่อ API ไม่สำเร็จ")
    print(repr(e))

except requests.exceptions.HTTPError as e:
    print("ERROR: API ตอบกลับด้วย HTTP Error")
    print(repr(e))

except Exception as e:
    print("ERROR:", repr(e))
