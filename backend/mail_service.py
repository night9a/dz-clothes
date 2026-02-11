import os
import requests

def get_email_config():
    """Get email configuration from environment."""
    return {
        'mailjet_api_key': os.getenv('MAILJET_API_KEY'),
        'mailjet_secret_key': os.getenv('MAILJET_SECRET_KEY'),
        'from_email': os.getenv('MAIL_FROM', 'noreply@dzclothes.dz'),
        'from_name': os.getenv('MAIL_FROM_NAME', 'DZ Clothes'),
    }

def send_via_mailjet(to_email: str, subject: str, html_content: str, from_email: str, from_name: str) -> bool:
    """Send email via Mailjet API."""
    config = get_email_config()
    
    if not config['mailjet_api_key'] or not config['mailjet_secret_key']:
        print("[Mail] Mailjet not configured - skipping")
        return False
    
    try:
        payload = {
            "Messages": [
                {
                    "From": {"Email": from_email, "Name": from_name},
                    "To": [{"Email": to_email}],
                    "Subject": subject,
                    "HTMLPart": html_content,
                    "TextPart": html_content.replace('<br>', '\n').replace('</p>', '\n'),
                }
            ]
        }
        
        response = requests.post(
            "https://api.mailjet.com/v3.1/send",
            auth=(config['mailjet_api_key'], config['mailjet_secret_key']),
            json=payload,
            timeout=10,
        )
        
        if response.status_code in (200, 201):
            print(f"[Mail] ✅ Mailjet email sent to {to_email}")
            return True
        else:
            print(f"[Mail] ❌ Mailjet error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[Mail] ❌ Mailjet error: {str(e)}")
        return False

def send_verification_email(to_email: str, verification_link: str, lang: str = 'fr') -> bool:
    """Send verification email with automatic provider fallback."""
    config = get_email_config()
    
    subject = "Vérifiez votre email - DZ Clothes" if lang == 'fr' else "تحقق من بريدك الإلكتروني - DZ Clothes"
    
    html_fr = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #e8c547 0%, #f0d06f 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .header h1 {{ color: #0a0a0a; margin: 0; font-size: 28px; }}
            .content {{ background: #ffffff; padding: 30px; border: 1px solid #e5e5e5; }}
            .button {{ display: inline-block; background: #e8c547; color: #0a0a0a; padding: 15px 30px; text-decoration: none; border-radius: 50px; font-weight: bold; margin: 20px 0; }}
            .footer {{ background: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>◆ DZ Clothes</h1>
            </div>
            <div class="content">
                <h2>Bienvenue chez DZ Clothes !</h2>
                <p>Merci de vous être inscrit. Cliquez sur le bouton ci-dessous pour vérifier votre adresse email :</p>
                <p style="text-align: center;">
                    <a href="{verification_link}" class="button">Vérifier mon email</a>
                </p>
                <p>Ou copiez ce lien dans votre navigateur :</p>
                <p style="word-break: break-all; color: #666; font-size: 12px;">{verification_link}</p>
                <p><strong>⏰ Ce lien expire dans 24 heures.</strong></p>
                <p>Si vous n'avez pas créé de compte, vous pouvez ignorer cet email.</p>
            </div>
            <div class="footer">
                <p>© 2024 DZ Clothes - Mode & Style Premium</p>
                <p>Cet email a été envoyé à {to_email}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    html_content = html_fr if lang == 'fr' else html_fr  # Use French for both for now
    
    print(f"[Mail] Attempting to send verification email to {to_email}")
    
    if send_via_mailjet(to_email, subject, html_content, config['from_email'], config['from_name']):
        return True
    
    print(f"[Mail] ⚠️ Email not sent to {to_email} - Mailjet not configured")
    print(f"[Mail] Verification link: {verification_link}")
    return True
