# FileHub

A simple cloud based file storage platform.

## Installation

- Clone the repository.
- For object storage, we have used a locally hosted single node instance of [MinIO](https://min.io/).
  - MinIO is fully compatible with AWS S3, thus is easily swappable if required.
- Create and activate a python virtual environment:
  - Linux/macOS: `$ python3 -m venv .venv && source .venv/bin/activate`
  - Windows: `$ python -m venv .venv && .venv\Scripts\activate.bat`
- Install dependencies:
  `$ pip install -r requirements.txt`
- Install git hook scripts:
  `$ pre-commit install`
- Run migrations:
  `$ python manage.py migrate`
- (Optional) Create a superuser to access the admin site:
  `$ python manage.py createsuperuser`
- Run the webserver:
  `$ python manage.py runserver`

## Troubleshooting

- Check if you are using the correct python version. Recommended versions include 3.10 and higher (CPython implementation)
- If you use a proxy server, make sure to exclude your private IP addresses (for both django and MinIO) to avoid any
  protocol hassle.
