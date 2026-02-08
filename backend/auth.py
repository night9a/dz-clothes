import uuid
import requests
from flask import request
from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
from flask_bcrypt import Bcrypt
from db import get_cursor
from mail_service import send_verification_email
from config import Config

bcrypt = Bcrypt()

def verify_google_token(id_token: str):
    """Verify Google id_token and return payload with email, name or None."""
    try:
        r = requests.get(
            'https://oauth2.googleapis.com/tokeninfo',
            params={'id_token': id_token},
            timeout=10,
        )
        if r.status_code != 200:
            return None
        data = r.json()
        if data.get('aud') != Config.GOOGLE_CLIENT_ID:
            return None
        return {
            'email': (data.get('email') or '').lower(),
            'name': data.get('name') or (f"{data.get('given_name', '')} {data.get('family_name', '')}").strip() or data.get('email', ''),
        }
    except Exception:
        return None

def register_user(email: str, password: str, full_name: str = None, lang: str = 'fr'):
    with get_cursor(commit=True) as cur:
        cur.execute("SELECT id FROM users WHERE email = %s", (email.lower(),))
        if cur.fetchone():
            return None, 'Email déjà utilisé'
        token = str(uuid.uuid4())
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        cur.execute("SELECT COUNT(*) AS n FROM users")
        is_first = cur.fetchone()['n'] == 0
        cur.execute(
            """INSERT INTO users (email, password_hash, full_name, verification_token, is_verified, is_admin)
               VALUES (%s, %s, %s, %s, FALSE, %s) RETURNING id""",
            (email.lower(), pw_hash, full_name, token, is_first),
        )
        row = cur.fetchone()
        user_id = row['id']
    link = f"{Config.FRONTEND_URL}{Config.VERIFY_EMAIL_URL_PATH}?token={token}"
    send_verification_email(email, link, lang)
    return user_id, None

def verify_email_token(token: str):
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE users SET is_verified = TRUE, verification_token = NULL WHERE verification_token = %s RETURNING id",
            (token,),
        )
        return cur.fetchone() is not None

def login_user(email: str, password: str):
    with get_cursor(commit=False) as cur:
        cur.execute(
            "SELECT id, password_hash, is_verified, is_admin FROM users WHERE email = %s",
            (email.lower(),),
        )
        row = cur.fetchone()
    if not row or not bcrypt.check_password_hash(row['password_hash'], password):
        return None, 'Email ou mot de passe incorrect'
    if not row['is_verified']:
        return None, 'Veuillez vérifier votre email avant de vous connecter'
    identity = {'id': row['id'], 'email': email.lower(), 'is_admin': row['is_admin']}
    token = create_access_token(identity=identity)
    return {'access_token': token, 'user': {'id': row['id'], 'email': email.lower(), 'is_admin': row['is_admin']}}, None

def get_current_user_id():
    try:
        verify_jwt_in_request()
        return get_jwt_identity().get('id')
    except Exception:
        return None

def get_current_user_admin():
    try:
        verify_jwt_in_request()
        return get_jwt_identity().get('is_admin') is True
    except Exception:
        return False


def login_or_register_google(id_token: str):
    """Verify Google token, find or create user, return (result_dict, error)."""
    payload = verify_google_token(id_token)
    if not payload or not payload.get('email'):
        return None, 'Token Google invalide'
    email = payload['email']
    full_name = (payload.get('name') or '').strip() or email
    with get_cursor(commit=True) as cur:
        cur.execute(
            "SELECT id, is_admin FROM users WHERE email = %s",
            (email,),
        )
        row = cur.fetchone()
        if row:
            user_id, is_admin = row['id'], row['is_admin']
        else:
            pw_hash = bcrypt.generate_password_hash(uuid.uuid4().hex).decode('utf-8')
            cur.execute(
                """INSERT INTO users (email, password_hash, full_name, is_verified, is_admin)
                   VALUES (%s, %s, %s, TRUE, FALSE) RETURNING id""",
                (email, pw_hash, full_name),
            )
            user_id = cur.fetchone()['id']
            is_admin = False
    identity = {'id': user_id, 'email': email, 'is_admin': is_admin}
    token = create_access_token(identity=identity)
    return {'access_token': token, 'user': {'id': user_id, 'email': email, 'is_admin': is_admin}}, None
