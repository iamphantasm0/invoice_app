import os
import base64
import io
from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse # Changed from star import
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from weasyprint import HTML # type: ignore
import uvicorn

app = FastAPI(title="Invoice Generator API", version="1.1.0")

# --- Configuration (Consider moving to a config file or environment variables for a real app) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static") # Define static directory path

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Mount static files - uncommented and path adjusted
# Create a 'static' directory in the same location as main.py if you want to serve local CSS/JS for form.html
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


COMPANY_DETAILS = {
    "name": "ONYX and GOLD Fabrics",
    "owner": "Abefe Alaso",
    "phone": "08034343274",
    "address": "",
    "email": "",
    "website": ""
}

PAYMENT_DETAILS = {
    "bank_name": "Zenith Bank PLC",
    "account_name": "ONYX AND GOLD FABRICS (Adebimpe Aderemi)",
    "account_number": "1002553295",
    "payment_terms": "",
    "additional_info": "Thank you for your prompt payment."
}

CURRENCY_SYMBOL = "NGN"
# --- End Configuration ---

@app.get("/", response_class=HTMLResponse)
async def invoice_form(request: Request):
    """Serves the HTML form to create an invoice."""
    return templates.TemplateResponse("form.html", {
        "request": request,
        "today_date": date.today().isoformat() # For defaulting invoice date
    })

@app.post("/generate-pdf", response_class=StreamingResponse)
async def generate_pdf(
    request: Request,
    client_name: str = Form(...),
    client_address: Optional[str] = Form(None),
    client_phone: Optional[str] = Form(None),
    client_email: Optional[str] = Form(None),
    invoice_number: str = Form(...),
    invoice_date: str = Form(...), # Added
    due_date: str = Form(...),
    project_reference: Optional[str] = Form(None), # Added
    discount: float = Form(0.0),
    vat_percentage: float = Form(0.0), # Renamed for clarity (e.g., user enters 7.5 for 7.5%)
    logo: Optional[UploadFile] = File(None),
    item_description: List[str] = Form(...),
    item_quantity: List[float] = Form(...), # Changed to float for quantities like 1.5 meters
    item_unit_price: List[float] = Form(...)
):
    """Generates a PDF invoice from the submitted form data."""

    # Validate that all item-related lists have the same number of elements
    if not (len(item_description) == len(item_quantity) == len(item_unit_price)):
        raise HTTPException(
            status_code=400,
            detail="Mismatch in the number of item descriptions, quantities, or unit prices. Please ensure each item has all three fields."
        )
    if not item_description or not item_description[0]: # Check if at least one item is added
         raise HTTPException(
            status_code=400,
            detail="At least one item must be added to the invoice."
        )


    logo_base64 = ""
    if logo and logo.filename: # Check if a file was actually uploaded
        try:
            logo_bytes = await logo.read()
            logo_base64 = base64.b64encode(logo_bytes).decode("utf-8")
        except Exception as e:
            # Log error or handle appropriately, for now, we'll just skip the logo
            print(f"Error reading logo: {e}")
            logo_base64 = "" # Ensure it's empty on error


    items = []
    subtotal = 0.0
    for i in range(len(item_description)):
        desc = item_description[i]
        qty = item_quantity[i]
        unit_price = item_unit_price[i]

        if not desc: # Skip if description is empty (e.g. user added an empty item row)
            continue

        total = qty * unit_price
        subtotal += total
        items.append({
            "description": desc,
            "quantity": qty, # Keep as number for potential further calculations if needed
            "unit_price_formatted": f"{unit_price:,.2f}",
            "total_formatted": f"{total:,.2f}"
        })

    if not items: # If all items were skipped due to empty descriptions
        raise HTTPException(
            status_code=400,
            detail="No valid items found. Please ensure item descriptions are filled."
        )

    vat_amount = (subtotal - discount) * vat_percentage / 100 # Calculate VAT on discounted subtotal
    total_due = subtotal - discount + vat_amount

    # Prepare context for the template
    template_context = {
        "request": request,
        "company": COMPANY_DETAILS,
        "payment": PAYMENT_DETAILS,
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
        "discount_formatted": f"{discount:,.2f}",
        "vat_percentage_display": f"{vat_percentage:.2f}%", # For display
        "vat_amount_formatted": f"{vat_amount:,.2f}",
        "total_price_formatted": f"{total_due:,.2f}",
        "logo_base64": logo_base64
    }

    try:
        html_content = templates.get_template("invoice_template.html").render(template_context)
    except Exception as e:
        print(f"Error rendering template: {e}")
        raise HTTPException(status_code=500, detail="Error rendering invoice template.")

    try:
        # For WeasyPrint, ensure base_url is set if you have relative paths for CSS/images in template
        # that are not handled by Tailwind CDN or base64 embedding.
        # Here, we assume most styling is via Tailwind CDN or inline.
        # If serving local CSS for PDF from 'static' dir:
        # base_url = str(request.url_for('static', path='')) # or specific CSS file
        # pdf = HTML(string=html_content, base_url=base_url).write_pdf()
        pdf = HTML(string=html_content).write_pdf()

    except Exception as e:
        print(f"Error generating PDF with WeasyPrint: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {e}")

    return StreamingResponse(
        io.BytesIO(pdf),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{invoice_number}_{client_name.replace(' ', '_')}.pdf"
        }
    )

if __name__ == "__main__":
    # It's good practice to ensure the templates directory exists when running directly
    if not os.path.exists(TEMPLATES_DIR):
        print(f"Error: Templates directory '{TEMPLATES_DIR}' not found.")
        exit(1)
        
    print(f"Serving API on http://127.0.0.1:8002")
    print(f"Templates directory: {TEMPLATES_DIR}")
    print(f"Static directory: {STATIC_DIR}")
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)
