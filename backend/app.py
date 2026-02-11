import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from functools import wraps
from db import get_cursor, init_db, seed_admin, seed_products
from auth import (
    register_user,
    verify_email_token,
    login_user,
    login_or_register_google,
)
from mail_service import send_verification_email
from telegram_service import notify_new_order, send_telegram_notification

app = Flask(__name__)
app.config.from_object('config.Config')
app.secret_key = os.getenv('JWT_SECRET_KEY', 'dev-secret-dz-clothes')
CORS(app, origins=os.getenv('FRONTEND_URL', 'http://localhost:5000').split(','), supports_credentials=True)
JWTManager(app)
Bcrypt(app)

# Helper to check if user is logged in
def login_required_web(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter', 'error')
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required_web(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Accès non autorisé', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# ---------- Frontend Routes ----------
@app.route('/')
def home():
    lang = session.get('lang', 'fr')
    with get_cursor(commit=False) as cur:
        cur.execute("""SELECT id, name_fr, name_ar, description_fr, description_ar, price, image_url, category, stock
                       FROM products WHERE is_active = TRUE ORDER BY created_at DESC LIMIT 6""")
        products = cur.fetchall()
    return render_template('home.html', products=products, lang=lang, user=session.get('user'))

@app.route('/shop')
def shop():
    lang = session.get('lang', 'fr')
    category = request.args.get('category', '')
    with get_cursor(commit=False) as cur:
        if category:
            cur.execute("""SELECT id, name_fr, name_ar, description_fr, description_ar, price, image_url, category, stock
                           FROM products WHERE is_active = TRUE AND category = %s ORDER BY created_at DESC""", (category,))
        else:
            cur.execute("""SELECT id, name_fr, name_ar, description_fr, description_ar, price, image_url, category, stock
                           FROM products WHERE is_active = TRUE ORDER BY created_at DESC""")
        products = cur.fetchall()
        
        # Get unique categories
        cur.execute("SELECT DISTINCT category FROM products WHERE is_active = TRUE AND category IS NOT NULL")
        categories = [row['category'] for row in cur.fetchall()]
    
    return render_template('shop.html', products=products, categories=categories, selected_category=category, lang=lang, user=session.get('user'))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    lang = session.get('lang', 'fr')
    with get_cursor(commit=False) as cur:
        cur.execute("""SELECT id, name_fr, name_ar, description_fr, description_ar, price, image_url, category, stock, options_sizes, options_colors
                       FROM products WHERE id = %s AND is_active = TRUE""", (product_id,))
        product = cur.fetchone()
    
    if not product:
        flash('Produit introuvable', 'error')
        return redirect(url_for('shop'))
    
    sizes = [x.strip() for x in (product.get('options_sizes') or '').split(',') if x.strip()]
    colors = [x.strip() for x in (product.get('options_colors') or '').split(',') if x.strip()]
    
    return render_template('product.html', product=product, sizes=sizes, colors=colors, lang=lang, user=session.get('user'))

@app.route('/cart')
def cart_page():
    lang = session.get('lang', 'fr')
    cart_session = session.get('cart_session')
    user_id = session.get('user_id')
    
    items = []
    total = 0
    
    with get_cursor(commit=False) as cur:
        if user_id:
            cur.execute("""SELECT c.id, c.product_id, c.quantity, c.option_size, c.option_color, 
                           p.name_fr, p.name_ar, p.price, p.image_url, p.stock
                           FROM cart_items c JOIN products p ON p.id = c.product_id
                           WHERE c.user_id = %s AND p.is_active = TRUE""", (user_id,))
        elif cart_session:
            cur.execute("""SELECT c.id, c.product_id, c.quantity, c.option_size, c.option_color,
                           p.name_fr, p.name_ar, p.price, p.image_url, p.stock
                           FROM cart_items c JOIN products p ON p.id = c.product_id
                           WHERE c.session_id = %s AND p.is_active = TRUE""", (cart_session,))
        
        if user_id or cart_session:
            items = cur.fetchall()
            total = sum(float(item['price']) * item['quantity'] for item in items)
    
    return render_template('cart.html', items=items, total=total, lang=lang, user=session.get('user'))

@app.route('/checkout')
@login_required_web
def checkout_page():
    lang = session.get('lang', 'fr')
    user_id = session.get('user_id')
    
    with get_cursor(commit=False) as cur:
        cur.execute("""SELECT c.id, c.product_id, c.quantity, c.option_size, c.option_color,
                       p.name_fr, p.name_ar, p.price
                       FROM cart_items c JOIN products p ON p.id = c.product_id
                       WHERE c.user_id = %s""", (user_id,))
        items = cur.fetchall()
    
    if not items:
        flash('Votre panier est vide', 'error')
        return redirect(url_for('shop'))
    
    subtotal = sum(float(item['price']) * item['quantity'] for item in items)
    
    return render_template('checkout.html', items=items, subtotal=subtotal, lang=lang, user=session.get('user'))

@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('login.html', lang=session.get('lang', 'fr'))

@app.route('/register')
def register_page():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('register.html', lang=session.get('lang', 'fr'))

@app.route('/verify-email')
def verify_email_page():
    token = request.args.get('token', '')
    return render_template('verify_email.html', token=token, lang=session.get('lang', 'fr'))

@app.route('/admin')
@admin_required_web
def admin_dashboard():
    return render_template('admin/dashboard.html', lang=session.get('lang', 'fr'), user=session.get('user'))

@app.route('/admin/orders')
@admin_required_web
def admin_orders():
    return render_template('admin/orders.html', lang=session.get('lang', 'fr'), user=session.get('user'))

@app.route('/admin/products')
@admin_required_web
def admin_products():
    return render_template('admin/products.html', lang=session.get('lang', 'fr'), user=session.get('user'))

@app.route('/admin/discounts')
@admin_required_web
def admin_discounts():
    return render_template('admin/discounts.html', lang=session.get('lang', 'fr'), user=session.get('user'))

@app.route('/admin/settings')
@admin_required_web
def admin_settings():
    return render_template('admin/settings.html', lang=session.get('lang', 'fr'), user=session.get('user'))

# ---------- Auth Actions ----------
@app.route('/action/register', methods=['POST'])
def action_register():
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    full_name = request.form.get('full_name', '').strip()
    lang = session.get('lang', 'fr')
    
    if not email or not password:
        flash('Email et mot de passe requis', 'error')
        return redirect(url_for('register_page'))
    
    user_id, err = register_user(email, password, full_name, lang)
    if err:
        flash(err, 'error')
        return redirect(url_for('register_page'))
    
    flash('Inscription réussie! Vérifiez votre email.', 'success')
    return redirect(url_for('login_page'))

@app.route('/action/login', methods=['POST'])
def action_login():
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    
    if not email or not password:
        flash('Email et mot de passe requis', 'error')
        return redirect(url_for('login_page'))
    
    result, err = login_user(email, password)
    if err:
        flash(err, 'error')
        return redirect(url_for('login_page'))
    
    # Store in session
    session['user_id'] = result['user']['id']
    session['user_email'] = result['user']['email']
    session['is_admin'] = result['user']['is_admin']
    session['user'] = result['user']
    
    flash('Connexion réussie!', 'success')
    redirect_to = request.args.get('redirect', '/')
    return redirect(redirect_to)

@app.route('/action/logout')
def action_logout():
    session.clear()
    flash('Déconnexion réussie', 'success')
    return redirect(url_for('home'))

@app.route('/action/verify-email', methods=['POST'])
def action_verify_email():
    token = request.form.get('token', '').strip()
    if not token:
        flash('Token manquant', 'error')
        return redirect(url_for('verify_email_page'))
    
    if verify_email_token(token):
        flash('Email vérifié! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login_page'))
    
    flash('Lien invalide ou expiré', 'error')
    return redirect(url_for('register_page'))

# ---------- Cart Actions ----------
@app.route('/action/add-to-cart', methods=['POST'])
def action_add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    option_size = request.form.get('option_size', '').strip() or None
    option_color = request.form.get('option_color', '').strip() or None
    
    user_id = session.get('user_id')
    cart_session = session.get('cart_session')
    
    if not cart_session and not user_id:
        import uuid
        cart_session = 's_' + str(uuid.uuid4())
        session['cart_session'] = cart_session
    
    with get_cursor(commit=True) as cur:
        if user_id:
            cur.execute("""SELECT id, quantity FROM cart_items WHERE user_id = %s AND product_id = %s
                           AND COALESCE(option_size,'') = COALESCE(%s,'') AND COALESCE(option_color,'') = COALESCE(%s,'')""",
                        (user_id, product_id, option_size, option_color))
            existing = cur.fetchone()
            if existing:
                cur.execute("UPDATE cart_items SET quantity = quantity + %s WHERE id = %s", (quantity, existing['id']))
            else:
                cur.execute("INSERT INTO cart_items (user_id, product_id, quantity, option_size, option_color) VALUES (%s, %s, %s, %s, %s)",
                            (user_id, product_id, quantity, option_size, option_color))
        else:
            cur.execute("""SELECT id, quantity FROM cart_items WHERE session_id = %s AND product_id = %s
                           AND COALESCE(option_size,'') = COALESCE(%s,'') AND COALESCE(option_color,'') = COALESCE(%s,'')""",
                        (cart_session, product_id, option_size, option_color))
            existing = cur.fetchone()
            if existing:
                cur.execute("UPDATE cart_items SET quantity = quantity + %s WHERE id = %s", (quantity, existing['id']))
            else:
                cur.execute("INSERT INTO cart_items (session_id, product_id, quantity, option_size, option_color) VALUES (%s, %s, %s, %s, %s)",
                            (cart_session, product_id, quantity, option_size, option_color))
    
    flash('Produit ajouté au panier!', 'success')
    return redirect(request.referrer or url_for('shop'))

@app.route('/action/update-cart/<int:item_id>', methods=['POST'])
def action_update_cart(item_id):
    quantity = int(request.form.get('quantity', 1))
    user_id = session.get('user_id')
    cart_session = session.get('cart_session')
    
    with get_cursor(commit=True) as cur:
        if user_id:
            if quantity > 0:
                cur.execute("UPDATE cart_items SET quantity = %s WHERE id = %s AND user_id = %s", (quantity, item_id, user_id))
            else:
                cur.execute("DELETE FROM cart_items WHERE id = %s AND user_id = %s", (item_id, user_id))
        else:
            if quantity > 0:
                cur.execute("UPDATE cart_items SET quantity = %s WHERE id = %s AND session_id = %s", (quantity, item_id, cart_session))
            else:
                cur.execute("DELETE FROM cart_items WHERE id = %s AND session_id = %s", (item_id, cart_session))
    
    flash('Panier mis à jour', 'success')
    return redirect(url_for('cart_page'))

@app.route('/action/remove-cart/<int:item_id>', methods=['POST'])
def action_remove_cart(item_id):
    user_id = session.get('user_id')
    cart_session = session.get('cart_session')
    
    with get_cursor(commit=True) as cur:
        if user_id:
            cur.execute("DELETE FROM cart_items WHERE id = %s AND user_id = %s", (item_id, user_id))
        else:
            cur.execute("DELETE FROM cart_items WHERE id = %s AND session_id = %s", (item_id, cart_session))
    
    flash('Article supprimé', 'success')
    return redirect(url_for('cart_page'))

# ---------- Checkout Action ----------
@app.route('/action/checkout', methods=['POST'])
@login_required_web
def action_checkout():
    user_id = session.get('user_id')
    baridi_phone = request.form.get('baridi_phone', '').strip()
    baridi_reference = request.form.get('baridi_reference', '').strip()
    shipping_address = request.form.get('shipping_address', '').strip()
    email = request.form.get('email', '').strip()
    full_name = request.form.get('full_name', '').strip()
    discount_code = request.form.get('discount_code', '').strip()
    
    if not email or not full_name or not shipping_address or not baridi_phone or not baridi_reference:
        flash('Tous les champs sont requis', 'error')
        return redirect(url_for('checkout_page'))
    
    with get_cursor(commit=False) as cur:
        cur.execute("""SELECT c.id, c.product_id, c.quantity, c.option_size, c.option_color, p.name_fr, p.name_ar, p.price, p.stock
                       FROM cart_items c JOIN products p ON p.id = c.product_id WHERE c.user_id = %s""", (user_id,))
        items = cur.fetchall()
    
    if not items:
        flash('Panier vide', 'error')
        return redirect(url_for('shop'))
    
    subtotal = sum(float(r['price']) * r['quantity'] for r in items)
    discount_amount = 0.0
    
    if discount_code:
        with get_cursor(commit=False) as cur:
            cur.execute("""SELECT percent_off, amount_off, min_purchase, max_uses, used_count, is_active
                           FROM discounts WHERE UPPER(code) = %s""", (discount_code.upper(),))
            d = cur.fetchone()
        if d and d['is_active'] and subtotal >= float(d['min_purchase'] or 0):
            if d['max_uses'] is None or (d['used_count'] or 0) < d['max_uses']:
                if d['percent_off']:
                    discount_amount = subtotal * float(d['percent_off']) / 100
                if d['amount_off']:
                    discount_amount = max(discount_amount, float(d['amount_off']))
                discount_amount = min(discount_amount, subtotal)
    
    total = round(subtotal - discount_amount, 2)
    order_number = f"DZ-{os.urandom(4).hex().upper()}"
    
    with get_cursor(commit=True) as cur:
        cur.execute("""INSERT INTO orders (user_id, order_number, status, total, discount_amount, baridi_phone, baridi_reference, shipping_address, email, full_name)
                       VALUES (%s, %s, 'pending', %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                    (user_id, order_number, total, discount_amount, baridi_phone, baridi_reference, shipping_address, email, full_name))
        order_id = cur.fetchone()['id']
        
        for r in items:
            cur.execute("""INSERT INTO order_items (order_id, product_id, product_name_fr, product_name_ar, price, quantity, option_size, option_color)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                        (order_id, r['product_id'], r['name_fr'], r['name_ar'], r['price'], r['quantity'], r.get('option_size'), r.get('option_color')))
        
        if discount_code and discount_amount > 0:
            cur.execute("UPDATE discounts SET used_count = COALESCE(used_count, 0) + 1 WHERE UPPER(code) = %s", (discount_code.upper(),))
        
        cur.execute("DELETE FROM cart_items WHERE user_id = %s", (user_id,))
    
    items_summary = '\n'.join(f"- {r['name_fr']} x{r['quantity']} = {float(r['price'])*r['quantity']:.2f} DA" for r in items)
    notify_new_order(order_number, total, email, items_summary)
    
    flash(f'Commande enregistrée! Numéro: {order_number}', 'success')
    return redirect(url_for('home'))

# ---------- Language Switch ----------
@app.route('/action/set-lang/<lang>')
def action_set_lang(lang):
    session['lang'] = lang if lang in ['fr', 'ar'] else 'fr'
    return redirect(request.referrer or url_for('home'))

# ---------- API Routes (for compatibility) ----------
# Keep all your existing API routes here
# ... (copy all API routes from original app.py)

# ---------- Init & run ----------
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

with app.app_context():
    init_db()
    seed_admin()
    seed_products()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
