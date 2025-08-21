# Deployment

The Dog Booking System was deployed to **Heroku** using **GitHub** and managed locally using **VSCode**.

- Live app: [https://dog-booking-system-1eebcb797de9.herokuapp.com/](https://dog-booking-system-1eebcb797de9.herokuapp.com/)
- GitHub repo: [https://github.com/Kerem-Haeger/dog_booking_system](https://github.com/Kerem-Haeger/dog_booking_system)

---

## Local Deployment (VSCode)

To run this project locally:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Kerem-Haeger/dog_booking_system.git
    ```

2. **Navigate into the project folder:**

    ```bash
    cd dog_booking_system
    ```

3. **Create a virtual environment:**

    ```bash
    python -m venv .venv
    .venv/Scripts/activate  # Windows
    source .venv/bin/activate  # macOS/Linux
    ```

4. **Install requirements:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Create a `.env` file** in the root directory and add:

    ```python
    import os

    os.environ['SECRET_KEY'] = 'your-secret-key'
    os.environ['DATABASE_URL'] = 'your-database-url'
    os.environ['DEBUG'] = 'True'
    ```

6. **Apply migrations:**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

7. **Create a superuser:**

    ```bash
    python manage.py createsuperuser
    ```

8. **Run the app locally:**

    ```bash
    python manage.py runserver
    ```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser to view the app.

---

## Heroku Deployment

### Prerequisites

- A Heroku account
- GitHub account with the repo linked

### Heroku Configuration via Web Dashboard

1. Go to [Heroku Dashboard](https://dashboard.heroku.com/) and select your deployed app.

2. Navigate to the **Settings** tab.

3. Click on **"Reveal Config Vars"**.

4. Add the following environment variables:

| Key            | Value                | Notes                                                  |
|----------------|----------------------|--------------------------------------------------------|
| `DATABASE_URL` | *from ElephantSQL*   | Copy from your ElephantSQL instance                    |
| `SECRET_KEY`   | *your Django secret* | Use [Djecrety](https://djecrety.ir/) to generate       |
| `DEBUG`        | `False`              | Important for production security 

5. Create a Procfile in your local workplace:
`web: gunicorn <name app>.wsgi:application`

6. You do **not** need to add `DISABLE_COLLECTSTATIC` unless your static files are not ready.

7. Ensure the same variables are also defined in your local `.env` file for consistency.

---

## Notes

- `ALLOWED_HOSTS` in `settings.py` includes `RENDER_EXTERNAL_HOSTNAME` and `herokuapp.com` domains.
- `collectstatic` was used to gather static files for production.
- ElephantSQL was used as the hosted PostgreSQL database provider.
- Email support and other environment variables can be added later if needed.

---

This deployment method ensures smooth project delivery using Heroku and GitHub from within VSCode.