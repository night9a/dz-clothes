"""Send verification emails via Mailjet API.

If Mailjet is not configured, we log the verification link to the console so
you can still verify accounts during development.
"""
import os
import requests

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

    api_key = os.getenv('MAILJET_API_KEY')
    secret_key = os.getenv('MAILJET_SECRET_KEY')
    from_email = os.getenv('MAIL_FROM', 'noreply@dzclothes.dz')

    if api_key and secret_key:
        try:
            payload = {
                "Messages": [
                    {
                        "From": {"Email": from_email, "Name": "DZ Clothes"},
                        "To": [{"Email": to_email}],
                        "Subject": subject,
                        "HTMLPart": html,
                    }
                ]
            }
            r = requests.post(
                "https://api.mailjet.com/v3.1/send",
                auth=(api_key, secret_key),
                json=payload,
                timeout=10,
            )
            if r.status_code in (200, 201):
                return True
            print(f"[DZ Clothes] Mailjet error: {r.status_code} {r.text}")
            return False
        except Exception as e:
            print(f"[DZ Clothes] Mailjet send failed: {e}")
            return False

    # No Mailjet configured: log link for manual verification (dev-friendly)
    print("\n" + "=" * 60)
    print("[DZ Clothes] Email verification (Mailjet non configuré)")
    print(f"  To: {to_email}")
    print(f"  Link: {verification_link}")
    print("  Configurez MAILJET_API_KEY et MAILJET_SECRET_KEY dans .env pour envoyer de vrais emails.")
    print("=" * 60 + "\n")
    return True
