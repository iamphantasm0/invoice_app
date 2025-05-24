import os
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
from weasyprint import HTML
import io
import uvicorn
import base64

app = FastAPI()
# templates = Jinja2Templates(directory="templates")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), 'templates'))

# app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def invoice_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/generate-pdf", response_class=StreamingResponse)
async def generate_pdf(
    request: Request,
    client_name: str = Form(...),
    invoice_number: str = Form(...),
    due_date: str = Form(...),
    discount: float = Form(0.0),
    vat: float = Form(0.0),
    logo: UploadFile = File(None),
    item_description: List[str] = Form(...),
    item_quantity: List[int] = Form(...),
    item_unit_price: List[float] = Form(...)
):
    # Handle logo upload
    logo_base64 = ""
    if logo:
        logo_bytes = await logo.read()
        logo_base64 = base64.b64encode(logo_bytes).decode("utf-8")

    # Calculate totals
    items = []
    subtotal = 0.0
    for desc, qty, unit_price in zip(item_description, item_quantity, item_unit_price):
        total = qty * unit_price
        subtotal += total
        items.append({
            "description": desc,
            "quantity": qty,
            "unit_price": f"{unit_price:,.2f}",
            "total": f"{total:,.2f}"
        })

    vat_amount = subtotal * vat / 100
    total_discount = discount
    total_due = subtotal + vat_amount - total_discount

    html_content = templates.get_template("invoice_template.html").render({
        "request": request,
        "client_name": client_name,
        "invoice_number": invoice_number,
        "due_date": due_date,
        "items": items,
        "subtotal": f"{subtotal:,.2f}",
        "vat_amount": f"{vat_amount:,.2f}",
        "discount": f"{discount:,.2f}",
        "total_price": f"{total_due:,.2f}",
        "logo_base64": logo_base64
    })

    pdf = HTML(string=html_content).write_pdf()
    return StreamingResponse(io.BytesIO(pdf), media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=invoice_{invoice_number}.pdf"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)
