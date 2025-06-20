import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

PLACEHOLDER_LOGO_BASE64 = os.environ.get("PLACEHOLDER_LOGO_BASE64")

COMPANY_DETAILS = {
    "name": os.environ.get("COMPANY_NAME", ""),
    "owner": os.environ.get("COMPANY_OWNER", ""),
    "phone": os.environ.get("COMPANY_PHONE", ""),
    "address": os.environ.get("COMPANY_ADDRESS", ""),
    "email": os.environ.get("COMPANY_EMAIL", ""),
    "website": os.environ.get("COMPANY_WEBSITE", ""),
    "logo_base64": PLACEHOLDER_LOGO_BASE64,
}

DEFAULT_PAYMENT_POLICY = os.environ.get("DEFAULT_PAYMENT_POLICY", "")

PAYMENT_DETAILS = {
    "bank_name": os.environ.get("PAYMENT_BANK_NAME", ""),
    "account_name": os.environ.get("PAYMENT_ACCOUNT_NAME", ""),
    "account_number": os.environ.get("PAYMENT_ACCOUNT_NUMBER", ""),
    "additional_info": os.environ.get("PAYMENT_ADDITIONAL_INFO", ""),
}

CURRENCY_SYMBOL = os.environ.get("CURRENCY_SYMBOL", "NGN")