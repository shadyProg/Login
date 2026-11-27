# Login-REST API Django base.


## Forgot Password & Password Reset

### Description
Implemented the Forgot Password and Reset Password functionality to allow users to securely recover access to their accounts.

### Features
- Added Forgot Password endpoint.
- Added secure password reset token generation.
- Implemented token expiration to prevent reuse of expired links.
- Added email delivery integration using Django Anymail and Mailtrap.
- Added Reset Password endpoint with token validation.
- Added password validation before updating user credentials.
- Handled invalid, expired, and already-used reset tokens.
- Added API documentation using `drf-spectacular`.

### Security
- Prevents password resets using invalid or expired tokens.
- Ensures reset tokens cannot be reused.
- Validates new passwords before saving.
- Protects against user enumeration through consistent responses.

### Testing
- Tested successful password reset flow.
- Tested invalid and expired tokens.
- Tested password validation and error responses.

### Result
Users can now securely reset their passwords through the email-based recovery flow.
