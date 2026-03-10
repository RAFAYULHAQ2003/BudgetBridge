# BudgetBridge

BudgetBridge is a comprehensive, Django-based financial management platform designed to streamline project budgeting, expense tracking, and workforce management for companies. It provides a multi-user environment with role-based access control, allowing for efficient collaboration between administrators, project managers, and employees.

## Features

- **Multi-Company Architecture:** Each instance of BudgetBridge can manage multiple companies, with data isolated between them.
- **Role-Based Access Control (RBAC):**  Define custom roles and permissions for users within a company, ensuring that users can only access the features and data relevant to their position.
- **Project Management:** Create and manage projects, assign project managers, and track project status and budget.
- **Financial Management:**
    - **Expense Tracking:** Employees can submit expenses, which can then be approved or rejected by authorized users.
    - **Invoicing:** Create and manage invoices for clients, track their status (draft, sent, paid), and record payments.
- **Workforce Management:**
    - **Employee Profiles:** Maintain detailed profiles for each employee, including their role, job title, and salary information.
    - **Timesheets:** Employees can submit timesheets for the hours they've worked on specific projects.
    - **Payroll Processing:** Run payroll for a given period, calculating gross and net pay for each employee.
- **Admin Panel:** A user-friendly admin panel (powered by `django-jazzmin` and `django-unfold`) for managing all aspects of the application.

## Roles

### Admin Panel

The Django admin panel provides a comprehensive interface for superusers to manage all data in the application, including:

- **User and Role Management:** Create and manage users, roles, and permissions.
- **Company and Project Management:**  Set up new companies, create projects, and manage project details.
- **Financial Oversight:**  View and manage all expenses, invoices, and payments across all companies.
- **Workforce Administration:** Manage employee profiles, timesheets, and payroll runs.

### Frontend (MVT)

The frontend of the application is built using Django's Model-View-Template (MVT) architecture. This provides a user-friendly interface for non-admin users to interact with the system.

- **Employees:** Can submit expenses and timesheets, and view their own payroll information.
- **Project Managers:** Can manage the projects they are assigned to, approve expenses and timesheets for their projects, and view project-related financial data.
- **Finance Managers/Accountants:** Can manage invoices, record payments, and run payroll.

## Workflow

The application follows a structured workflow, with different roles performing specific tasks.

### 1. Superadmin Setup

1.  **Create a Superadmin:** The first step is to create a superadmin account using the `createsuperuser` management command.
2.  **Log in to Admin Panel:** The superadmin logs into the Django admin panel.
3.  **Create a Company:** The superadmin creates a new company and adds its details.
4.  **Create a Company Admin:** The superadmin creates a new user who will be the administrator for the company.
5.  **Assign Permissions:** The superadmin creates a `company_admin` role with the necessary permissions and assigns this role to the company admin user.

### 2. Company Admin Setup (from Admin Panel)

1.  **Log in to Admin Panel:** The company admin logs into the Django admin panel.
2.  **Add Users and Employees:** The company admin adds new users and creates `EmployeeProfile`s for them.
3.  **Create Custom Roles:** The company admin creates custom roles with specific permissions for different types of employees within the company.
4.  **Assign Roles:** The company admin assigns these roles to the employees.
5.  **Create Projects and Clients:** The company admin creates new projects, adds clients for those projects, and assigns a project manager to each project.
6.  **Assign Employees to Projects:** The company admin assigns employees to the relevant projects.

### 3. Standard User Actions (from Frontend)

Once the setup is complete, standard users can perform their tasks through the frontend of the application.

-   **Employees:**
    -   Log in to the application.
    -   Add timesheets for the hours they've worked.
    -   Submit expenses.
    -   View their personal details and payroll information.
-   **Project Managers:**
    -   Log in to the application.
    -   Review and approve or reject timesheets submitted by employees for their projects.
    -   Review and approve or reject expenses submitted for their projects.
-   **Accountants/Finance Managers:**
    -   Log in to the application.
    -   Generate payroll for the company for a given period.
    -   Manage invoices and record payments.

## Models and Features

### Accounts

- **User:** Extends the default Django `User` model with a UUID primary key, an email as the unique identifier, and a link to the company they belong to.
- **Role:**  Defines a role within a company, with a set of associated permissions. Each role is linked to a Django `Group` to enforce access control.

### Operations

- **Company:** Represents a company using the platform. Contains basic company information such as name, registration number, and contact details.
- **Client:** Represents a client of a company.
- **Project:** Represents a project undertaken by a company for a client. It has a budget, a start and end date, and a status (planned, active, completed).
- **EmployeeProject:** A through model that links an employee to a project, defining their role in that project.

### Finance

- **ExpenseCategory:** Categories for expenses (e.g., travel, supplies).
- **Expense:** Represents an expense submitted by an employee for a specific project. It has a status (submitted, approved, rejected) and is linked to the employee who submitted it and the user who approved it.
- **Invoice:** Represents an invoice sent to a client for a project. It has a status (draft, sent, partial, paid, overdue) and includes details such as subtotal, tax, and total amount.
- **InvoiceItem:** Represents a line item on an invoice.
- **Payment:** Represents a payment received for an invoice.

### Workforce

- **EmployeeProfile:**  Contains detailed information about an employee, including their job title, employment type (full-time, contract), salary type (fixed, hourly), and joining date.
- **Timesheet:**  Represents a timesheet submitted by an employee for the hours they've worked on a specific project. It has a status (submitted, approved).
- **PayrollRun:** Represents a payroll run for a specific period for a company.
- **PayrollItem:** Represents the payroll details for a single employee for a specific payroll run, including gross pay, deductions, and net pay.

## Technology Stack

- **Backend:**
    - [Django](https://www.djangoproject.com/): A high-level Python Web framework.
    - [Django REST framework](https://www.django-rest-framework.org/): A powerful and flexible toolkit for building Web APIs (although this project seems to be primarily MVT).
    - `django-jazzmin`: For a modern, responsive admin theme.
    - `django-unfold`: For a modern, responsive admin theme.
- **Database:**
    - [PostgreSQL](https://www.postgresql.org/): A powerful, open source object-relational database system.
- **Containerization:**
    - [Docker](https://www.docker.com/): For containerizing and running the application.
    - [Docker Compose](https://docs.docker.com/compose/): For defining and running multi-container Docker applications.



## How to Run the App

### Local Setup (without Docker)

1. **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd BudgetBridge
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv myenv
    source myenv/bin/activate  # macOS/Linux
    # myenv\Scripts\activate    # Windows
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the database (PostgreSQL) & ENV:**
    - Make sure PostgreSQL is installed and running.
    - Create a database and user for the app:
      ```sql
      CREATE DATABASE budgetbridge_db;
      CREATE USER budgetbridge_user WITH PASSWORD '12345678';
      GRANT ALL PRIVILEGES ON DATABASE budgetbridge_db TO budgetbridge_user;
      ```
    - Create a `.env` file in the root directory with the following:
      ```env
      SECRET_KEY=<your-secret-key>
      DEBUG=True
      DB_NAME=budgetbridge_db
      DB_USER=budgetbridge_user
      DB_PASSWORD=12345678
      DB_HOST=localhost
      DB_PORT=5432
      REDIS_URL_LOCAL=redis://localhost:6379/0

      # Email
      EMAIL_HOST_USER=
      EMAIL_HOST_PASSWORD=

      ```

5. **Start Redis (if not already running):**
    ```bash
    brew services start redis   # macOS
    # or for Linux:
    sudo service redis-server start
    ```

6. **Run Django migrations:**
    ```bash
    python manage.py migrate
    ```

7. **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```

8. **Start the Django development server:**
    ```bash
    export DJANGO_SETTINGS_MODULE=BudgetBridge.settings.local
    python manage.py runserver
    ```

9. **Start Celery worker (for background tasks):**
    ```bash
    celery -A BudgetBridge worker --loglevel=info
    ```

10. **Optional: Clean compiled Python files**
    ```bash
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -delete
    ```

11. **Access the app:**  
    Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

### Docker Setup

1. **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd BudgetBridge
    ```

2. **Ensure Docker and Docker Compose are installed.**

3. **Set up the ENV:**
      ```
    - Create a `.env` file in the root directory with the following:
      ```env
      SECRET_KEY=<your-secret-key>
      DEBUG=True
      POSTGRES_DB=budgetbridge_db
      POSTGRES_USER=budgetbridge_user
      POSTGRES_PASSWORD=12345678
      POSTGRES_HOST=db
      POSTGRES_PORT=5432
      REDIS_URL=redis://redis:6379/0

      # Email
      EMAIL_HOST_USER=
      EMAIL_HOST_PASSWORD=

      ```

4. **Build and start containers:**
    ```bash
    docker-compose up --build
    ```

    This will start:
    - Django app on [http://localhost:8000](http://localhost:8000)
    - PostgreSQL database container
    - Redis container
    - Celery worker (if configured in `docker-compose.yml`)

5. **Optional: Run Django management commands inside Docker:**
    ```bash
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py createsuperuser
    ```

6. **Stop containers:**
    ```bash
    docker-compose down
    ```
