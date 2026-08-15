# 🏥 Hospital Management System (HMS) — Backend API

A highly structured, RESTful API for a **Hospital Management System (HMS)** built with **Django** and **Django REST Framework (DRF)**. This system provides a comprehensive backend to manage users (with role-based access control), departments, doctors, patients, appointments, prescriptions, billing, and medicines.

The database schema is strictly designed around the Entity-Relationship Diagram (ERD) provided in the project specifications.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-REST%20Framework-092E20)
![License](https://img.shields.io/badge/License-MIT-green)
[![Live Demo](https://img.shields.io/badge/Live-Demo-success)](https://hospital-management-system-backend-ps6p.onrender.com/)

---

## 📑 Table of Contents

- [Tech Stack & DRF Features](#️-tech-stack--drf-features)
- [Database Design & ERD](#️-database-design--erd)
- [Core Features & Functionalities](#-core-features--functionalities)
- [Advanced DRF Implementations](#️-advanced-drf-implementations)
- [API Endpoints](#-api-endpoints-overview)
- [Local Installation & Setup](#-local-installation--setup)
- [Environment Variables](#-environment-variables)
- [Running Tests](#-running-tests)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🛠️ Tech Stack & DRF Features

This project utilizes modern Django REST Framework practices to ensure clean design, modularity, and data integrity.

* **Framework:** Django & Django REST Framework (DRF)
* **Database:** PostgreSQL (Preferred) / SQLite (Development)
* **Authentication:** JWT (JSON Web Tokens) / Token Authentication
* **Role-Based Permissions:** Custom permission classes restricting API access based on roles (`admin`, `doctor`, `patient`, `receptionist`)
* **Filtering & Searching:** `django-filter` integration with custom search and ordering backends
* **Validation:** Strict serializer-level data validation (e.g., status updates, role verification)

---

## 🗄️ Database Design & ERD

### Entity-Relationship Diagram (ERD)

<img width="1341" height="922" alt="Screenshot from 2026-07-17 03-58-35" src="https://github.com/user-attachments/assets/51d1d1cf-7de1-4196-aead-899ebbe49093" />


### Database Schema Overview

The system architecture features clean relational integrity as illustrated in the ERD:

| Model | Relationships | Key Fields |
| :--- | :--- | :--- |
| **User** | Extends Django Base User | `username`, `email`, `role` (Admin, Doctor, Patient, Receptionist) |
| **Doctor** | OneToOne to `User`, FK to `Department` | `specialization`, `experience`, `is_available` |
| **Patient** | OneToOne to `User` | `age`, `gender`, `blood_group`, `phone` |
| **Department** | One-to-Many with `Doctor` | `name`, `description` |
| **Appointment** | FK to `Patient`, FK to `Doctor` | `appointment_date`, `status` |
| **Prescription** | OneToOne to `Appointment` | `diagnosis`, `notes` |
| **PrescriptionMedicine** | FK to `Prescription`, FK to `Medicine` | `dosage`, `duration` |
| **Medicine** | Many-to-Many via PrescriptionMedicine | `name`, `description`, `unit` |
| **Bill** | FK to `Patient` | `amount`, `paid` (boolean) |

---

## 📋 Core Features & Functionalities

### 1. User Management & Authentication
* **Multi-Role Registration:** Supports four distinct registration endpoints for `patient`, `doctor`, `admin`, and `receptionist` roles. Only patient registration is open to the public — doctor, admin, and receptionist accounts can only be created by an existing admin.
* **Secure Authentication:** Secure login with token generation (JWT or DRF Token) to issue access tokens.
* **Profile Auto-linking:** Automatically links users to their respective `Doctor` or `Patient` profiles upon registration.

### 2. Doctor & Patient Profiles
* **Doctor Directory:** Manages doctor details including department, specialization, experience, phone, and active availability status (`is_available`).
* **Patient Profiles:** Keeps track of patient-specific demographics (age, gender, blood group, address, and phone number).

### 3. Appointment Management
* **Scheduling System:** Patients can request or book appointments with specific doctors.
* **Status Lifecycle:** Tracks appointments through key stages: `pending`, `approved`, `completed`, and `cancelled`.
* **Flexible Querying:** Filter appointments instantly by doctor, patient, or date.

### 4. Prescription & Medicine Module
* **Atomic Prescription Creation:** Allows doctors to generate prescriptions containing a diagnosis, general notes, and a list of multiple medicines.
* **PrescriptionMedicine Junction:** Tracks exact dosages and durations for each prescribed item.
* **Medicine Directory:** Global searchable database of medicines.

### 5. Billing System
* **Bill Generation:** Generates invoice bills tied directly to patients.
* **Payment Tracking:** Tracks total payment amount and real-time payment status (`paid` / `unpaid`).

---

## ⚙️ Advanced DRF Implementations

### Custom Role-Based Permissions
API access is controlled via custom permission classes guarding endpoints:
* `IsAdminOrReceptionist`: Only administrators and receptionists can manage billing or update global settings.
* `IsDoctor`: Only active doctors can write or update diagnoses and prescriptions.
* `IsPatient`: Restricts patients to viewing only their own bills, appointments, and prescriptions.

### Filtering, Searching, & Ordering
The API leverages `django-filter` for advanced querying:
* **Appointment Filters:** Filter appointments instantly by `doctor_id`, `patient_id`, `appointment_date`, or `status`.
* **Search Filters:** `SearchFilter` is implemented on Medicines and Doctor specialties (e.g., `/api/medicines/?search=Paracetamol`).

---

## 🔗 API Endpoints Overview

| Endpoint | Method | Description | Access |
| :--- | :--- | :--- | :--- |
| `/api/auth/register/patient/` | POST | Register a new patient (auto-creates Patient profile) | Public |
| `/api/auth/register/doctor/` | POST | Register a new doctor (auto-creates Doctor profile) | Admin |
| `/api/auth/register/admin/` | POST | Register a new hospital admin | Admin |
| `/api/auth/register/receptionist/` | POST | Register a new receptionist | Admin |
| `/api/auth/login/` | POST | Obtain access & refresh tokens | Public |
| `/api/doctors/` | GET | List doctors (filter by department, specialization) | All authenticated |
| `/api/doctors/{id}` | GET | View Doctor Details | All authenticated |
| `/api/doctors/{id}` | PUT, PATCH, DELETE | Update Doctor Details | Admin |
| `/api/patients/` | GET | List patients | All authenticated |
| `/api/patients/{id}` | GET | View Patient Details | All authenticated |
| `/api/patients/{id}` | PUT, PATCH, DELETE | Update or Delete Patient Details | Admin, Receptionist |
| `/api/appointments/` | GET | View appointments | All authenticated |
| `/api/appointments/{id}/` | PUT, PATCH, DELETE | Update/Delete appointment | Doctor, Admin, Receptionist |
| `/api/prescriptions/` | GET | View prescriptions | All authenticated |
| `/api/prescriptions/` | POST | Create prescriptions | Doctor |
| `/api/medicines/?search=` | GET | Search medicine directory | All authenticated |
| `/api/bills/` | GET | View bills | All authenticated |
| `/api/bills/` | POST | Generate bills | Admin, Receptionist |
| `/api/bills/{id}` | GET | View bill details | All authenticated |
| `/api/bills/{id}` | PUT, PATCH, DELETE | Update / delete bill | Admin, Receptionist |

---

## 🚀 Local Installation & Setup

Follow these simple steps to spin up the backend locally on your machine for testing and review.

### Prerequisites
* Python (>= 3.10)
* `pip` (Python Package Installer)
* PostgreSQL (optional — SQLite works out of the box for development)

### Step 1: Clone the Repository
```bash
git clone https://github.com/rohan9932/hospital-management-system-backend.git
cd hospital-management-system-backend
```

### Step 2: Set Up Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the example env file and fill in your own values (see [Environment Variables](#-environment-variables) below).
```bash
cp .env.example .env
```

### Step 5: Run Database Migrations
Generate and apply migrations to build the database tables matching the ERD.
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create a Superuser
Create an administrative account to access the Django Admin Interface.
```bash
python manage.py createsuperuser
```

### Step 7: Run the Development Server
```bash
python manage.py runserver
```

The server will start running at `http://127.0.0.1:8000/`. You can access endpoints or view the interactive browsable API interface directly!

---

## 🔐 Environment Variables

Create a `.env` file in the project root with the following keys:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=your-database-url
```

---

## ✅ Running Tests

```bash
python manage.py test
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
