import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
from flask_bcrypt import Bcrypt
from datetime import datetime
import uuid

def get_connection():
    return psycopg2.connect(
        os.getenv('DATABASE_URL'),
        cursor_factory=RealDictCursor
    )

@contextmanager
def get_cursor(commit=False):
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        if commit:
            conn.commit()
    finally:
        cur.close()
        conn.close()

# -------------------------
# Database Initialization
# -------------------------
def init_db():
    with get_cursor(commit=True) as cur:
        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                is_verified BOOLEAN DEFAULT FALSE,
                verification_token VARCHAR(255),
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Products table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name_fr VARCHAR(255) NOT NULL,
                name_ar VARCHAR(255),
                description_fr TEXT,
                description_ar TEXT,
                price DECIMAL(10,2) NOT NULL,
                image_url VARCHAR(500),
                category VARCHAR(100),
                stock INTEGER DEFAULT 0,
                options_sizes VARCHAR(500),
                options_colors VARCHAR(500),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Cart items
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cart_items (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                session_id VARCHAR(255),
                product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                quantity INTEGER DEFAULT 1,
                option_size VARCHAR(50),
                option_color VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Discounts
        cur.execute("""
            CREATE TABLE IF NOT EXISTS discounts (
                id SERIAL PRIMARY KEY,
                code VARCHAR(50) UNIQUE NOT NULL,
                percent_off DECIMAL(5,2) DEFAULT 0,
                amount_off DECIMAL(10,2) DEFAULT 0,
                min_purchase DECIMAL(10,2) DEFAULT 0,
                max_uses INTEGER,
                used_count INTEGER DEFAULT 0,
                valid_from TIMESTAMP,
                valid_until TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Orders
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                order_number VARCHAR(50) UNIQUE NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                total DECIMAL(10,2) NOT NULL,
                discount_amount DECIMAL(10,2) DEFAULT 0,
                baridi_phone VARCHAR(50),
                baridi_reference VARCHAR(255),
                shipping_address TEXT,
                email VARCHAR(255),
                full_name VARCHAR(255),
                telegram_notified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Order items
        cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                product_id INTEGER REFERENCES products(id),
                product_name_fr VARCHAR(255),
                product_name_ar VARCHAR(255),
                price DECIMAL(10,2) NOT NULL,
                quantity INTEGER NOT NULL,
                option_size VARCHAR(50),
                option_color VARCHAR(50)
            )
        """)

        # Ensure columns exist even if table existed
        for col, col_type in [('option_size','VARCHAR(50)'), ('option_color','VARCHAR(50)')]:
            cur.execute(f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='order_items' AND column_name='{col}'
                    ) THEN
                        ALTER TABLE order_items ADD COLUMN {col} {col_type};
                    END IF;
                END$$;
            """)

        # Admin settings
        cur.execute("""
            CREATE TABLE IF NOT EXISTS admin_settings (
                id SERIAL PRIMARY KEY,
                key VARCHAR(100) UNIQUE NOT NULL,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Drop old cart indexes if exist
        try:
            cur.execute("DROP INDEX IF EXISTS cart_user_product;")
            cur.execute("DROP INDEX IF EXISTS cart_session_product;")
        except Exception:
            pass

# -------------------------
# Seed admin
# -------------------------
def seed_admin():
    bcrypt = Bcrypt()
    pw_hash = bcrypt.generate_password_hash('123').decode('utf-8')
    with get_cursor(commit=True) as cur:
        cur.execute("SELECT id FROM users WHERE email = 'admin@admin.com'")
        if cur.fetchone():
            cur.execute(
                "UPDATE users SET password_hash = %s, is_admin = TRUE WHERE email = 'admin@admin.com'",
                (pw_hash,),
            )
        else:
            cur.execute(
                """INSERT INTO users (email, password_hash, full_name, is_verified, is_admin)
                   VALUES ('admin@admin.com', %s, 'Admin', TRUE, TRUE)""",
                (pw_hash,),
            )

# -------------------------
# Checkout function
# -------------------------
def checkout(user_id, shipping_address=None, email=None, full_name=None):
    with get_cursor(commit=True) as cur:
        # Get cart items
        cur.execute("SELECT * FROM cart_items WHERE user_id = %s", (user_id,))
        cart_items = cur.fetchall()
        if not cart_items:
            return {"error": "Cart is empty."}

        # Calculate total
        total = sum([float(item['price']) * item['quantity'] for item in cart_items])

        # Create order
        order_number = str(uuid.uuid4())
        cur.execute(
            """INSERT INTO orders (user_id, order_number, total, shipping_address, email, full_name)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
            (user_id, order_number, total, shipping_address, email, full_name)
        )
        order_id = cur.fetchone()['id']

        # Insert order items
        for item in cart_items:
            cur.execute("SELECT name_fr, name_ar, price FROM products WHERE id = %s", (item['product_id'],))
            prod = cur.fetchone()
            cur.execute(
                """INSERT INTO order_items
                   (order_id, product_id, product_name_fr, product_name_ar, price, quantity, option_size, option_color)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    order_id,
                    item['product_id'],
                    prod['name_fr'],
                    prod['name_ar'],
                    float(prod['price']),
                    item['quantity'],
                    item.get('option_size'),
                    item.get('option_color')
                )
            )

        # Clear cart
        cur.execute("DELETE FROM cart_items WHERE user_id = %s", (user_id,))

        return {"success": True, "order_id": order_id, "order_number": order_number, "total": total}

def seed_products():
    """Insert sample products with images and DZ prices if none exist."""
    with get_cursor(commit=False) as cur:
        cur.execute("SELECT COUNT(*) AS n FROM products")
        if cur.fetchone()['n'] > 0:
            return
    samples = [
        ('T-shirt Blanc Classique', 'تيشيرت أبيض كلاسيكي', 'T-shirt en coton confortable, coupe régulière.', 'تيشيرت قطني مريح، قصة عادية.', 2500, 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600', 'T-shirts', 50, 'S,M,L,XL', 'Blanc,Noir,Gris,Bleu marine'),
        ('Jean Slim Noir', 'جينز أسود سليم', 'Jean slim fit, idéal pour un look urbain.', 'جينز سليم، مثالي للمظهر الحضري.', 4500, 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600', 'Pantalons', 30, '32,34,36,38,40', 'Noir,Bleu,Bleu délavé'),
        ('Veste Denim', 'سترة دينيم', 'Veste en denim résistant, style casual.', 'سترة دينيم متينة، ستايل كاجوال.', 6500, 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600', 'Vestes', 20, 'S,M,L,XL', 'Bleu,Noir'),
        ('Robe d\'été Fleurie', 'فستان صيفي زهري', 'Robe légère à motifs floraux, parfaite pour l\'été.', 'فستان خفيف بزخارف زهرية، مثالي للصيف.', 3800, 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600', 'Robes', 25, 'S,M,L', 'Fleurie,Bleu,Rose'),
        ('Sweat à Capuche Gris', 'سويتر رمادي بقبعة', 'Sweat confortable en coton, capuche doublée.', 'سويتر مريح من القطن، قبعة مبطنة.', 3200, 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=600', 'Sweats', 40, 'S,M,L,XL', 'Gris,Noir,Bordeaux'),
        ('Chaussures Baskets Blanc', 'حذاء رياضي أبيض', 'Baskets polyvalentes, semelle confortable.', 'حذاء رياضي متعدد الاستخدامات، نعل مريح.', 5500, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600', 'Chaussures', 35, '39,40,41,42,43,44', 'Blanc,Noir,Gris'),
        ('Sac à Main Cuir', 'حقيبة يد جلدية', 'Sac en cuir synthétique, bandoulière réglable.', 'حقيبة من الجلد الصناعي، حزام كتف قابل للتعديل.', 4200, 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600', 'Accessoires', 15, 'Unique', 'Noir,Marron,Beige'),
        ('Polo Bleu Marine', 'بولو أزرق داكن', 'Polo en piqué, coupe moderne.', 'بولو من القطن المبرد، قصة عصرية.', 2800, 'https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=600', 'T-shirts', 45, 'S,M,L,XL', 'Bleu marine,Blanc,Rouge'),
        ('Short Cargo Beige', 'شورت كارجو بيج', 'Short cargo multi-poches, résistant.', 'شورت كارجو متعدد الجيوب، متين.', 2900, 'https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=600', 'Shorts', 30, 'S,M,L,XL', 'Beige,Kaki,Noir'),
    ]
    with get_cursor(commit=True) as cur:
        for row in samples:
            name_fr, name_ar, desc_fr, desc_ar, price, image_url, category, stock, sizes, colors = row
            cur.execute(
                """INSERT INTO products (name_fr, name_ar, description_fr, description_ar, price, image_url, category, stock, options_sizes, options_colors, is_active)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)""",
                (name_fr, name_ar, desc_fr, desc_ar, price, image_url, category, stock, sizes, colors),
            )
