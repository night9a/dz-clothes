"""Send verification emails via SMTP (free, no API key). No SMTP config = log link to console."""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_email(to_email: str, verification_link: str, lang: str = 'fr') -> bool:
    subject = "Vérifiez votre email - DZ Clothes" if lang == 'fr' else "تحقق من بريدك الإلكتروني - DZ Clothes"
    html_fr = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Bienvenue sur DZ Clothes</h2>
        <p>Cliquez sur le lien ci-dessous pour vérifier votre adresse email :</p>
        <p><a href="{verification_link}" style="background: #1e40af; color: #fff; padding: 12px 24px; text-decoration: none; border-radius: 8px;">Vérifier mon email</a></p>
        <p>Ou copiez ce lien : {verification_link}</p>
        <p>Ce lien expire dans 24 heures.</p>
    </div>
    """
    html_ar = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; direction: rtl;">
        <h2>مرحباً بك في DZ Clothes</h2>
        <p>انقر على الرابط أدناه للتحقق من بريدك الإلكتروني:</p>
        <p><a href="{verification_link}" style="background: #1e40af; color: #fff; padding: 12px 24px; text-decoration: none; border-radius: 8px;">تحقق من بريدي</a></p>
        <p>أو انسخ هذا الرابط: {verification_link}</p>
        <p>ينتهي صلاحية هذا الرابط خلال 24 ساعة.</p>
    </div>
    """
    html = html_fr if lang == 'fr' else html_ar

    server = os.getenv('MAIL_SERVER')
    port = int(os.getenv('MAIL_PORT', '587'))
    username = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    use_tls = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    from_addr = os.getenv('MAIL_FROM', username or 'noreply@dzclothes.dz')

    if server and username and password:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_addr
            msg['To'] = to_email
            msg.attach(MIMEText(html, 'html', 'utf-8'))
            with smtplib.SMTP(server, port) as s:
                if use_tls:
                    s.starttls()
                s.login(username, password)
                s.sendmail(from_addr, [to_email], msg.as_string())
            return True
        except Exception as e:
            print(f"[DZ Clothes] Email send failed: {e}")
            return False

    # No SMTP configured: log link so you can verify without any API key (dev-friendly)
    print("\n" + "=" * 60)
    print("[DZ Clothes] Email verification (no SMTP configured)")
    print(f"  To: {to_email}")
    print(f"  Link: {verification_link}")
    print("  Copy the link above into your browser to verify.")
    print("  To send real emails, set MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD in .env (e.g. Mailtrap free).")
    print("=" * 60 + "\n")
    return True
