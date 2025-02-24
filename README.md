# AnimeHub

AnimeHub is a platform for managing and tracking anime and series.

## Features
- User registration and authentication
- Managing a list of titles (adding, deleting, editing)
- Updating information about watched episodes
- IP-based request limiting using Nginx
- Request logging with request ID
- Deployment via Docker
- Testing with pytest

## Technologies Used
- **Programming Language**: Python 3.11
- **Web Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy + Alembic
- **Nginx**
- **Containerization**: Docker
- **Testing**: pytest

## Installation and Running

### 1. Clone the Repository
```sh
git clone https://github.com/kyofu95/animehub
cd animehub
```

### 2. Configure Environment Variables
Create a `.env` file and specify the necessary variables (example in `.env.sample`).

### 3. Run with Docker
For the production version:
```sh
docker compose --env-file .env -f docker-compose.yml up --build 
```
For development:
```sh
docker compose --env-file .env -f docker-compose.dev.yml up --build 
```

### 4. API Access
After launching, the server will be available at:
```
http://localhost:80/docs
```

### 5. Running Tests
```sh
pytest tests
```
