"""Enhanced email service with multiple providers and better error handling.

Supports:
1. Mailjet API (primary)
2. SMTP fallback (Gmail, Mailtrap, etc.)
3. Console logging for development

Priority: Mailjet → SMTP → Console
"""
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

def get_email_config():
    """Get email configuration from environment."""
    return {
        'mailjet_api_key': os.getenv('MAILJET_API_KEY'),
        'mailjet_secret_key': os.getenv('MAILJET_SECRET_KEY'),
        'smtp_server': os.getenv('MAIL_SERVER'),
        'smtp_port': int(os.getenv('MAIL_PORT', '587')),
        'smtp_username': os.getenv('MAIL_USERNAME'),
        'smtp_password': os.getenv('MAIL_PASSWORD'),
        'smtp_use_tls': os.getenv('MAIL_USE_TLS', 'true').lower() == 'true',
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
                    "From": {
                        "Email": from_email,
                        "Name": from_name
                    },
                    "To": [
                        {
                            "Email": to_email
                        }
                    ],
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
            result = response.json()
            print(f"[Mail] ✅ Mailjet email sent to {to_email}")
            print(f"[Mail] Message ID: {result.get('Messages', [{}])[0].get('To', [{}])[0].get('MessageID', 'N/A')}")
            return True
        else:
            print(f"[Mail] ❌ Mailjet error: {response.status_code}")
            print(f"[Mail] Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("[Mail] ❌ Mailjet timeout - request took too long")
        return False
    except requests.exceptions.ConnectionError:
        print("[Mail] ❌ Mailjet connection error - check internet connection")
        return False
    except Exception as e:
        print(f"[Mail] ❌ Mailjet error: {str(e)}")
        return False


def send_via_smtp(to_email: str, subject: str, html_content: str, from_email: str, from_name: str) -> bool:
    """Send email via SMTP (Gmail, Mailtrap, etc.)."""
    config = get_email_config()
    
    if not config['smtp_server'] or not config['smtp_username'] or not config['smtp_password']:
        print("[Mail] SMTP not configured - skipping")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        
        # Add HTML content
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Connect to SMTP server
        if config['smtp_use_tls']:
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(config['smtp_server'], config['smtp_port'])
        
        # Login and send
        server.login(config['smtp_username'], config['smtp_password'])
        server.send_message(msg)
        server.quit()
        
        print(f"[Mail] ✅ SMTP email sent to {to_email} via {config['smtp_server']}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("[Mail] ❌ SMTP authentication failed - check username/password")
        return False
    except smtplib.SMTPException as e:
        print(f"[Mail] ❌ SMTP error: {str(e)}")
        return False
    except Exception as e:
        print(f"[Mail] ❌ SMTP unexpected error: {str(e)}")
        return False


def log_to_console(to_email: str, subject: str, verification_link: str) -> bool:
    """Log email to console for development."""
    print("\n" + "=" * 80)
    print("📧 EMAIL VERIFICATION (Development Mode)")
    print("=" * 80)
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"Verification Link: {verification_link}")
    print("")
    print("⚠️  Email providers not configured. Set one of:")
    print("   1. Mailjet: MAILJET_API_KEY, MAILJET_SECRET_KEY")
    print("   2. SMTP: MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD")
    print("=" * 80 + "\n")
    return True


def send_verification_email(to_email: str, verification_link: str, lang: str = 'fr') -> bool:
    """
    Send verification email with automatic provider fallback.
    
    Priority: Mailjet → SMTP → Console
    """
    config = get_email_config()
    
    # Prepare email content
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
            .button:hover {{ background: #f0d06f; }}
            .footer {{ background: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }}
            .link {{ word-break: break-all; color: #666; font-size: 12px; }}
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
                <p class="link">{verification_link}</p>
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
    
    html_ar = f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; direction: rtl; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #e8c547 0%, #f0d06f 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .header h1 {{ color: #0a0a0a; margin: 0; font-size: 28px; }}
            .content {{ background: #ffffff; padding: 30px; border: 1px solid #e5e5e5; }}
            .button {{ display: inline-block; background: #e8c547; color: #0a0a0a; padding: 15px 30px; text-decoration: none; border-radius: 50px; font-weight: bold; margin: 20px 0; }}
            .button:hover {{ background: #f0d06f; }}
            .footer {{ background: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }}
            .link {{ word-break: break-all; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>◆ DZ Clothes</h1>
            </div>
            <div class="content">
                <h2>مرحباً بك في DZ Clothes!</h2>
                <p>شكراً لتسجيلك. انقر على الزر أدناه للتحقق من بريدك الإلكتروني:</p>
                <p style="text-align: center;">
                    <a href="{verification_link}" class="button">تحقق من بريدي</a>
                </p>
                <p>أو انسخ هذا الرابط في متصفحك:</p>
                <p class="link">{verification_link}</p>
                <p><strong>⏰ ينتهي صلاحية هذا الرابط خلال 24 ساعة.</strong></p>
                <p>إذا لم تقم بإنشاء حساب، يمكنك تجاهل هذا البريد الإلكتروني.</p>
            </div>
            <div class="footer">
                <p>© 2024 DZ Clothes - أزياء وستايل فاخر</p>
                <p>تم إرسال هذا البريد إلى {to_email}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    html_content = html_fr if lang == 'fr' else html_ar
    
    # Try providers in order: Mailjet → SMTP → Console
    print(f"[Mail] Attempting to send verification email to {to_email}")
    
    # Try Mailjet first
    if send_via_mailjet(to_email, subject, html_content, config['from_email'], config['from_name']):
        return True
    
    # Try SMTP as fallback
    print("[Mail] Mailjet failed, trying SMTP...")
    if send_via_smtp(to_email, subject, html_content, config['from_email'], config['from_name']):
        return True
    
    # Log to console as last resort
    print("[Mail] All email providers failed, logging to console...")
    return log_to_console(to_email, subject, verification_link)


def send_order_confirmation(to_email: str, order_number: str, total: float, items_summary: str, lang: str = 'fr') -> bool:
    """Send order confirmation email."""
    config = get_email_config()
    
    subject = f"Commande confirmée #{order_number} - DZ Clothes" if lang == 'fr' else f"تأكيد الطلب #{order_number} - DZ Clothes"
    
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
            .order-number {{ font-size: 24px; font-weight: bold; color: #e8c547; text-align: center; margin: 20px 0; }}
            .items {{ background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .total {{ font-size: 20px; font-weight: bold; text-align: right; margin-top: 20px; color: #e8c547; }}
            .footer {{ background: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>◆ DZ Clothes</h1>
            </div>
            <div class="content">
                <h2>✅ Commande confirmée !</h2>
                <div class="order-number">#{order_number}</div>
                <p>Merci pour votre commande. Nous avons bien reçu votre paiement Baridi Mob.</p>
                <div class="items">
                    <h3>Votre commande :</h3>
                    <pre>{items_summary}</pre>
                </div>
                <div class="total">Total : {total:.2f} DA</div>
                <p>Nous traiterons votre commande dans les plus brefs délais. Vous recevrez un email de confirmation d'expédition.</p>
            </div>
            <div class="footer">
                <p>© 2024 DZ Clothes - Mode & Style Premium</p>
                <p>Cet email a été envoyé à {to_email}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Try providers in order
    if send_via_mailjet(to_email, subject, html_fr, config['from_email'], config['from_name']):
        return True
    
    if send_via_smtp(to_email, subject, html_fr, config['from_email'], config['from_name']):
        return True
    
    print(f"[Mail] Order confirmation logged to console for {to_email}")
    print(f"Order: {order_number}, Total: {total} DA")
    return True