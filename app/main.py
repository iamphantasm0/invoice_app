import os
import base64
import io
import uuid
from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from weasyprint import HTML # type: ignore
import uvicorn

app = FastAPI(title="Invoice Generator API", version="1.3.0") # Incremented version

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Placeholder Base64 encoded image (e.g., a simple 1x1 transparent pixel or your actual logo)
# You should replace this with your actual logo's base64 string
# To get base64 of your logo:
# 1. Online tool: Search "image to base64"
# 2. Python:
#    with open("path_to_your_logo.png", "rb") as image_file:
#        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
#    print(encoded_string)
PLACEHOLDER_LOGO_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAJYAAABkCAQAAABkASRIAAAAxUlEQVR42u3PMQEAAAgEoDe50yLg0g7g7A4BCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIKgA/gBNr0AARGlZMAAAAAASUVORK5CYII=" # Example: A large transparent PNG

COMPANY_DETAILS = {
    "name": "ONYX and GOLD Fabrics",
    "owner": "Abefe Alaso",
    "phone": "08034343274",
    "address": "123 Fabric Lane, Textile City, NG", # Added example address
    "email": "info@onyxandgold.com", # Added example email
    "website": "www.onyxandgold.com", # Added example website
    "logo_base64": PLACEHOLDER_LOGO_BASE64
}

DEFAULT_PAYMENT_POLICY = (
    "PAYMENT POLICY: 80% Upfront and FULL PAYMENT TO BE COMPLETED BEFORE EVENT DATE.\n"
    "Note: Only financial commitment secures date.\n"
    "Note: A deposit is an agreement to our ‘PAYMENT POLICY’."
)

PAYMENT_DETAILS = {
    "bank_name": "Zenith Bank PLC",
    "account_name": "ONYX AND GOLD FABRICS (Adebimpe Aderemi)",
    "account_number": "1002553295",
    # "payment_terms": DEFAULT_PAYMENT_POLICY, # This will now come from the form
    "additional_info": "Thank you for your prompt payment." # General thank you
}

CURRENCY_SYMBOL = "NGN"

@app.get("/", response_class=HTMLResponse)
async def invoice_form(request: Request):
    invoice_number = f"INV-{uuid.uuid4().hex[:6].upper()}"
    return templates.TemplateResponse("form.html", {
        "request": request,
        "today_date": date.today().isoformat(),
        "auto_invoice_number": invoice_number,
        "payment_policy_default": DEFAULT_PAYMENT_POLICY # Pass default policy to form
    })

@app.post("/generate-pdf", response_class=StreamingResponse)
async def generate_pdf(
    request: Request,
    client_name: str = Form(...),
    client_address: Optional[str] = Form(None),
    client_phone: Optional[str] = Form(None),
    client_email: Optional[str] = Form(None),
    invoice_number: str = Form(...),
    invoice_date: str = Form(...),
    due_date: Optional[str] = Form(None), # Make due_date optional
    project_reference: Optional[str] = Form(None),
    discount: float = Form(0.0),
    vat_percentage: float = Form(0.0),
    payment_policy: str = Form(DEFAULT_PAYMENT_POLICY), # Get policy from form
    item_description: List[str] = Form(...),
    item_quantity: List[float] = Form(...), # Ensure these can be float for things like 1.5 meters
    item_unit_price: List[float] = Form(...)
):
    if not (len(item_description) == len(item_quantity) == len(item_unit_price)):
        raise HTTPException(status_code=400, detail="Mismatch in item list lengths. Ensure all item fields are filled for each row.")

    # Filter out empty/incomplete items before further processing
    valid_items_data = []
    for i in range(len(item_description)):
        desc = item_description[i]
        qty = item_quantity[i]
        price = item_unit_price[i]
        if desc and desc.strip() and qty is not None and price is not None: # Basic check
             valid_items_data.append({"description": desc, "quantity": qty, "unit_price": price})

    if not valid_items_data:
        raise HTTPException(status_code=400, detail="At least one complete item (description, quantity, price) must be added.")

    logo_base64 = COMPANY_DETAILS.get("logo_base64", "")

    items = []
    subtotal = 0.0
    for item_data in valid_items_data:
        desc = item_data["description"]
        qty = item_data["quantity"]
        unit_price = item_data["unit_price"]
        
        total = qty * unit_price
        subtotal += total
        items.append({
            "description": desc,
            "quantity": qty, # Keep as number for potential calculations if needed later
            "unit_price_formatted": f"{unit_price:,.2f}",
            "total_formatted": f"{total:,.2f}"
        })

    # discount_amount = discount # Assuming discount is already the amount
    # vat_amount = (subtotal - discount_amount) * (vat_percentage / 100.0)
    # total_due = subtotal - discount_amount + vat_amount
    
    # Recalculate based on form values which should be 0 if disabled
    actual_discount = discount if discount > 0 else 0.0
    subtotal_after_discount = subtotal - actual_discount
    actual_vat_amount = subtotal_after_discount * (vat_percentage / 100.0) if vat_percentage > 0 else 0.0
    total_due = subtotal_after_discount + actual_vat_amount


    context = {
        "request": request,
        "company": COMPANY_DETAILS,
        "payment": PAYMENT_DETAILS, # Keep for bank details
        "currency_symbol": CURRENCY_SYMBOL,
        "client_name": client_name,
        "client_address": client_address,
        "client_phone": client_phone,
        "client_email": client_email,
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "project_reference": project_reference,
        "items": items,
        "subtotal_formatted": f"{subtotal:,.2f}",
        "discount_formatted": f"{actual_discount:,.2f}",
        "vat_percentage_display": f"{vat_percentage:.2f}%" if vat_percentage > 0 else "0.00%",
        "vat_amount_formatted": f"{actual_vat_amount:,.2f}",
        "total_price_formatted": f"{total_due:,.2f}",
        "logo_base64": logo_base64,
        "payment_policy": payment_policy # Pass the (potentially edited) policy
    }

    try:
        html_content = templates.get_template("invoice_template.html").render(context)
        # For debugging HTML output:
        # with open("rendered_invoice.html", "w", encoding="utf-8") as f:
        # f.write(html_content)
        # print("Rendered HTML to rendered_invoice.html")

        pdf = HTML(string=html_content, base_url=str(request.base_url)).write_pdf() # Added base_url for WeasyPrint if it needs to resolve relative paths for CSS/images if not embedded
    except Exception as e:
        print(f"Error during PDF generation: {e}") # Log error to console
        # For more detailed WeasyPrint errors, you might need to check its logs or use a debugger
        raise HTTPException(status_code=500, detail=f"Error generating PDF. Check server logs. Details: {str(e)[:200]}")


    return StreamingResponse(
        io.BytesIO(pdf),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{invoice_number}_{client_name.replace(' ', '_')}.pdf"
        }
    )

if __name__ == "__main__":
    if not os.path.exists(TEMPLATES_DIR):
        print(f"Error: Templates directory '{TEMPLATES_DIR}' not found.")
        exit(1)
    # Ensure static directory exists for any static files you might add later
    if not os.path.exists(STATIC_DIR):
        os.makedirs(STATIC_DIR, exist_ok=True)
        print(f"Created static directory: {STATIC_DIR}")

    print(f"Serving API on http://127.0.0.1:8002")
    print(f"Templates directory: {TEMPLATES_DIR}")
    print(f"Static directory: {STATIC_DIR}")
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)

