# Login API project guide

## What this project does

This project is a Django REST Framework API for user accounts. It supports account
registration, email verification with a one-time code (OTP), JWT login, protected
profile access, and password reset by email.

The main technologies are:

- Django
- Django REST Framework
- Simple JWT for access and refresh tokens
- drf-spectacular for OpenAPI documentation
- Mailtrap through django-anymail for email delivery
- SQLite for the development database

## Project layout

```text
Jwttutorial/
|-- manage.py
|-- mysite/
|   |-- settings.py
|   `-- urls.py
`-- users/
    |-- models.py
    |-- serializer.py
    |-- views.py
    |-- urls.py
    |-- tests.py
    `-- migrations/
```

The root `requirements.txt` contains the Python dependencies. `mysite/settings.py`
contains the Django, database, email, JWT, and API documentation settings.

## Run the project locally

From the repository root in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\requirements.txt
Set-Location .\Jwttutorial
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

### Email configuration

Email delivery is configured through Mailtrap. The settings read these environment
variables:

```text
MAILTRAP_API_TOKEN=your_mailtrap_api_token
MAILTRAP_SANDBOX_ID=your_mailtrap_sandbox_id
EMAIL_HOST_USER=your_email_host_user
EMAIL_HOST_PASSWORD=your_email_host_password
```

Provide real values in a local environment file, such as `Jwttutorial\.env.var`.
Do not commit credentials or tokens to source control. The registration, resend
code, and password-reset flows require working email configuration.

## Account and verification flow

1. Send `POST /api/register/` with a username, email, and password.
2. The account is created as inactive. A five-digit code is emailed to the user.
   The code is stored as a hash and expires after 10 minutes.
3. Send `POST /api/verify-email/` with the email and code. A valid code activates
   the account.
4. If the code expires, send `POST /api/resend_otp/` with the email address to
   request a fresh code.
5. After verification, log in through `POST /api/login/`.

Inactive accounts cannot log in. The resend endpoint returns the same response
whether an account exists or is already active, so it does not confirm account
existence.

## API endpoints

All user endpoints begin with `/api/`.

| Method | Endpoint | Purpose | Authentication |
|---|---|---|---|
| `POST` | `/api/register/` | Create an inactive account and email an OTP | Not required |
| `POST` | `/api/verify-email/` | Verify the OTP and activate the account | Not required |
| `POST` | `/api/resend_otp/` | Email a fresh OTP to an inactive account | Not required |
| `POST` | `/api/login/` | Log in with a username or email and receive JWTs | Not required |
| `GET` | `/api/userinfo/` | Get the current user's profile | Bearer access token |
| `POST` | `/api/forgot_password/` | Email a password-reset link | Not required |
| `POST` | `/api/reset_password/<token>` | Set a new password using a reset token | Not required |
| `POST` | `/api/token/` | Obtain a token using the Simple JWT endpoint | Not required |
| `POST` | `/api/token/refresh/` | Get a new access token from a refresh token | Refresh token |
| `GET` | `/api/schema/` | Get the OpenAPI schema | Not required |
| `GET` | `/api/docs/` | Open the Swagger UI | Not required |

### Register

`POST /api/register/`

Required JSON fields are `username`, `email`, and `password`. `phone_number` is
optional. The password must be at least eight characters long.

```json
{
  "username": "jane_doe",
  "email": "jane@example.com",
  "password": "ExamplePass123!"
}
```

The response confirms registration and email delivery. It does not contain login
tokens; verify the email first.

### Verify an email

`POST /api/verify-email/`

```json
{
  "email": "jane@example.com",
  "code": "04821"
}
```

The code must be a string of exactly five digits. A successful response activates
the account and clears the stored verification code.

### Resend an OTP

`POST /api/resend_otp/`

```json
{
  "email": "jane@example.com"
}
```

The endpoint sends a new code only when the email belongs to an inactive account.
Its response is intentionally generic regardless of whether an email was sent.

### Log in

`POST /api/login/`

Provide exactly one identifier: either `username` or `email`, along with
`password`.

```json
{
  "email": "jane@example.com",
  "password": "ExamplePass123!"
}
```

A successful login returns `access` and `refresh` tokens. Use the access token
for protected API requests:

```http
Authorization: Bearer <access_token>
```

### Get the current user's profile

`GET /api/userinfo/` requires a valid access token and returns the signed-in
user's username, email, and phone number.

### Reset a password

1. Send `POST /api/forgot_password/` with the registered email address.
2. Follow the reset link sent to that email. The token is valid for 30 minutes.
3. Send `POST /api/reset_password/<token>` with matching `password` and
   `confirmPassword` values.

Example request body:

```json
{
  "password": "NewExamplePass123!",
  "confirmPassword": "NewExamplePass123!"
}
```

## Data models

### User

The custom `User` model extends Django's `AbstractUser` and includes:

- A UUID primary key
- A unique email address
- An optional, unique phone number
- A role: customer, provider, or admin
- An `is_active` flag, which is false for new registrations until email
  verification succeeds
- A hashed email-verification code and its expiry time

### Profile

Each user has a related `Profile`, created automatically when the user is created.
It stores the password-reset token and its expiry time.

## JWT token settings

The current settings configure access tokens to last **5 days** and refresh tokens
to last **2 days**. The login endpoint's OpenAPI description currently lists
different lifetimes, so treat `mysite/settings.py` as the source of truth until
those descriptions are updated.

## Run tests

From the `Jwttutorial` directory:

```powershell
python manage.py test users
```

## Development and deployment notes

The checked-in settings are for development. Before deploying publicly:

- Set `DEBUG` to `False` and restrict `ALLOWED_HOSTS`.
- Load `SECRET_KEY` from a secret environment variable instead of keeping it in
  `settings.py`.
- Configure email credentials securely and use the correct TLS settings for the
  email provider.
- Review token lifetimes, password-reset behavior, and API throttling for the
  needs of the deployment.

The legacy `register` function and `update_user` function are not currently
connected to routes in `users/urls.py`.
