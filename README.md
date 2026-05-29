# Resource Allocation System

A Django-based web application for managing emergency resource distribution across districts, volunteers, staff, and citizens.

## Project Summary

This project provides a complete emergency resource allocation platform built with Django. It helps administrators, district staff, volunteers, and citizens coordinate aid requests and manage essential inventory during crises.

## Main Features

- Admin can manage districts, resource categories, staff, and volunteer approvals.
- Staff can manage resource stock, review resource requests, and oversee local logistics.
- Volunteers can view assigned missions and update delivery status.
- Citizens can submit emergency resource requests and track request progress.
- Includes authentication, role-based dashboards, and integrated data management.

## Technology Stack

- Python 3
- Django
- SQLite3
- HTML, CSS, JavaScript

## Repository Structure

- `public/`: Django project root
- `public/myapp/`: main application containing models, views, and migrations
- `public/public/`: project settings, URLs, and WSGI/ASGI configuration
- `public/templates/`: HTML templates for different user roles
- `public/static/`: static assets for the frontend

## Getting Started

1. Clone the repository.
2. Create a virtual environment and install dependencies from `public/requirements.txt`.
3. Run Django migrations.
4. Start the development server.

Example commands:

```bash
cd public
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Notes

- The project already contains a detailed application-level README at `public/README.md`.
- Use the Django development server to explore the admin, citizen, staff, and volunteer functionality.
