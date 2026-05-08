# Food Menu App - Flask + Postgres

เว็บแอปเมนูกับข้าว ใช้ Flask + SQLAlchemy
รองรับ SQLite ตอนรันในเครื่อง และ Postgres ตอน Deploy

## รันบนคอม

```bash
pip install -r requirements.txt
python app.py
```

เปิด:

```text
http://127.0.0.1:8000
```

## Deploy บน Render + Neon

1. อัปโหลดไฟล์ขึ้น GitHub
2. สร้างฐานข้อมูล Postgres ฟรีที่ Neon
3. Copy connection string จาก Neon
4. สร้าง Web Service บน Render จาก GitHub repo
5. ตั้ง Environment Variable:

```text
DATABASE_URL=ใส่ connection string จาก Neon
```

6. Build Command:

```bash
pip install -r requirements.txt
```

7. Start Command:

```bash
gunicorn app:app
```