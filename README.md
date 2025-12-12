# 🧾 Invoice Generator – ONYX and GOLD Fabrics

This is a simple FastAPI-powered web application that lets users generate and download styled PDF invoices. It was originally built for ONYX and GOLD Fabrics to streamline their client invoicing.

## ✨ Features

- Fast, browser-based invoice form
- Add multiple line items (description, quantity, unit price)
- Calculates subtotal, VAT, discount, and total due
- Clean Tailwind-inspired styling
- Outputs downloadable PDF invoice (no new tab)
- Dockerized and deployable (e.g., Render, Fly.io)

## 🚀 Live Demo

You can try the app here:  
👉 **[https://invoice-app-7xim.onrender.com/](https://invoice-app-7xim.onrender.com/)**

## 📦 Usage

1. Fill in client details, invoice number, dates, and items.
2. (Optionally) upload a logo.
3. Click **Generate PDF** to immediately download a styled invoice.

> This app was built with simplicity in mind — it doesn’t use a database or email system by default.

---

## ⚙️ Configuration

The app uses environment variables for easy customization. Configuration is stored in a `.env` file.

> **Note:** The `.env` file is gitignored for privacy. Your sensitive business information stays local.

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your details:**
   - Company name, owner, phone
   - Bank account details
   - Payment policy
   - Logo (Base64 encoded - see instructions in `.env.example`)
   - Currency symbol

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   python app/main.py
   ```

The app will be available at `http://127.0.0.1:8002`

---

## 🔧 Customization

If you or your business needs a **more robust version** of this app — such as:
- Invoice tracking or history
- Admin panel or client login
- Email delivery of invoices
- Database persistence
- Online payments integration

👉 Feel free to reach out: **[iamphantasm0@gmail.com](mailto:iamphantasm0@gmail.com)**  
I'd be happy to help tailor a version that fits your workflow better.

---

## 📄 License

MIT © 2025 ONYX and GOLD Fabrics / built by [@iamphantasm0](mailto:iamphantasm0@gmail.com)
