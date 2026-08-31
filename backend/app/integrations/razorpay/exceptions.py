class RazorpayException(Exception):
    pass

class SignatureVerificationError(RazorpayException):
    pass
