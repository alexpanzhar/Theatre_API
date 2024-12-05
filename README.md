# Theatre_API

This is a Django-based API for managing a theatre system. It provides endpoints to manage theatres, plays and users,
supporting actions like CRUD operations for each entity.

## Features

- **Play Management**: Create, update, delete, and retrieve play details.
- **Performances Management**: Manage performances, assign movies, and more.
- **User Authentication**: Handle user login, registration, and permissions.
- **Dockerized**: The project is Dockerized for easier deployment.

## Installation

### Prerequisites:

- Python 3.x
- PostgreSQL (for local setup)
- Docker (optional for containerized setup)

### Local Setup:

1. Clone this repository:
   ```bash
   git clone https://github.com/alexpanzhar/Theatre_API.git
   cd Theatre_API

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows, use `venv\Scripts\activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt


4. Create a .env file in the project root with the following content:
   ```bash
   echo -e "SECRET_KEY=test_secret_key\nDEBUG=True\nPOSTGRES_PASSWORD=theatre\nPOSTGRES_USER=theatre\nPOSTGRES_DB=theatre\nPOSTGRES_HOST=localhost\nPOSTGRES_PORT=5432\nPGDATA=/var/lib/postgresql/data" > .env

5. Run migrations:
   ```bash
   python manage.py migrate

6. Start the development server:
   ```bash
   python manage.py runserver

#### IMPORTANT:

The PostgreSQL service must be locally installed and
running for the application to function correctly.
Ensure that your database container or local installation
is set up with the correct configurations specified in the `.env`
file before starting the project.

### Docker Setup:

1. Create a .env file in the project root with the following content:
   ```bash
   echo -e "SECRET_KEY=test_secret_key\nDEBUG=True\nPOSTGRES_PASSWORD=theatre\nPOSTGRES_USER=theatre\nPOSTGRES_DB=theatre\nPOSTGRES_HOST=db\nPOSTGRES_PORT=5432\nPGDATA=/var/lib/postgresql/data" > .env

2. Build the Docker image:
   ```bash
   docker-compose build

3. Run the container:
   ```bash
   docker-compose up
