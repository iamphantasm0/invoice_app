# Configuration Changes Summary

## Overview
All hardcoded configuration values have been moved to environment variables using a `.env` file. This allows for easier customization and deployment without modifying the source code.

## Changes Made

### 1. Created `.env` file
Contains all configurable values:
- Company details (name, owner, phone)
- Logo (Base64 encoded)
- Payment policy
- Bank account details
- Currency symbol

### 2. Created `.env.example` file
Template file showing all available configuration options with example values.

### 3. Updated `requirements.txt`
Added `python-dotenv~=1.0.0` for loading environment variables.

### 4. Updated `app/main.py`
- Added `from dotenv import load_dotenv` import
- Added `load_dotenv()` call at startup
- Replaced hardcoded values with `os.getenv()` calls
- All values have fallback defaults matching the original hardcoded values

### 5. Updated `.gitignore`
Added `.env` to prevent committing sensitive configuration to version control.

### 6. Updated `README.md`
Added configuration section with instructions on how to set up the `.env` file.

## How to Use

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your values:**
   - Update company information
   - Update bank account details
   - Customize payment policy
   - Replace logo with your own (Base64 encoded)

3. **Run the app:**
   ```bash
   pip install -r requirements.txt
   python app/main.py
   ```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `COMPANY_NAME` | Company name | Your Company Name |
| `COMPANY_OWNER` | Owner name | Owner Full Name |
| `COMPANY_PHONE` | Contact phone | +1234567890 |
| `LOGO_BASE64` | Base64 encoded logo | YOUR_BASE64_ENCODED_LOGO_HERE |
| `DEFAULT_PAYMENT_POLICY` | Payment terms | Your payment policy text |
| `BANK_NAME` | Bank name | Your Bank Name |
| `ACCOUNT_NAME` | Account holder name | Your Account Name |
| `ACCOUNT_NUMBER` | Account number | 1234567890 |
| `PAYMENT_ADDITIONAL_INFO` | Thank you message | Thank you for your business. |
| `CURRENCY_SYMBOL` | Currency code | USD |

## Benefits

✅ **No code changes needed** - Update configuration without touching source code  
✅ **Environment-specific configs** - Different settings for dev/staging/production  
✅ **Security** - Sensitive data not committed to version control  
✅ **Easy deployment** - Configure via environment variables on hosting platforms  
✅ **Backward compatible** - All defaults match original hardcoded values  

## Deployment Notes

For deployment platforms (Render, Heroku, etc.), you can set environment variables directly in their dashboard instead of using a `.env` file.

