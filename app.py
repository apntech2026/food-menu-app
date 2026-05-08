from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", "food_menu.db")

INITIAL_DATA = {
    "ต้ม": [
        "ต้มจืดไข่น้ำ",
        "ต้มเล้งแซ่บ",
        "ต้มยำกุ้ง",
        "ต้มยำกุ้งแม่น้ำ",
        "ต้มยำรวมมิตรน้ำข้น",
        "ต้มแซ่บเนื้อน่องลาย",
        "ต้มแซ่บกระดูกหมูอ่อน",
        "ต้มข่าไก่",
        "ปีกไก่ต้มโค้ก",
        "ต้มผักกาดดอง",
    ],
    "ผัด": [
        "ผัดกะเพราหมูสับ",
        "ผัดกะเพราเนื้อสับ",
        "ผัดผักบุ้งจีน",
        "ผัดเผ็ดหน่อไม้ดองใบยี่หร่า",
        "ผัดดอกกะหล่ำ",
        "ผัดบล็อคโคลี่กุ้ง",
        "ผัดยอดฟักแม้ว",
        "ผัดตับดอกหอม",
        "ผัดพริกเหลืองถั่วลันเตาหวาน",
        "ผัดกะเพราปลาหมึก",
        "ผัดกะเพราหมูกรอบ",
        "ผัดคะน้าหมูกรอบ",
        "ผัดระเบิดเนื้อสับ",
        "ผัดระเบิดปลาหมึก",
        "ผัดกะเพราตับไก่",
        "ผัดหมูกระเทียม",
    ],
    "แกง": [
        "แกงส้มกุ้ง",
        "แกงปูใบชะพลู",
        "แกงเขียวหวานไก่",
        "แกงเขียวหวานเนื้อ",
        "แกงเขียวลูกชิ้นปลากราย",
        "แกงป่าเนื้อ",
        "แกงไก่หม้อแม่นุ่น",
        "แกงเผ็ดมะเขือลูกชิ้นปลากราย",
        "ขนมจีนน้ำยา",
    ],
    "ทอด": [
        "กุ้งแม่น้ำทอดเกลือ",
        "หมูทอด",
        "เนื้อเค็มทอด",
        "ปีกไก่ทอด",
        "ปลาตะเพียนทอด",
        "ปลาลิ้นหมาทอด",
    ],
    "ย่าง": [
        "ปลาช่อนย่าง",
        "กุ้งแม่น้ำเผา",
    ],
    "ลาบ&ยำ": [
        "ยำไข่ดาว",
        "ยำกุนเชียง",
        "พล่ากุ้ง",
        "ลาบหมู",
        "ลาบเป็ด",
        "ลาบไก่",
        "ยำเนื้อย่าง",
        "ลาบปลาดุก",
        "ยำวุ้นเส้น",
        "ยำคอหมูย่าง",
        "ยำปลาดุกฟู",
    ],
    "เมนูพิเศษ": [
        "ก๋วยเตี๋ยวเนื้อตุ๋น",
        "ข้าวมันไก่",
        "ข้าวผัดแหนม",
        "ข้าวผัดกุนเชียง",
        "มาม่าผัดขี้เมา",
        "สปาเก็ตตี้ขี้เมา",
        "สปาเก็ตตี้ต้มยำ",
        "ข้าวผัดต้มยำ",
        "สุกี้น้ำ/แห้งหมู",
    ],
}


def get_db():
    if "db" not in g:
        db_dir = os.path.dirname(DB_PATH)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row

    db.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
        )
    """)

    count = db.execute("SELECT COUNT(*) AS total FROM categories").fetchone()["total"]

    if count == 0:
        for category_name, foods in INITIAL_DATA.items():
            cursor = db.execute(
                "INSERT INTO categories (name) VALUES (?)",
                (category_name,)
            )
            category_id = cursor.lastrowid

            for food_name in foods:
                db.execute(
                    "INSERT INTO foods (category_id, name) VALUES (?, ?)",
                    (category_id, food_name)
                )

    db.commit()
    db.close()


@app.route("/")
def index():
    db = get_db()
    categories = db.execute("""
        SELECT 
            categories.id,
            categories.name,
            COUNT(foods.id) AS food_count
        FROM categories
        LEFT JOIN foods ON foods.category_id = categories.id
        GROUP BY categories.id
        ORDER BY categories.id
    """).fetchall()

    return render_template("index.html", categories=categories)


@app.route("/category/add", methods=["POST"])
def add_category():
    name = request.form.get("name", "").strip()

    if name:
        db = get_db()
        try:
            db.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            db.commit()
        except sqlite3.IntegrityError:
            pass

    return redirect(url_for("index"))


@app.route("/category/<int:category_id>")
def category(category_id):
    db = get_db()

    category = db.execute(
        "SELECT * FROM categories WHERE id = ?",
        (category_id,)
    ).fetchone()

    if category is None:
        return "ไม่พบประเภทเมนูนี้", 404

    foods = db.execute(
        "SELECT * FROM foods WHERE category_id = ? ORDER BY id",
        (category_id,)
    ).fetchall()

    return render_template("category.html", category=category, foods=foods)


@app.route("/category/<int:category_id>/edit", methods=["POST"])
def edit_category(category_id):
    name = request.form.get("name", "").strip()

    if name:
        db = get_db()
        try:
            db.execute(
                "UPDATE categories SET name = ? WHERE id = ?",
                (name, category_id)
            )
            db.commit()
        except sqlite3.IntegrityError:
            pass

    return redirect(url_for("index"))


@app.route("/category/<int:category_id>/delete", methods=["POST"])
def delete_category(category_id):
    db = get_db()
    db.execute("DELETE FROM foods WHERE category_id = ?", (category_id,))
    db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    db.commit()

    return redirect(url_for("index"))


@app.route("/category/<int:category_id>/food/add", methods=["POST"])
def add_food(category_id):
    name = request.form.get("name", "").strip()

    if name:
        db = get_db()
        db.execute(
            "INSERT INTO foods (category_id, name) VALUES (?, ?)",
            (category_id, name)
        )
        db.commit()

    return redirect(url_for("category", category_id=category_id))


@app.route("/category/<int:category_id>/food/<int:food_id>/edit", methods=["POST"])
def edit_food(category_id, food_id):
    name = request.form.get("name", "").strip()

    if name:
        db = get_db()
        db.execute(
            "UPDATE foods SET name = ? WHERE id = ? AND category_id = ?",
            (name, food_id, category_id)
        )
        db.commit()

    return redirect(url_for("category", category_id=category_id))


@app.route("/category/<int:category_id>/food/<int:food_id>/delete", methods=["POST"])
def delete_food(category_id, food_id):
    db = get_db()
    db.execute(
        "DELETE FROM foods WHERE id = ? AND category_id = ?",
        (food_id, category_id)
    )
    db.commit()

    return redirect(url_for("category", category_id=category_id))


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)