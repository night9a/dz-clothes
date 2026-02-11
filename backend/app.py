import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from flask_bcrypt import Bcrypt
from db import get_cursor, init_db, seed_admin, seed_products
from auth import (
    register_user,
    verify_email_token,
    login_user,
    login_or_register_google,
    get_current_user_id,
    get_current_user_admin,
)
from mail_service import send_verification_email
from telegram_service import notify_new_order, get_admin_chat_id, send_telegram_notification

app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app, origins=os.getenv('FRONTEND_URL', 'https://dzclothes.netlify.app').split(','), supports_credentials=True)
JWTManager(app)
Bcrypt(app)

# ---------- Auth ----------
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''
    full_name = (data.get('full_name') or '').strip()
    lang = (data.get('lang') or 'fr')[:2]
    if not email or not password:
        return jsonify({'error': 'Email et mot de passe requis'}), 400
    user_id, err = register_user(email, password, full_name, lang)
    if err:
        return jsonify({'error': err}), 400
    return jsonify({'message': 'Inscription réussie. Vérifiez votre email.', 'user_id': user_id}), 201

@app.route('/api/auth/verify-email', methods=['POST'])
def verify_email():
    data = request.get_json() or {}
    token = (data.get('token') or '').strip()
    if not token:
        return jsonify({'error': 'Token manquant'}), 400
    if verify_email_token(token):
        return jsonify({'message': 'Email vérifié'})
    return jsonify({'error': 'Lien invalide ou expiré'}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''
    if not email or not password:
        return jsonify({'error': 'Email et mot de passe requis'}), 400
    result, err = login_user(email, password)
    if err:
        return jsonify({'error': err}), 401
    return jsonify(result)

@app.route('/api/auth/google', methods=['POST'])
def auth_google():
    data = request.get_json() or {}
    credential = (data.get('credential') or data.get('id_token') or '').strip()
    if not credential:
        return jsonify({'error': 'Token Google manquant'}), 400
    result, err = login_or_register_google(credential)
    if err:
        return jsonify({'error': err}), 401
    return jsonify(result)

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def me():
    identity = get_jwt_identity()
    return jsonify({'user': identity})

# ---------- Products (public) ----------
@app.route('/api/products', methods=['GET'])
def list_products():
    lang = request.args.get('lang', 'fr')
    category = request.args.get('category')
    with get_cursor(commit=False) as cur:
        cur.execute(
            """SELECT id, name_fr, name_ar, description_fr, description_ar, price, image_url, category, stock, options_sizes, options_colors
               FROM products WHERE is_active = TRUE ORDER BY created_at DESC"""
        )
        rows = cur.fetchall()
    name_key = 'name_fr' if lang == 'fr' else 'name_ar'
    desc_key = 'description_fr' if lang == 'fr' else 'description_ar'
    out = []
    for r in rows:
        if category and r['category'] != category:
            continue
        sizes = [x.strip() for x in (r.get('options_sizes') or '').split(',') if x.strip()]
        colors = [x.strip() for x in (r.get('options_colors') or '').split(',') if x.strip()]
        out.append({
            'id': r['id'],
            'name': r[name_key] or r['name_fr'],
            'description': (r[desc_key] or r['description_fr']) or '',
            'price': float(r['price']),
            'image_url': r['image_url'],
            'category': r['category'],
            'stock': r['stock'],
            'options_sizes': sizes,
            'options_colors': colors,
        })
    return jsonify(out)

@app.route('/api/products/<int:pid>', methods=['GET'])
def get_product(pid):
    lang = request.args.get('lang', 'fr')
    with get_cursor(commit=False) as cur:
        cur.execute(
            """SELECT id, name_fr, name_ar, description_fr, description_ar, price, image_url, category, stock, options_sizes, options_colors
               FROM products WHERE id = %s AND is_active = TRUE""",
            (pid,),
        )
        r = cur.fetchone()
    if not r:
        return jsonify({'error': 'Produit introuvable'}), 404
    name_key = 'name_fr' if lang == 'fr' else 'name_ar'
    desc_key = 'description_fr' if lang == 'fr' else 'description_ar'
    sizes = [x.strip() for x in (r.get('options_sizes') or '').split(',') if x.strip()]
    colors = [x.strip() for x in (r.get('options_colors') or '').split(',') if x.strip()]
    return jsonify({
        'id': r['id'],
        'name': r[name_key] or r['name_fr'],
        'description': (r[desc_key] or r['description_fr']) or '',
        'price': float(r['price']),
        'image_url': r['image_url'],
        'category': r['category'],
        'stock': r['stock'],
        'options_sizes': sizes,
        'options_colors': colors,
    })

# ---------- Cart ----------
def _cart_identifier():
    uid = get_current_user_id()
    if uid:
        return {'user_id': uid, 'session_id': None}
    sid = request.headers.get('X-Cart-Session') or request.cookies.get('cart_session') or request.json.get('cart_session') if request.is_json else None
    return {'user_id': None, 'session_id': sid}

@app.route('/api/cart', methods=['GET'])
def get_cart():
    ident = _cart_identifier()
    lang = request.args.get('lang', 'fr')
    with get_cursor(commit=False) as cur:
        if ident['user_id']:
            cur.execute(
                """SELECT c.id, c.product_id, c.quantity, c.option_size, c.option_color, p.name_fr, p.name_ar, p.price, p.image_url, p.stock
                   FROM cart_items c JOIN products p ON p.id = c.product_id
                   WHERE c.user_id = %s AND p.is_active = TRUE""",
                (ident['user_id'],),
            )
        elif ident['session_id']:
            cur.execute(
                """SELECT c.id, c.product_id, c.quantity, c.option_size, c.option_color, p.name_fr, p.name_ar, p.price, p.image_url, p.stock
                   FROM cart_items c JOIN products p ON p.id = c.product_id
                   WHERE c.session_id = %s AND p.is_active = TRUE""",
                (ident['session_id'],),
            )
        else:
            return jsonify([])
        rows = cur.fetchall()
    name_key = 'name_fr' if lang == 'fr' else 'name_ar'
    return jsonify([{
        'id': r['id'],
        'product_id': r['product_id'],
        'quantity': r['quantity'],
        'option_size': r.get('option_size'),
        'option_color': r.get('option_color'),
        'name': r[name_key] or r['name_fr'],
        'price': float(r['price']),
        'image_url': r['image_url'],
        'stock': r['stock'],
    } for r in rows])

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    quantity = max(1, int(data.get('quantity', 1)))
    option_size = (data.get('option_size') or '').strip() or None
    option_color = (data.get('option_color') or '').strip() or None
    ident = _cart_identifier()
    if not ident['user_id'] and not ident['session_id']:
        return jsonify({'error': 'Connexion ou session panier requise'}), 400
    if not product_id:
        return jsonify({'error': 'product_id requis'}), 400
    with get_cursor(commit=True) as cur:
        cur.execute("SELECT id, stock FROM products WHERE id = %s AND is_active = TRUE", (product_id,))
        p = cur.fetchone()
        if not p:
            return jsonify({'error': 'Produit introuvable'}), 404
        if ident['user_id']:
            cur.execute("""SELECT id, quantity FROM cart_items WHERE user_id = %s AND product_id = %s
                           AND COALESCE(option_size,'') = COALESCE(%s,'') AND COALESCE(option_color,'') = COALESCE(%s,'')""",
                        (ident['user_id'], product_id, option_size, option_color))
            existing = cur.fetchone()
            if existing:
                cur.execute("UPDATE cart_items SET quantity = quantity + %s WHERE id = %s", (quantity, existing['id']))
            else:
                cur.execute("INSERT INTO cart_items (user_id, product_id, quantity, option_size, option_color) VALUES (%s, %s, %s, %s, %s)",
                            (ident['user_id'], product_id, quantity, option_size, option_color))
        else:
            cur.execute("""SELECT id, quantity FROM cart_items WHERE session_id = %s AND product_id = %s
                           AND COALESCE(option_size,'') = COALESCE(%s,'') AND COALESCE(option_color,'') = COALESCE(%s,'')""",
                        (ident['session_id'], product_id, option_size, option_color))
            existing = cur.fetchone()
            if existing:
                cur.execute("UPDATE cart_items SET quantity = quantity + %s WHERE id = %s", (quantity, existing['id']))
            else:
                cur.execute("INSERT INTO cart_items (session_id, product_id, quantity, option_size, option_color) VALUES (%s, %s, %s, %s, %s)",
                            (ident['session_id'], product_id, quantity, option_size, option_color))
    return jsonify({'message': 'Ajouté au panier'})

@app.route('/api/cart/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    data = request.get_json() or {}
    quantity = data.get('quantity')
    if quantity is None:
        return jsonify({'error': 'quantity requis'}), 400
    quantity = max(0, int(quantity))
    ident = _cart_identifier()
    with get_cursor(commit=True) as cur:
        if ident['user_id']:
            cur.execute("UPDATE cart_items SET quantity = %s WHERE id = %s AND user_id = %s", (quantity, item_id, ident['user_id']))
        else:
            cur.execute("UPDATE cart_items SET quantity = %s WHERE id = %s AND session_id = %s", (quantity, item_id, ident['session_id']))
        if cur.rowcount == 0:
            return jsonify({'error': 'Article introuvable'}), 404
        if quantity == 0:
            cur.execute("DELETE FROM cart_items WHERE id = %s", (item_id,))
    return jsonify({'message': 'Panier mis à jour'})

@app.route('/api/cart/<int:item_id>', methods=['DELETE'])
def remove_cart_item(item_id):
    ident = _cart_identifier()
    with get_cursor(commit=True) as cur:
        if ident['user_id']:
            cur.execute("DELETE FROM cart_items WHERE id = %s AND user_id = %s", (item_id, ident['user_id']))
        else:
            cur.execute("DELETE FROM cart_items WHERE id = %s AND session_id = %s", (item_id, ident['session_id']))
        if cur.rowcount == 0:
            return jsonify({'error': 'Article introuvable'}), 404
    return jsonify({'message': 'Supprimé'})

# ---------- Discount ----------
@app.route('/api/discount/validate', methods=['POST'])
def validate_discount():
    data = request.get_json() or {}
    code = (data.get('code') or '').strip().upper()
    subtotal = float(data.get('subtotal', 0))
    if not code:
        return jsonify({'error': 'Code requis'}), 400
    with get_cursor(commit=False) as cur:
        cur.execute(
            """SELECT id, percent_off, amount_off, min_purchase, max_uses, used_count, valid_from, valid_until, is_active
               FROM discounts WHERE UPPER(code) = %s""",
            (code,),
        )
        d = cur.fetchone()
    if not d or not d['is_active']:
        return jsonify({'error': 'Code invalide'}), 400
    from datetime import datetime
    now = datetime.utcnow()
    if d['valid_from'] and d['valid_from'] > now:
        return jsonify({'error': 'Code pas encore valide'}), 400
    if d['valid_until'] and d['valid_until'] < now:
        return jsonify({'error': 'Code expiré'}), 400
    if d['max_uses'] is not None and (d['used_count'] or 0) >= d['max_uses']:
        return jsonify({'error': 'Code épuisé'}), 400
    if d['min_purchase'] and subtotal < float(d['min_purchase']):
        return jsonify({'error': f"Minimum d'achat: {d['min_purchase']} DA"}), 400
    amount = 0.0
    if d['percent_off']:
        amount = subtotal * float(d['percent_off']) / 100
    if d['amount_off']:
        amount = max(amount, float(d['amount_off']))
    amount = min(amount, subtotal)
    return jsonify({'valid': True, 'discount_amount': round(amount, 2), 'code': code})

# ---------- Checkout (Baridi Mob) ----------
@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.get_json() or {}
    baridi_phone = (data.get('baridi_phone') or '').strip()
    baridi_reference = (data.get('baridi_reference') or '').strip()
    shipping_address = (data.get('shipping_address') or '').strip()
    email = (data.get('email') or '').strip()
    full_name = (data.get('full_name') or '').strip()
    discount_code = (data.get('discount_code') or '').strip()
    ident = _cart_identifier()
    if not ident['user_id'] and not ident['session_id']:
        return jsonify({'error': 'Panier requis'}), 400
    if not email or not full_name or not shipping_address:
        return jsonify({'error': 'Email, nom et adresse requis'}), 400
    if not baridi_phone or not baridi_reference:
        return jsonify({'error': 'Numéro Baridi Mob et référence requis'}), 400

    with get_cursor(commit=False) as cur:
        if ident['user_id']:
            cur.execute(
                """SELECT c.id, c.product_id, c.quantity, c.option_size, c.option_color, p.name_fr, p.name_ar, p.price, p.stock
                   FROM cart_items c JOIN products p ON p.id = c.product_id WHERE c.user_id = %s""",
                (ident['user_id'],),
            )
        else:
            cur.execute(
                """SELECT c.id, c.product_id, c.quantity, c.option_size, c.option_color, p.name_fr, p.name_ar, p.price, p.stock
                   FROM cart_items c JOIN products p ON p.id = c.product_id WHERE c.session_id = %s""",
                (ident['session_id'],),
            )
        items = cur.fetchall()
    if not items:
        return jsonify({'error': 'Panier vide'}), 400
    subtotal = sum(float(r['price']) * r['quantity'] for r in items)
    discount_amount = 0.0
    if discount_code:
        with get_cursor(commit=False) as cur:
            cur.execute(
                """SELECT percent_off, amount_off, min_purchase, max_uses, used_count, is_active
                   FROM discounts WHERE UPPER(code) = %s""",
                (discount_code.upper(),),
            )
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
        cur.execute(
            """INSERT INTO orders (user_id, order_number, status, total, discount_amount, baridi_phone, baridi_reference, shipping_address, email, full_name)
               VALUES (%s, %s, 'pending', %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (ident['user_id'], order_number, total, discount_amount, baridi_phone, baridi_reference, shipping_address, email, full_name),
        )
        order_id = cur.fetchone()['id']
        for r in items:
            cur.execute(
                """INSERT INTO order_items (order_id, product_id, product_name_fr, product_name_ar, price, quantity, option_size, option_color)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (order_id, r['product_id'], r['name_fr'], r['name_ar'], r['price'], r['quantity'], r.get('option_size'), r.get('option_color')),
            )
        if discount_code and discount_amount > 0:
            cur.execute(
                "UPDATE discounts SET used_count = COALESCE(used_count, 0) + 1 WHERE UPPER(code) = %s",
                (discount_code.upper(),),
            )
        if ident['user_id']:
            cur.execute("DELETE FROM cart_items WHERE user_id = %s", (ident['user_id'],))
        else:
            cur.execute("DELETE FROM cart_items WHERE session_id = %s", (ident['session_id'],))
    items_summary = '\n'.join(f"- {r['name_fr']} x{r['quantity']} = {float(r['price'])*r['quantity']:.2f} DA" for r in items)
    notify_new_order(order_number, total, email, items_summary)
    with get_cursor(commit=True) as cur:
        cur.execute("UPDATE orders SET telegram_notified = TRUE WHERE id = %s", (order_id,))
    return jsonify({'order_number': order_number, 'total': total, 'message': 'Commande enregistrée'})

# ---------- Admin ----------
def admin_required(f):
    from functools import wraps
    @wraps(f)
    @jwt_required()
    def wrapped(*args, **kwargs):
        if not get_current_user_admin():
            return jsonify({'error': 'Non autorisé'}), 403
        return f(*args, **kwargs)
    return wrapped

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    with get_cursor(commit=False) as cur:
        cur.execute("SELECT COUNT(*) AS total FROM orders")
        total_orders = cur.fetchone()['total']
        cur.execute("SELECT COALESCE(SUM(total), 0) AS s FROM orders")
        total_sales = float(cur.fetchone()['s'])
        cur.execute("SELECT COUNT(*) AS total FROM products WHERE is_active = TRUE")
        total_products = cur.fetchone()['total']
        cur.execute("""SELECT DATE(created_at) AS d, COUNT(*) AS cnt, COALESCE(SUM(total), 0) AS total_day
                       FROM orders GROUP BY DATE(created_at) ORDER BY d DESC LIMIT 30""")
        sales_by_day = [{'date': str(r['d']), 'count': r['cnt'], 'total': float(r['total_day'])} for r in cur.fetchall()]
    return jsonify({
        'total_orders': total_orders,
        'total_sales': total_sales,
        'total_products': total_products,
        'sales_by_day': sales_by_day,
    })

@app.route('/api/admin/orders', methods=['GET'])
@admin_required
def admin_orders():
    with get_cursor(commit=False) as cur:
        cur.execute("""SELECT id, order_number, status, total, discount_amount, email, full_name, baridi_phone, baridi_reference, shipping_address, created_at
                       FROM orders ORDER BY created_at DESC""")
        orders = [dict(r) for r in cur.fetchall()]
    for o in orders:
        o['total'] = float(o['total'])
        o['discount_amount'] = float(o['discount_amount'] or 0)
        o['created_at'] = o['created_at'].isoformat() if o.get('created_at') else None
    return jsonify(orders)

@app.route('/api/admin/orders/<int:oid>', methods=['GET'])
@admin_required
def admin_order_detail(oid):
    with get_cursor(commit=False) as cur:
        cur.execute("""SELECT id, order_number, status, total, discount_amount, email, full_name, baridi_phone, baridi_reference, shipping_address, created_at
                       FROM orders WHERE id = %s""", (oid,))
        o = cur.fetchone()
        if not o:
            return jsonify({'error': 'Commande introuvable'}), 404
        cur.execute("SELECT product_id, product_name_fr, product_name_ar, price, quantity FROM order_items WHERE order_id = %s", (oid,))
        o['items'] = [dict(r) for r in cur.fetchall()]
    o['total'] = float(o['total'])
    o['discount_amount'] = float(o['discount_amount'] or 0)
    o['created_at'] = o['created_at'].isoformat() if o.get('created_at') else None
    return jsonify(o)

@app.route('/api/admin/orders/<int:oid>/status', methods=['PATCH'])
@admin_required
def admin_order_status(oid):
    data = request.get_json() or {}
    status = (data.get('status') or '').strip() or None
    if not status:
        return jsonify({'error': 'status requis'}), 400
    with get_cursor(commit=True) as cur:
        cur.execute("UPDATE orders SET status = %s WHERE id = %s RETURNING id", (status, oid))
        if cur.rowcount == 0:
            return jsonify({'error': 'Commande introuvable'}), 404
    return jsonify({'message': 'Statut mis à jour'})

@app.route('/api/admin/products', methods=['GET'])
@admin_required
def admin_products():
    with get_cursor(commit=False) as cur:
        cur.execute("""SELECT id, name_fr, name_ar, description_fr, description_ar, price, image_url, category, stock, options_sizes, options_colors, is_active, created_at
                       FROM products ORDER BY created_at DESC""")
        rows = cur.fetchall()
    return jsonify([{**r, 'price': float(r['price']), 'created_at': r['created_at'].isoformat() if r.get('created_at') else None} for r in rows])

@app.route('/api/admin/products', methods=['POST'])
@admin_required
def admin_create_product():
    data = request.get_json() or {}
    name_fr = (data.get('name_fr') or '').strip()
    if not name_fr:
        return jsonify({'error': 'name_fr requis'}), 400
    price = float(data.get('price', 0))
    with get_cursor(commit=True) as cur:
        cur.execute(
            """INSERT INTO products (name_fr, name_ar, description_fr, description_ar, price, image_url, category, stock, options_sizes, options_colors, is_active)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (
                name_fr,
                (data.get('name_ar') or '').strip(),
                (data.get('description_fr') or '').strip(),
                (data.get('description_ar') or '').strip(),
                price,
                (data.get('image_url') or '').strip(),
                (data.get('category') or '').strip(),
                int(data.get('stock', 0)),
                (data.get('options_sizes') or '').strip(),
                (data.get('options_colors') or '').strip(),
                data.get('is_active', True),
            ),
        )
        pid = cur.fetchone()['id']
    return jsonify({'id': pid, 'message': 'Produit créé'}), 201

@app.route('/api/admin/products/<int:pid>', methods=['PUT'])
@admin_required
def admin_update_product(pid):
    data = request.get_json() or {}
    with get_cursor(commit=True) as cur:
        cur.execute(
            """UPDATE products SET name_fr = COALESCE(NULLIF(%s, ''), name_fr), name_ar = COALESCE(NULLIF(%s, ''), name_ar),
               description_fr = COALESCE(NULLIF(%s, ''), description_fr), description_ar = COALESCE(NULLIF(%s, ''), description_ar),
               price = COALESCE(NULLIF(%s::decimal, 0), price), image_url = COALESCE(NULLIF(%s, ''), image_url),
               category = COALESCE(NULLIF(%s, ''), category), stock = COALESCE(%s, stock),
               options_sizes = COALESCE(%s, options_sizes), options_colors = COALESCE(%s, options_colors),
               is_active = COALESCE(%s, is_active)
               WHERE id = %s RETURNING id""",
            (
                (data.get('name_fr') or '').strip(),
                (data.get('name_ar') or '').strip(),
                (data.get('description_fr') or '').strip(),
                (data.get('description_ar') or '').strip(),
                data.get('price'),
                (data.get('image_url') or '').strip(),
                (data.get('category') or '').strip(),
                data.get('stock'),
                (data.get('options_sizes') or '').strip() or None,
                (data.get('options_colors') or '').strip() or None,
                data.get('is_active'),
                pid,
            ),
        )
        if cur.rowcount == 0:
            return jsonify({'error': 'Produit introuvable'}), 404
    return jsonify({'message': 'Produit mis à jour'})

@app.route('/api/admin/products/<int:pid>', methods=['DELETE'])
@admin_required
def admin_delete_product(pid):
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM products WHERE id = %s RETURNING id", (pid,))
        if cur.rowcount == 0:
            return jsonify({'error': 'Produit introuvable'}), 404
    return jsonify({'message': 'Produit supprimé'})

@app.route('/api/admin/discounts', methods=['GET'])
@admin_required
def admin_discounts():
    with get_cursor(commit=False) as cur:
        cur.execute("""SELECT id, code, percent_off, amount_off, min_purchase, max_uses, used_count, valid_from, valid_until, is_active, created_at
                       FROM discounts ORDER BY created_at DESC""")
        rows = cur.fetchall()
    return jsonify([{**r, 'percent_off': float(r['percent_off'] or 0), 'amount_off': float(r['amount_off'] or 0),
                    'min_purchase': float(r['min_purchase'] or 0), 'created_at': r['created_at'].isoformat() if r.get('created_at') else None} for r in rows])

@app.route('/api/admin/discounts', methods=['POST'])
@admin_required
def admin_create_discount():
    data = request.get_json() or {}
    code = (data.get('code') or '').strip().upper()
    if not code:
        return jsonify({'error': 'code requis'}), 400
    with get_cursor(commit=True) as cur:
        cur.execute(
            """INSERT INTO discounts (code, percent_off, amount_off, min_purchase, max_uses, valid_from, valid_until, is_active)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (
                code,
                float(data.get('percent_off', 0)),
                float(data.get('amount_off', 0)),
                float(data.get('min_purchase', 0)),
                data.get('max_uses'),
                data.get('valid_from'),
                data.get('valid_until'),
                data.get('is_active', True),
            ),
        )
        did = cur.fetchone()['id']
    return jsonify({'id': did, 'message': 'Réduction créée'}), 201

@app.route('/api/admin/discounts/<int:did>', methods=['PUT'])
@admin_required
def admin_update_discount(did):
    data = request.get_json() or {}
    with get_cursor(commit=True) as cur:
        cur.execute(
            """UPDATE discounts SET code = COALESCE(NULLIF(UPPER(%s), ''), code), percent_off = COALESCE(%s, percent_off),
               amount_off = COALESCE(%s, amount_off), min_purchase = COALESCE(%s, min_purchase), max_uses = %s,
               valid_from = %s, valid_until = %s, is_active = COALESCE(%s, is_active) WHERE id = %s RETURNING id""",
            (
                (data.get('code') or '').strip(),
                data.get('percent_off'),
                data.get('amount_off'),
                data.get('min_purchase'),
                data.get('max_uses'),
                data.get('valid_from'),
                data.get('valid_until'),
                data.get('is_active'),
                did,
            ),
        )
        if cur.rowcount == 0:
            return jsonify({'error': 'Réduction introuvable'}), 404
    return jsonify({'message': 'Réduction mise à jour'})

@app.route('/api/admin/discounts/<int:did>', methods=['DELETE'])
@admin_required
def admin_delete_discount(did):
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM discounts WHERE id = %s RETURNING id", (did,))
        if cur.rowcount == 0:
            return jsonify({'error': 'Réduction introuvable'}), 404
    return jsonify({'message': 'Réduction supprimée'})

@app.route('/api/admin/settings/telegram', methods=['GET'])
@admin_required
def admin_telegram_get():
    chat_id = get_admin_chat_id()
    return jsonify({'telegram_chat_id': chat_id, 'enabled': bool(chat_id)})

@app.route('/api/admin/settings/telegram', methods=['POST'])
@admin_required
def admin_telegram_set():
    data = request.get_json() or {}
    chat_id = (data.get('telegram_chat_id') or '').strip()
    with get_cursor(commit=True) as cur:
        cur.execute("""INSERT INTO admin_settings (key, value, updated_at) VALUES ('telegram_chat_id', %s, CURRENT_TIMESTAMP)
                       ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP""", (chat_id or None,))
    send_telegram_notification("✅ Notifications DZ Clothes activées. Vous recevrez les nouvelles commandes ici.")
    return jsonify({'message': 'Telegram configuré'})

# ---------- Init & run ----------
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

with app.app_context():
    init_db()
    seed_admin()
    seed_products()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
