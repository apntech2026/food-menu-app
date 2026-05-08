# Food Menu CRUD Flask App

เว็บแอปจัดการเมนูกับข้าวด้วย Flask + SQLite

## ความสามารถ

- เพิ่ม / ลบ / แก้ไข ประเภทกับข้าว
- เพิ่ม / ลบ / แก้ไข เมนูกับข้าว
- แสดงเมนูแยกตามประเภท
- รองรับมือถือ
- มีไฟล์สำหรับ Deploy ขึ้น Render

## วิธีรันบนคอม

```bash
pip install -r requirements.txt
python app.py
```

เปิดเว็บ:

```text
http://127.0.0.1:8000
```

## Deploy ขึ้น Render

1. อัปโหลดโปรเจกต์นี้ขึ้น GitHub
2. เข้า Render
3. New > Web Service
4. เลือก GitHub repo
5. ตั้งค่า:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
6. กด Deploy

## หมายเหตุเรื่องฐานข้อมูลบน Render

แอปนี้ใช้ SQLite โดยค่าเริ่มต้นไฟล์ฐานข้อมูลชื่อ `food_menu.db`

ถ้าจะให้ข้อมูลไม่หายบน Render ควรใช้ Persistent Disk แล้วตั้งค่า Environment Variable:

```text
DB_PATH=/var/data/food_menu.db
```