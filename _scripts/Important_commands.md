# Important Commands

## Django Commands

- `django-admin startproject <project_name>` : Creates a new Django project.
- `django-admin startapp <app_name>` : Creates a new Django application within the project.
- `python manage.py runserver` : Starts the Django development server.
- `python manage.py makemigrations` : Creates new migrations based on the changes detected to your models.
- `python manage.py migrate` : Applies database migrations.
- `python manage.py createsuperuser` : Creates a new superuser account for the admin site.
- `python manage.py test` : Runs the test suite for your Django application.

## Deployment Commands
- `uv sync`: Installs dependencies from the `pyproject.toml` file using the 'uv' tool.
- `uv run python manage.py migrate` : Applies database migrations using the 'uv' tool.
- `uv run gunicorn network.wsgi:application --bind 0.0.0.0:$PORT` : Command to run the Django application using Gunicorn server.
- `uv run python manage.py collectstatic --noinput` : Collects static files for deployment using the 'uv' tool.

Build: 
```bash
uv sync && uv run python manage.py migrate && uv run python manage.py collectstatic --noinput
```

Start:
```bash
uv run gunicorn network.wsgi:application --bind 0.0.0.0:$PORT
```