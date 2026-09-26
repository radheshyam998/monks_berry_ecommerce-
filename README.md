# The Monks Berry — Product Sales Website

A complete full-stack e-commerce starter built from the uploaded Monks Berry product brochure.

## Stack
- Backend: Python + Flask + SQLAlchemy + JWT
- Database: SQLite by default; MySQL supported through `DATABASE_URL`
- Frontend: HTML5 + CSS3 + Vanilla JavaScript
- Reports: ReportLab PDF invoice
- Auth: JWT stored in localStorage
- Admin: product CRUD, order status, dashboard statistics
- Checkout: Cash on Delivery works out of the box; Razorpay can be enabled with API keys.

## Product content used from the brochure
- Rosehip Pulp — 100% Pure & Original
- Rosehip Dry Berries — 200g
- Rosehip Dry Berry Powder — 100g
- Brand positioning: pure, natural, nutritious; Himalayan origin.
- Nutrition/benefit copy is kept as product-information content, not a substitute for professional medical advice.

## Run locally

### 1. Backend
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env  # macOS/Linux

python app.py
```

Open: http://127.0.0.1:5000

Default admin:
- Email: admin@monksberry.local
- Password: Admin@12345

Change these values immediately in production.

### 2. MySQL
Create a database, then set:
`DATABASE_URL=mysql+pymysql://USER:PASSWORD@localhost:3306/monksberry`

Install:
`pip install pymysql`

### 3. Razorpay (optional)
Set:
- RAZORPAY_KEY_ID
- RAZORPAY_KEY_SECRET

Then choose Online Payment at checkout. Without keys, COD remains fully usable.

## Production checklist
- Change SECRET_KEY and admin password.
- Use MySQL/PostgreSQL.
- Put Flask behind Gunicorn/Nginx.
- Enable HTTPS.
- Set secure cookie/token strategy suitable for your deployment.
- Add your actual business address, GSTIN, shipping policy, return policy and payment credentials.
- Replace brochure-derived images if you have licensed production photography.
