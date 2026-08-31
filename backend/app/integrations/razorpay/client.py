import hmac
import hashlib
from app.config import settings
from .exceptions import SignatureVerificationError

def verify_webhook_signature(payload_body: bytes, signature_header: str, secret: str = None) -> bool:
    if secret is None:
        secret = settings.RAZORPAY_WEBHOOK_SECRET
    
    if not secret:
        raise SignatureVerificationError("Webhook secret is not configured")
        
    expected_signature = hmac.new(
        key=secret.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_signature, signature_header):
        raise SignatureVerificationError("Invalid signature")
        
    return True
