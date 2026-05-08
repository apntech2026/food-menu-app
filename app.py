from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

database_url = os.environ.get("DATABASE_URL", "sqlite:///food_menu.db")

# Render/Neon บางที่ให้ URL เป็น postgres:// ให้แปลงเป็น postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

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


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    foods = db.relationship("Food", backref="category", cascade="all, delete-orphan")


class Food(db.Model):
    __tablename__ = "foods"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)


def init_db():
    db.create_all()

    if Category.query.count() == 0:
        for category_name, foods in INITIAL_DATA.items():
            category = Category(name=category_name)
            db.session.add(category)
            db.session.flush()

            for food_name in foods:
                db.session.add(Food(name=food_name, category_id=category.id))

        db.session.commit()


@app.route("/")
def index():
    categories = Category.query.order_by(Category.id).all()
    return render_template("index.html", categories=categories)


@app.route("/category/add", methods=["POST"])
def add_category():
    name = request.form.get("name", "").strip()

    if name:
        exists = Category.query.filter_by(name=name).first()
        if not exists:
            db.session.add(Category(name=name))
            db.session.commit()

    return redirect(url_for("index"))


@app.route("/category/<int:category_id>")
def category(category_id):
    category = Category.query.get_or_404(category_id)
    foods = Food.query.filter_by(category_id=category_id).order_by(Food.id).all()
    return render_template("category.html", category=category, foods=foods)


@app.route("/category/<int:category_id>/edit", methods=["POST"])
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    name = request.form.get("name", "").strip()

    if name:
        category.name = name
        db.session.commit()

    return redirect(url_for("index"))


@app.route("/category/<int:category_id>/delete", methods=["POST"])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()

    return redirect(url_for("index"))


@app.route("/category/<int:category_id>/food/add", methods=["POST"])
def add_food(category_id):
    Category.query.get_or_404(category_id)
    name = request.form.get("name", "").strip()

    if name:
        db.session.add(Food(category_id=category_id, name=name))
        db.session.commit()

    return redirect(url_for("category", category_id=category_id))


@app.route("/category/<int:category_id>/food/<int:food_id>/edit", methods=["POST"])
def edit_food(category_id, food_id):
    food = Food.query.filter_by(id=food_id, category_id=category_id).first_or_404()
    name = request.form.get("name", "").strip()

    if name:
        food.name = name
        db.session.commit()

    return redirect(url_for("category", category_id=category_id))


@app.route("/category/<int:category_id>/food/<int:food_id>/delete", methods=["POST"])
def delete_food(category_id, food_id):
    food = Food.query.filter_by(id=food_id, category_id=category_id).first_or_404()
    db.session.delete(food)
    db.session.commit()

    return redirect(url_for("category", category_id=category_id))


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)