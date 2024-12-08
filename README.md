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
file before starting the project. The example can be find in `example.env`

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

## Managing access

Use the following command to load prepared data from fixture:
  `python manage.py loaddata theatre_db_data.json`.

After loading data from fixture you can use:
1. Following superuser (or create another one by yourself):

- E-mail: `admin.user@theatre.com`
- Password: `admin`

2. Following user (or create another using  `api/user/register/` endpoint):
- E-mail: `user_1@theatre.com`
- Password: `user_1`

For getting access and refresh tokens, follow `/api/user/token` endpoint

## API Endpoints
API provides different endpoints for managing Genres, Actors, Theatre Halls, Performances, Plays and Reservations. 
Follow `api/schema/swagger-ui/` or `api/schema/redoc/` to see
and manipulate with all endpoint.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.