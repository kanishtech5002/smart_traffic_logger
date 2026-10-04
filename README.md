# Smart Traffic Violation Logger

An efficient, clean, and beginner-friendly web application built with **Python Flask**, **SQLite**, and **SQLAlchemy ORM** designed for traffic police and authorized law enforcement officers to digitally record, track, search, and manage traffic violations with dynamic QR code e-challans and public status verification.

---

## 📌 Project Overview

Traditional paper-based traffic ticketing is slow, prone to data loss, and difficult to verify in real-time. **Smart Traffic Violation Logger** simplifies traffic enforcement by providing:
1. **Officer Management Portal**: Authenticated access to log violations, inspect traffic history, manage payment status, and print digital receipts.
2. **Dynamic QR Code Generation**: Every violation generates a unique QR code linked directly to a public verification URL.
3. **Public Citizen Status Verification**: A secure, read-only webpage reachable by scanning the QR code, allowing vehicle owners to check challan authenticity and payment status without needing an officer account.

---

## 🚀 Key Features

* **Log Violations (Create)**: Record vehicle registration numbers (normalized to uppercase), violation types, locations, offense dates, and fine amounts. All new entries automatically default to **Unpaid**.
* **Real-time Dashboard (Read)**: Displays live enforcement statistics: Total Violations, Paid Violations, and Unpaid Violations, along with recent offense activity.
* **Violation History (Read)**: View records in a responsive Bootstrap table with color-coded status badges (`Paid` / `Unpaid`).
* **Instant Search by Vehicle Number**: Quickly look up all past offenses linked to a specific vehicle registration number.
* **Multi-Parameter Filtering**: Simultaneously filter records by:
  - **Violation Date**
  - **Payment Status** (`All`, `Paid`, `Unpaid`)
  - **Violation Type** (`No Helmet`, `Overspeeding`, `Signal Violation`, etc.)
  - Includes a one-click **Clear Filters** reset button.
* **Update Payment Status (Update)**: Single-click `Mark as Paid` action that immediately updates the database and reflects in the UI and QR verification page.
* **Full CRUD Support**: Complete Create, Read, Update (edit details), and Delete operations (with safety confirmation modal).
* **Digital Printable Challan**: Generates an official, print-friendly e-challan receipt with vehicle details, penalty information, and browser `Print Challan` functionality.
* **Dynamic QR Code Generation**: Automatically creates a QR code image saved under `static/qr_codes/challan_<id>.png` containing the URL to the public verification page.
* **Public Status Page**: Accessible at `/status/<violation_id>` without officer credentials. Read-only view for citizens; safely rejects non-existent challans with `"Invalid or unavailable challan."`
* **Officer Authentication (Security)**: Flask session-based login protecting all management routes, ensuring only authorized personnel can alter violation data.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| **Backend Framework** | Python 3, Flask |
| **Database & ORM** | SQLite 3, Flask-SQLAlchemy |
| **Frontend UI** | HTML5, CSS3, Bootstrap 5, Bootstrap Icons |
| **Templating Engine** | Jinja2 (Template Inheritance via `base.html`) |
| **QR Code Engine** | Python `qrcode`, Pillow (`PIL`) |

---

## 📂 Project Directory Structure

```text
smart_traffic_violation_logger/
│
├── app.py                      # Main Flask application, routes, models, & logic
├── requirements.txt            # Python dependencies
├── README.md                   # Full documentation & project guide
│
├── instance/
│   └── traffic.db              # SQLite database file (created automatically)
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom styles & print stylesheet
│   │
│   └── qr_codes/               # Dynamically generated PNG QR codes
│       ├── challan_1.png
│       └── ...
│
└── templates/
    ├── base.html               # Master layout with responsive navbar & alerts
    ├── login.html              # Officer authentication page
    ├── dashboard.html          # Stats counter cards & recent activity
    ├── add_violation.html      # New violation entry form
    ├── history.html            # Search, filter, and violations table
    ├── edit_violation.html     # Edit violation details form
    ├── challan.html            # Printable digital e-challan with QR code
    └── public_status.html      # Citizen read-only status verification
```

---

## 💻 Installation & Setup (Windows)

### Step 1: Open Terminal / Command Prompt
Navigate to the project directory:
```bash
cd "C:\Users\kanis\OneDrive\Desktop\Smart Traffic"
```

### Step 2: Create a Python Virtual Environment (Recommended)
```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment
On Windows Command Prompt:
```cmd
venv\Scripts\activate
```
Or in PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

Start the Flask development server:
```bash
python app.py
```

Open your web browser and visit:
```text
http://127.0.0.1:5000
```

---

## 🔑 Officer Login Credentials (Demo)

For demonstration purposes, the application includes pre-configured officer credentials:

* **Username:** `officer`
* **Password:** `traffic123`

*(Note: Citizens scanning a QR code do **not** need to log in to view their challan status!)*

---

## 🧪 Pre-loaded Test Data

When initialized on a fresh database, the application automatically seeds the following demo records with their respective QR codes:

| ID | Vehicle Number | Violation Type | Location | Date | Fine Amount | Status |
|---|---|---|---|---|---|---|
| #1 | `TN30AB1234` | No Helmet | Salem | 2026-09-26 | ₹1000 | Unpaid |
| #2 | `TN33CD5678` | Overspeeding | Namakkal | 2026-09-25 | ₹2000 | Paid |
| #3 | `TN29EF9012` | Signal Violation | Erode | 2026-09-24 | ₹500 | Unpaid |

---

## 🗺️ Application Workflow

```text
TRAFFIC OFFICER
       ↓
    Login (/login)
       ↓
    Dashboard (/dashboard)
       ↓
 Add Violation (/add-violation)
       ↓
 Enter: Vehicle Number, Type, Location, Date, Fine
       ↓
     Save
       ↓
 SQLite Database (status automatically = "Unpaid")
       ↓
 Generate Dynamic QR Code (static/qr_codes/challan_<id>.png)
       ↓
 Digital Challan (/challan/<id>)
       ↓
┌──────────────────────────────────────┐
│                                      │
↓                                      ↓
Search & Filter Records            Scan QR Code
(/history)                             ↓
│                                  Public Status (/status/<id>)
↓                                      ↓
Edit / Delete / Mark as Paid       Read-Only Violation & Payment Info
```

---

## 🌐 Flask Routes Overview

| Route | Method | Access | Description |
|---|---|---|---|
| `/` | `GET` | Protected | Redirects to `/dashboard` |
| `/dashboard` | `GET` | Protected | Displays summary statistics and recent records |
| `/login` | `GET`, `POST` | Public | Officer login form & session creation |
| `/logout` | `GET` | Protected | Destroys session and logs out officer |
| `/add-violation` | `GET`, `POST` | Protected | Logs new violation with automatic `Unpaid` status |
| `/history` | `GET` | Protected | Search by vehicle, filter by date, type, status |
| `/edit/<id>` | `GET`, `POST` | Protected | Edit violation details and payment status |
| `/delete/<id>` | `POST` | Protected | Deletes violation record and removes QR code |
| `/mark-paid/<id>` | `GET`, `POST` | Protected | Quick-updates status from `Unpaid` to `Paid` |
| `/challan/<id>` | `GET` | Protected | Displays printable digital challan with QR code |
| `/status/<id>` | `GET` | **Public** | Citizen read-only verification page (QR destination) |

---

## 🎓 Viva Questions & Answers

### Q1: Why use SQLAlchemy ORM instead of raw SQLite queries?
> **Answer:** SQLAlchemy translates Python classes and objects into SQL statements. It prevents SQL injection attacks through automatic parameter binding, improves code readability, eliminates manual cursor handling, and allows easy migration between database engines if needed.

### Q2: How does the QR code work in this project?
> **Answer:** When an officer logs a violation, the backend uses Python's `qrcode` library to encode the absolute URL of the public status page (`/status/<id>`). The resulting image is saved in `static/qr_codes/challan_<id>.png`. When scanned by a phone camera, it directs the browser to the public status page.

### Q3: Why is the `/status/<id>` route public while other routes are protected?
> **Answer:** Citizens receiving a physical or digital challan need to verify their ticket without having police department credentials. The public route is strictly read-only, preventing any unauthorized modification or deletion of records.

### Q4: How is the payment status workflow maintained?
> **Answer:** Newly created records are strictly hardcoded to `status = "Unpaid"` upon insertion. Only authenticated officers can invoke `/mark-paid/<id>` or edit the status to `Paid`.

### Q5: How do browser print styles work on the challan page?
> **Answer:** In `style.css`, `@media print` queries hide navigation bars, buttons, and footers, ensuring only the official receipt card is rendered on paper or PDF.

---

## ⚙️ Common Errors & Troubleshooting

1. **`ModuleNotFoundError: No module named 'flask'`**
   - Solution: Activate your virtual environment and run `pip install -r requirements.txt`.
2. **`OperationalError: unable to open database file`**
   - Solution: Ensure the `instance/` directory exists and has write permissions. `app.py` automatically creates it using `os.makedirs(app.instance_path, exist_ok=True)`.
3. **QR Code image not showing on challan**
   - Solution: Ensure the `static/qr_codes/` directory exists. The application automatically re-generates missing QR codes upon accessing the challan route.
4. **Port 5000 is already in use**
   - Solution: Change the port in `app.run(port=5001)` or terminate the process occupying port 5000.
