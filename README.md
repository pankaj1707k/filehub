# FileHub

A simple cloud based file storage platform.

## Installation

- Clone the repository.
- For object storage, we have used a locally hosted single node instance of [MinIO](https://min.io/).
  - MinIO is fully compatible with AWS S3, thus is easily swappable if required.
- Create and activate a python virtual environment:
  - Linux/macOS: `$ python3 -m venv .venv && source .venv/bin/activate`
  - Windows (Powershell): `$ python -m venv .venv && .venv\Scripts\activate`
- Install dependencies:
  `$ pip install -r requirements.txt`
- Install git hook scripts:
  `$ pre-commit install`
- Navigate to `src` directory and create a `.env` file to setup the required environment variables,
  provided in `.env.dist` file.
- Run migrations:
  `$ python manage.py migrate`
- (Optional) Create a superuser to access the admin site:
  `$ python manage.py createsuperuser`
- Run the webserver:
  `$ python manage.py runserver`

## Troubleshooting

- Check if you are using the correct python version. Recommended versions include 3.10 and higher (CPython implementation)
- If the virtual environment setup command for Windows does not run on the _Windows Powershell_,
  consider the following variations:
  - Split the command on `&&` and run them separately.
  - On `cmd`, for the second part of the command, try: `$ .venv\Scripts\activate.bat`
- If email communication is not working, check if you have configured:
  - Email used has the domain `gmail.com`
  - Two-factor authentication is enabled on your Google account.
  - You are using a valid **App Password** generated from your Google account.
  - Email port (587) not blocked by firewall.
- If you use a proxy server, make sure to exclude your private IP addresses (for both django and MinIO) to avoid any protocol hassle.
