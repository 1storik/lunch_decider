# Lunch Decider

## Requirements
- Docker
- Docker Compose
- Python 3.9

## Installation

1. **Clone the repository:**
   ```bash
   git clone <URL_вашего_репозитория>
   cd lunch_decider

2. **Build and run containers:**
   ```bash
   docker-compose up --build

3. **To run tests, use the command:**
   ```bash
   docker-compose exec web pytest

4. **Database migrations:**
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser