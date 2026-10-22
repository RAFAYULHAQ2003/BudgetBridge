# BudgetBridge

BudgetBridge is a Django-based financial management platform for project budgeting, expense tracking and workforce management. It supports multiple companies, each with its own users, roles and data, and provides role-based access for administrators, project managers, accountants and employees.

## Table of Contents

- [Features](#features)
- [Roles](#roles)
- [Workflow](#workflow)
- [Data Model](#data-model)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Environment Variables](#environment-variables)
  - [Local Setup](#local-setup)
  - [Docker Setup](#docker-setup)

## Features

- **Multi-company architecture:** Manage multiple companies from a single instance, with data isolated between them.
- **Role-based access control (RBAC):** Define custom roles and permissions per company so users only see the features and data relevant to their position.
- **Project management:** Create projects, assign project managers and employees, and track status and budget.
- **Financial management:**
  - **Expense tracking:** Employees submit expenses; authorised users approve or reject them.
  - **Company expenses:** Accountants record and approve company-level expenses.
  - **Invoicing:** Create invoices for clients, track their status and email project payment invoices directly from the application.
  - **Payments:** Record payments with status tracking (pending, confirmed, failed) and multiple payment methods.
- **Workforce management:**
  - **Employee profiles:** Store role, job title, employment type and salary information.
  - **Timesheets:** Employees log hours worked on specific projects.
  - **Payroll:** Run payroll for a period, calculating gross and net pay for each employee.
- **Background processing:** Celery and Redis handle asynchronous tasks such as sending emails.

## Roles

### Admin Panel

The Django admin panel gives superusers and company administrators full control over application data:

- **Users and roles:** Create users, roles and permissions.
- **Companies and projects:** Set up companies, create projects and manage project details.
- **Financial oversight:** View and manage expenses, invoices and payments.
- **Workforce administration:** Manage employee profiles, timesheets and payroll runs.

### Web Application

Non-admin users work through the main web application, built with Django's Model-View-Template (MVT) architecture:

| Role | Capabilities |
|---|---|
| **Employee** | Submit expenses and timesheets; view personal details and payroll information. |
| **Project Manager** | Create projects, assign employees, and approve or reject timesheets and expenses for their projects. |
| **Accountant / Finance Manager** | Manage invoices, record payments, approve company expenses and run payroll. |

## Workflow

### 1. Superadmin Setup

1. Create a superadmin account with `python manage.py createsuperuser`.
2. Log in to the Django admin panel.
3. Create a company and enter its details.
4. Create a user to act as the company administrator.
5. Create a `company_admin` role with the required permissions and assign it to that user.

### 2. Company Admin Setup (Admin Panel)

1. Log in to the Django admin panel.
2. Add users and create an `EmployeeProfile` for each one.
3. Create custom roles with the permissions each type of employee needs.
4. Assign roles to employees.
5. Create clients and projects, and assign a project manager to each project.
6. Assign employees to projects.

### 3. Day-to-Day Use (Web Application)

- **Employees** log in, record timesheets, submit expenses and view their payroll information.
- **Project managers** review and approve or reject timesheets and expenses for their projects.
- **Accountants** generate payroll for a period, manage invoices and record payments.

## Data Model

### Accounts

- **User:** Custom user model with a UUID primary key, email as the unique identifier and a link to the user's company.
- **Role:** A company-specific set of permissions, backed by a Django `Group` for access control.

### Operations

- **Company:** A company using the platform, with its name, registration number and contact details.
- **Client:** A client of a company.
- **Project:** Work undertaken for a client, with a budget, start and end dates, and a status (planned, active, completed).
- **EmployeeProject:** Links an employee to a project and defines their role on it.

### Finance

- **ExpenseCategory:** Expense categories such as travel or supplies.
- **Expense:** An expense submitted against a project, with a status (submitted, approved, rejected), the submitting employee and the approver.
- **Invoice:** An invoice for a client, with a status (draft, sent, partial, paid, overdue), subtotal, tax and total.
- **InvoiceItem:** A line item on an invoice.
- **ProjectPaymentInvoice:** An invoice for project-based billing, kept separate from expense invoices.
- **Payment:** A payment received against a project payment invoice, with a status (pending, confirmed, failed) and payment method (bank transfer, cash, JazzCash).

### Workforce

- **EmployeeProfile:** Job title, employment type (full-time, contract), salary type (fixed, hourly) and joining date.
- **Timesheet:** Hours logged by an employee on a project, with a status (submitted, approved) and payment status.
- **PayrollRun:** A payroll run for a company over a given period.
- **PayrollItem:** One employee's pay for a payroll run, including gross pay, deductions and net pay.

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | [Python 3.12](https://www.python.org/), [Django 5.1](https://www.djangoproject.com/) |
| Database | [PostgreSQL](https://www.postgresql.org/) |
| Task queue | [Celery](https://docs.celeryq.dev/) with [Redis](https://redis.io/) as broker |
| Containerisation | [Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/) |
| CI/CD | GitHub Actions |

## Project Structure

```
BudgetBridge/
├── BudgetBridge/          # Project configuration (settings, URLs, Celery, WSGI/ASGI)
│   └── settings/
│       ├── base.py        # Shared settings
│       ├── local.py       # Local development
│       └── docker.py      # Docker environment
├── accounts/              # Users, roles, authentication and dashboard
├── operations/            # Companies, clients and projects
├── finance/               # Expenses, invoices and payments
├── workforce/             # Employee profiles, timesheets and payroll
├── templates/             # HTML templates
├── static/                # CSS, JavaScript and images
├── Dockerfile
├── docker-compose.yaml
├── docker-compose-dev.yaml
├── entrypoint.sh
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python 3.12
- PostgreSQL
- Redis
- Docker and Docker Compose (for the Docker setup)

### Environment Variables

Create a `.env` file in the project root. It is listed in `.gitignore` and must never be committed.

| Variable | Used by | Description |
|---|---|---|
| `SECRET_KEY` | All | Django secret key |
| `DEBUG` | All | `True` for development, `False` for production |
| `EMAIL_HOST_USER` | All | SMTP username for outgoing email |
| `EMAIL_HOST_PASSWORD` | All | SMTP password or app password |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Local | PostgreSQL connection |
| `REDIS_URL_local` | Local | Redis URL for Celery |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` | Docker | PostgreSQL connection |
| `REDIS_URL` | Docker | Redis URL for Celery |

### Local Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/RAFAYULHAQ2003/BudgetBridge.git
   cd BudgetBridge
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv myenv
   source myenv/bin/activate      # macOS / Linux
   # myenv\Scripts\activate       # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create the database**

   ```sql
   CREATE DATABASE budgetbridge_db;
   CREATE USER budgetbridge_user WITH PASSWORD '<your-db-password>';
   GRANT ALL PRIVILEGES ON DATABASE budgetbridge_db TO budgetbridge_user;
   ```

5. **Configure the environment**

   ```env
   SECRET_KEY=<your-secret-key>
   DEBUG=True

   DB_NAME=budgetbridge_db
   DB_USER=budgetbridge_user
   DB_PASSWORD=<your-db-password>
   DB_HOST=localhost
   DB_PORT=5432

   REDIS_URL_local=redis://localhost:6379/0

   EMAIL_HOST_USER=
   EMAIL_HOST_PASSWORD=
   ```

6. **Start Redis**

   ```bash
   brew services start redis          # macOS
   sudo service redis-server start    # Linux
   ```

7. **Select the local settings module**

   Run this in every terminal you use for the project:

   ```bash
   export DJANGO_SETTINGS_MODULE=BudgetBridge.settings.local
   ```

8. **Apply migrations and create a superuser**

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

9. **Run the development server**

   ```bash
   python manage.py runserver
   ```

10. **Start the Celery worker** (in a second terminal)

    ```bash
    celery -A BudgetBridge worker --loglevel=info
    ```

The application is available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Docker Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/RAFAYULHAQ2003/BudgetBridge.git
   cd BudgetBridge
   ```

2. **Configure the environment**

   ```env
   SECRET_KEY=<your-secret-key>
   DEBUG=True

   POSTGRES_DB=budgetbridge_db
   POSTGRES_USER=budgetbridge_user
   POSTGRES_PASSWORD=<your-db-password>
   POSTGRES_HOST=db
   POSTGRES_PORT=5432

   REDIS_URL=redis://redis:6379/0

   EMAIL_HOST_USER=
   EMAIL_HOST_PASSWORD=
   ```

3. **Build and start the containers**

   ```bash
   docker compose up --build
   ```

   This starts four services:

   | Service | Description |
   |---|---|
   | `server` | Django application on [http://localhost:8000](http://localhost:8000) |
   | `db` | PostgreSQL database |
   | `redis` | Redis broker |
   | `celery` | Celery worker |

   `docker-compose-dev.yaml` runs the prebuilt image published to Docker Hub instead of building locally:

   ```bash
   docker compose -f docker-compose-dev.yaml up
   ```

4. **Create a superuser**

   ```bash
   docker compose exec server python manage.py createsuperuser
   ```

5. **Stop the containers**

   ```bash
   docker compose down
   ```
