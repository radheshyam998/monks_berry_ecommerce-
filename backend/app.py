import os
import uuid
from datetime import datetime
from io import BytesIO

from flask import Flask, jsonify, request, send_from_directory, send_file, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import func
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from config import Config
from models import db, User, Product, Order, OrderItem

app = Flask(__name__, static_folder="static", static_url_path="/static")
@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    from flask import Response

    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://the-monks-berry-95z0.onrender.com/</loc>
    </url>
</urlset>"""

    return Response(xml, status=200, mimetype="application/xml")


@app.route("/robots.txt", methods=["GET"])
def robots_txt():
    from flask import Response

    content = """User-agent: *
Allow: /

Sitemap: https://the-monks-berry-95z0.onrender.com/sitemap.xml
"""
    return Response(content, status=200, mimetype="text/plain")


app.config.from_object(Config)
db.init_app(app)
JWTManager(app)
CORS(app)

def current_user():
    uid = get_jwt_identity()
    return User.query.get(int(uid))

def product_or_404(pid):
    return Product.query.get_or_404(pid)

def seed_data():
    admin = User.query.filter_by(email=app.config["ADMIN_EMAIL"]).first()
    if not admin:
        admin = User(
            name="Store Admin",
            email=app.config["ADMIN_EMAIL"],
            role="admin",
            phone=""
        )
        admin.set_password(app.config["ADMIN_PASSWORD"])
        db.session.add(admin)

    if Product.query.count() == 0:
        products = [
            Product(
                name="Rosehip Pulp",
                slug="rosehip-pulp",
                short_description="100% pure & original rosehip pulp from the Himalayas.",
                description="Cold-processed rosehip pulp made from handpicked, ripe rosehips. A naturally rich source of vitamin C and plant compounds.",
                price=499, mrp=699, stock=100, weight="500 ml",
                image="/static/assets/products/rosehip-pulp.jpg",
                benefits="Rich in Vitamin C | Antioxidants | Supports everyday wellness | No added sugar",
                usage="Shake well. Take 2 tablespoons (30 ml) in 200 ml water. Refrigerate after opening.",
                nutrition="Approx. per 100 ml: Energy 46 kcal; Vitamin C 400 mg; Calcium 30 mg; Potassium 250 mg.",
                featured=True
            ),
            Product(
                name="Rosehip Dry Berries",
                slug="rosehip-dry-berries",
                short_description="Naturally sun-dried rosehip berries, rich in vitamin C and antioxidants.",
                description="Handpicked rosehips from the Himalayan region, naturally sun-dried to preserve their important nutrients, vibrant flavor and goodness.",
                price=349, mrp=499, stock=150, weight="200 g",
                image="/static/assets/products/rosehip-dry-berries.jpg",
                benefits="Rich in Vitamin C | Antioxidant-rich fruit | Dietary fibre | No additives or preservatives",
                usage="Use 1–2 teaspoons (5–10 g) daily. Brew as tea, add to smoothies or oatmeal, or use in baking.",
                nutrition="Approx. per 100 g: Energy 260 kcal; Vitamin C 425 mg; Fibre 20 g; Potassium 1100 mg.",
                featured=True
            ),
            Product(
                name="Rosehip Dry Berry Powder",
                slug="rosehip-dry-berry-powder",
                short_description="Versatile rosehip berry powder, rich in vitamin C and plant polyphenols.",
                description="Fine powder made from carefully dried rosehip fruits. Suitable for smoothies, yoghurt, oats, juices and culinary preparations.",
                price=299, mrp=399, stock=200, weight="100 g",
                image="/static/assets/products/rosehip-powder.jpg",
                benefits="Rich in Vitamin C | Polyphenols | Flavonoids | Dietary fibre | Natural carotenoids",
                usage="Mix 1 teaspoon (3–5 g) daily into smoothies, yoghurt, oats, juices or other food preparations.",
                nutrition="Approx. per 100 g: Energy 220 kcal; Vitamin C 450 mg; Fibre 18 g; Potassium 800 mg.",
                featured=True
            )
        ]
        db.session.add_all(products)
    db.session.commit()

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_pages(path):
    full = os.path.join(app.static_folder, path)
    if os.path.isfile(full):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

@app.post("/api/auth/register")
def register():
    data = request.get_json() or {}
    name, email, password = data.get("name","").strip(), data.get("email","").strip().lower(), data.get("password","")
    if not name or not email or len(password) < 6:
        return jsonify({"message":"Name, valid email and password of at least 6 characters are required."}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"message":"Email already registered."}), 409
    user=User(name=name,email=email,role="customer",phone=data.get("phone",""),address=data.get("address",""))
    user.set_password(password)
    db.session.add(user); db.session.commit()
    token=create_access_token(identity=str(user.id))
    return jsonify({"token":token,"user":user.to_dict()})

@app.post("/api/auth/login")
def login():
    data=request.get_json() or {}
    user=User.query.filter_by(email=data.get("email","").strip().lower()).first()
    if not user or not user.check_password(data.get("password","")):
        return jsonify({"message":"Invalid email or password."}), 401
    token=create_access_token(identity=str(user.id))
    return jsonify({"token":token,"user":user.to_dict()})

@app.get("/api/auth/me")
@jwt_required()
def me():
    return jsonify({"user":current_user().to_dict()})

@app.put("/api/auth/me")
@jwt_required()
def update_me():
    user=current_user(); data=request.get_json() or {}
    user.name=data.get("name",user.name).strip()
    user.phone=data.get("phone",user.phone)
    user.address=data.get("address",user.address)
    db.session.commit()
    return jsonify({"user":user.to_dict()})

@app.get("/api/products")
def products():
    q=request.args.get("q","").strip()
    category=request.args.get("category","").strip()
    featured=request.args.get("featured")
    query=Product.query.filter_by(active=True)
    if q:
        query=query.filter(db.or_(Product.name.ilike(f"%{q}%"),Product.description.ilike(f"%{q}%")))
    if category:
        query=query.filter_by(category=category)
    if featured == "1":
        query=query.filter_by(featured=True)
    return jsonify({"products":[p.to_dict() for p in query.order_by(Product.id.desc()).all()]})

@app.get("/api/products/<int:pid>")
def product(pid):
    p=product_or_404(pid)
    return jsonify({"product":p.to_dict()})

@app.post("/api/orders")
@jwt_required()
def create_order():
    user=current_user(); data=request.get_json() or {}
    items=data.get("items",[])
    if not items: return jsonify({"message":"Cart is empty."}),400
    shipping_name=data.get("shipping_name",user.name).strip()
    shipping_phone=data.get("shipping_phone",user.phone or "").strip()
    shipping_address=data.get("shipping_address",user.address or "").strip()
    if not shipping_name or not shipping_phone or not shipping_address:
        return jsonify({"message":"Shipping name, phone and address are required."}),400

    subtotal=0
    normalized=[]
    for item in items:
        p=Product.query.get(int(item.get("product_id")))
        qty=int(item.get("quantity",0))
        if not p or not p.active: return jsonify({"message":"A product is unavailable."}),400
        if qty<1 or qty>p.stock: return jsonify({"message":f"Only {p.stock} units available for {p.name}."}),400
        subtotal += p.price*qty
        normalized.append((p,qty))

    shipping=0 if subtotal>=999 else 79
    discount=float(data.get("discount",0) or 0)
    total=max(0,subtotal+shipping-discount)
    method=data.get("payment_method","COD")
    if method not in ("COD","ONLINE"): method="COD"

    order=Order(
        order_number="MB-"+datetime.utcnow().strftime("%Y%m%d")+"-"+uuid.uuid4().hex[:6].upper(),
        user_id=user.id, subtotal=subtotal, shipping=shipping, discount=discount, total=total,
        payment_method=method, payment_status="Pending", order_status="Placed",
        shipping_name=shipping_name, shipping_phone=shipping_phone, shipping_address=shipping_address,
        notes=data.get("notes","")
    )
    db.session.add(order); db.session.flush()
    for p,qty in normalized:
        p.stock -= qty
        db.session.add(OrderItem(order_id=order.id,product_id=p.id,product_name=p.name,price=p.price,quantity=qty,image=p.image))
    db.session.commit()
    return jsonify({"order":order.to_dict()}),201

@app.get("/api/orders")
@jwt_required()
def my_orders():
    user=current_user()
    orders=Order.query.filter_by(user_id=user.id).order_by(Order.id.desc()).all()
    return jsonify({"orders":[o.to_dict() for o in orders]})

@app.get("/api/orders/<int:oid>")
@jwt_required()
def order_detail(oid):
    user=current_user(); o=Order.query.get_or_404(oid)
    if o.user_id != user.id and user.role!="admin": return jsonify({"message":"Forbidden"}),403
    return jsonify({"order":o.to_dict()})

@app.get("/api/orders/<int:oid>/invoice")
@jwt_required()
def invoice(oid):
    user=current_user(); o=Order.query.get_or_404(oid)
    if o.user_id != user.id and user.role!="admin": return jsonify({"message":"Forbidden"}),403
    buf=BytesIO()
    c=canvas.Canvas(buf,pagesize=A4)
    w,h=A4
    c.setFont("Helvetica-Bold",22); c.drawString(45,h-55,"THE MONKS BERRY")
    c.setFont("Helvetica",10); c.drawString(45,h-75,"Himalayan Goodness • Pure • Natural • Nutritious")
    c.setFont("Helvetica-Bold",14); c.drawString(45,h-115,"INVOICE")
    c.setFont("Helvetica",10)
    c.drawString(45,h-135,f"Order: {o.order_number}")
    c.drawString(45,h-150,f"Date: {o.created_at.strftime('%d %b %Y')}")
    c.drawString(45,h-165,f"Customer: {o.shipping_name}")
    c.drawString(45,h-180,f"Phone: {o.shipping_phone}")
    y=h-220
    c.setFont("Helvetica-Bold",10)
    c.drawString(45,y,"Product"); c.drawString(340,y,"Qty"); c.drawString(390,y,"Price"); c.drawString(470,y,"Amount")
    y-=18; c.setFont("Helvetica",10)
    for item in o.items:
        c.drawString(45,y,item.product_name[:45]); c.drawString(345,y,str(item.quantity))
        c.drawRightString(435,y,f"₹{item.price:.2f}")
        c.drawRightString(535,y,f"₹{item.price*item.quantity:.2f}"); y-=18
    y-=10
    c.line(340,y,535,y); y-=20
    c.drawRightString(535,y,f"Subtotal: ₹{o.subtotal:.2f}"); y-=16
    c.drawRightString(535,y,f"Shipping: ₹{o.shipping:.2f}"); y-=16
    c.drawRightString(535,y,f"Discount: ₹{o.discount:.2f}"); y-=20
    c.setFont("Helvetica-Bold",12); c.drawRightString(535,y,f"Total: ₹{o.total:.2f}")
    y-=40; c.setFont("Helvetica",9)
    c.drawString(45,y,"Thank you for choosing The Monks Berry.")
    c.drawString(45,y-15,"Product information is for general wellness information and does not replace medical advice.")
    c.save(); buf.seek(0)
    return send_file(buf,download_name=f"{o.order_number}.pdf",as_attachment=True,mimetype="application/pdf")

# Admin
def admin_required():
    u=current_user()
    if u.role!="admin": return jsonify({"message":"Admin access required."}),403
    return None

@app.get("/api/admin/stats")
@jwt_required()
def admin_stats():
    err=admin_required()
    if err:return err
    total_orders=Order.query.count()
    revenue=db.session.query(func.coalesce(func.sum(Order.total),0)).scalar()
    customers=User.query.filter_by(role="customer").count()
    products=Product.query.count()
    return jsonify({"total_orders":total_orders,"revenue":float(revenue or 0),"customers":customers,"products":products})

@app.get("/api/admin/orders")
@jwt_required()
def admin_orders():
    err=admin_required()
    if err:return err
    orders=Order.query.order_by(Order.id.desc()).all()
    return jsonify({"orders":[o.to_dict() for o in orders]})

@app.put("/api/admin/orders/<int:oid>")
@jwt_required()
def admin_update_order(oid):
    err=admin_required()
    if err:return err
    o=Order.query.get_or_404(oid); data=request.get_json() or {}
    if data.get("order_status"): o.order_status=data["order_status"]
    if data.get("payment_status"): o.payment_status=data["payment_status"]
    db.session.commit()
    return jsonify({"order":o.to_dict()})

@app.get("/api/admin/products")
@jwt_required()
def admin_products():
    err=admin_required()
    if err:return err
    return jsonify({"products":[p.to_dict() for p in Product.query.order_by(Product.id.desc()).all()]})

@app.post("/api/admin/products")
@jwt_required()
def admin_create_product():
    err=admin_required()
    if err:return err
    data=request.get_json() or {}
    required=["name","slug","price","mrp","stock"]
    if any(k not in data for k in required): return jsonify({"message":"Missing required fields."}),400
    if Product.query.filter_by(slug=data["slug"]).first(): return jsonify({"message":"Slug already exists."}),409
    p=Product(name=data["name"],slug=data["slug"],short_description=data.get("short_description",""),
              description=data.get("description",""),price=float(data["price"]),mrp=float(data["mrp"]),
              stock=int(data["stock"]),weight=data.get("weight",""),image=data.get("image",""),
              category=data.get("category","Rosehip"),benefits=data.get("benefits",""),
              usage=data.get("usage",""),nutrition=data.get("nutrition",""),
              featured=bool(data.get("featured",False)),active=bool(data.get("active",True)))
    db.session.add(p);db.session.commit()
    return jsonify({"product":p.to_dict()}),201

@app.put("/api/admin/products/<int:pid>")
@jwt_required()
def admin_update_product(pid):
    err=admin_required()
    if err:return err
    p=Product.query.get_or_404(pid); data=request.get_json() or {}
    for k in ["name","slug","short_description","description","weight","image","category","benefits","usage","nutrition"]:
        if k in data: setattr(p,k,data[k])
    for k in ["price","mrp"]:
        if k in data: setattr(p,k,float(data[k]))
    for k in ["stock"]:
        if k in data: setattr(p,k,int(data[k]))
    for k in ["featured","active"]:
        if k in data: setattr(p,k,bool(data[k]))
    db.session.commit()
    return jsonify({"product":p.to_dict()})

@app.delete("/api/admin/products/<int:pid>")
@jwt_required()
def admin_delete_product(pid):
    err=admin_required()
    if err:return err
    p=Product.query.get_or_404(pid); p.active=False; db.session.commit()
    return jsonify({"message":"Product disabled."})

@app.get("/api/admin/customers")
@jwt_required()
def admin_customers():
    err=admin_required()
    if err:return err
    users=User.query.filter_by(role="customer").order_by(User.id.desc()).all()
    return jsonify({"customers":[u.to_dict() for u in users]})

with app.app_context():
    db.create_all()
    seed_data()

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT","5000")),debug=True)
