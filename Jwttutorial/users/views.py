from django.shortcuts import get_object_or_404
from django.core.mail import send_mail ,EmailMessage
from django.conf import settings
from rest_framework.views import APIView # for class based view
from rest_framework.decorators import api_view, permission_classes # for function based view
from rest_framework.response import Response
from rest_framework import request, status
from .serializer import (
    EmailVerificationSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    ResendOtpSerializer,
    UserSerializer,
)
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny , IsAuthenticated
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.utils import timezone
import datetime


def create_verification_code(user):
    code = get_random_string(length=5, allowed_chars='0123456789')
    user.email_verification_code = make_password(code)
    user.email_verification_code_expires_at = timezone.now() + datetime.timedelta(minutes=10)
    user.save(update_fields=[
        'email_verification_code',
        'email_verification_code_expires_at',
    ])
    
    # send_mail(
    #     subject='Verify your email address',
    #     message=f'Your email verification code is {code}. It expires in 10 minutes.',
    #     from_email=settings.DEFAULT_FROM_EMAIL,
    #     recipient_list=[user.email],
    #     fail_silently=False,
    # )
    
    body = (
            f"Hello {user.username},\n\n"
            f"Your email verification code is {code}. \n\n"
            f"It expires in 10 minutes.\n"
            f"<{user.email}>.\n"
            
        )
    
    message = EmailMessage(
            subject="Verify your email address",
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
            reply_to=["support@example.com"],
        )
    
    message.esp_extra = {
            "category": "Verification",
            "custom_variables": {
                "user_id": str(user.id),
                "email_type": "Verify_emailAddress",
            },
        }
    
    message.send()


# Create your views here.
class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id='users_register_create',
        tags=['Authentication'],
        summary='Register a new user account',
        description=(
            'Creates a new user account and sends a **5-digit verification code** to the '
            'provided email address. The account remains **inactive** until the email is '
            'verified via the `/api/verify-email/` endpoint.\n\n'
            '**Required fields:** `username`, `email`, `password`\n\n'
            '**Optional fields:** `phone_number`\n\n'
            '**Password rules:** minimum 8 characters.'
        ),
        request=UserSerializer,
        responses={
            201: inline_serializer(
                name='RegisterResponse',
                fields={
                    'detail': serializers.CharField(
                        help_text='Success message confirming registration and email dispatch.'
                    ),
                },
            ),
            400: inline_serializer(
                name='RegisterErrorResponse',
                fields={
                    'username': serializers.ListField(
                        child=serializers.CharField(),
                        help_text='Validation errors for the username field.',
                        required=False,
                    ),
                    'email': serializers.ListField(
                        child=serializers.CharField(),
                        help_text='Validation errors for the email field.',
                        required=False,
                    ),
                    'password': serializers.ListField(
                        child=serializers.CharField(),
                        help_text='Validation errors for the password field.',
                        required=False,
                    ),
                    'phone_number': serializers.ListField(
                        child=serializers.CharField(),
                        help_text='Validation errors for the phone_number field.',
                        required=False,
                    ),
                },
            ),
        },
        examples=[
            OpenApiExample(
                name='Minimal registration (no phone)',
                summary='Register with username, email and password only',
                description='The most common registration payload — phone_number is optional.',
                value={
                    'username': 'john_doe',
                    'email': 'john@example.com',
                    'password': 'SecurePass123',
                },
                request_only=True,
            ),
            OpenApiExample(
                name='Full registration (with phone)',
                summary='Register including an optional phone number',
                value={
                    'username': 'jane_doe',
                    'email': 'jane@example.com',
                    'password': 'MyP@ssw0rd!',
                    'phone_number': '+201012345678',
                },
                request_only=True,
            ),
            OpenApiExample(
                name='201 – Registration successful',
                summary='Account created; verification email sent',
                value={
                    'detail': 'Registration successful. Check your email for the verification code.',
                },
                response_only=True,
                status_codes=['201'],
            ),
            OpenApiExample(
                name='400 – Email already exists',
                summary='Duplicate email address',
                value={'email': ['user with this email already exists.']},
                response_only=True,
                status_codes=['400'],
            ),
            OpenApiExample(
                name='400 – Password too short',
                summary='Password does not meet minimum length',
                value={'password': ['Ensure this field has at least 8 characters.']},
                response_only=True,
                status_codes=['400'],
            ),
        ],
        auth=[],
    )
    # def post(self, request):
    #     user_name = request.data.get('username')
    #     email = request.data.get('email')
    #     phone_number = request.data.get('phone_number')
    #     password = request.data.get('password')
    #     if not user_name or not email or not password: # phone optional
    #         return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)
    #     if User.objects.filter(email=email).exists():
    #         return Response({'error': 'email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    #     if phone_number is not None and User.objects.filter(phone_number=phone_number).exists():
    #         return Response({'error': 'Phone number already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    #     #TODO add a check to ensure phone is unique 
    #     user = User.objects.create_user(username=user_name, email=email, password=password, phone_number=phone_number)
    #     refresh = RefreshToken.for_user(user)
    #     serializer = UserSerializer(user)
    #     return Response({
    #         'msg': 'User registered successfully.',
    #         'user': serializer.data,
    #         'refresh': str(refresh),
    #         'access': str(refresh.access_token),
    #     }, status=status.HTTP_201_CREATED) #note: I have added a check to ensure that all required fields are provided and that the username is unique. If any of these checks fail, an appropriate error message is returned.
    #         #look how write response and status code in django rest framework. I have also added a message to indicate that the user was registered successfully.

    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(password=make_password(serializer.validated_data['password']))
            create_verification_code(user)
            return Response({
                'detail': 'Registration successful. Check your email for the verification code.',
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@extend_schema(
    operation_id='users_resend_otp_create',
    tags=['Authentication'],
    summary='Resend the email verification code',
    description=(
        'Send a fresh 5-digit verification code to an inactive account. '
        'The new code expires after 10 minutes. The response does not reveal '
        'whether an account exists or is already active.'
    ),
    request=ResendOtpSerializer,
    responses={
        200: inline_serializer(
            name='ResendOtpResponse',
            fields={'detail': serializers.CharField()},
        ),
        400: inline_serializer(
            name='ResendOtpValidationError',
            fields={
                'email': serializers.ListField(
                    child=serializers.CharField(),
                    required=False,
                ),
            },
        ),
    },
    auth=[],
)
def resend_otp(request):
    serializer = ResendOtpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = User.objects.filter(
        email__iexact=serializer.validated_data['email'],
        is_active=False,
    ).first()
    if user is not None:
        create_verification_code(user)

    return Response(
        {'detail': 'If the account is unverified, a new code has been sent.'},
        status=status.HTTP_200_OK,
    )

@api_view(['POST'])
@permission_classes([AllowAny])
@extend_schema(
    operation_id='users_verify_email_create',
    tags=['Authentication'],
    summary='Verify a user email address',
    description=(
        'Activates a new user account by validating the **5-digit numeric code** that was '
        'sent to the user\'s email after registration.\n\n'
        '**Flow:**\n'
        '1. User registers via `POST /api/register/`\n'
        '2. A 5-digit code is emailed to the user (valid for **10 minutes**)\n'
        '3. User submits their email + code here to activate the account\n\n'
        '**Notes:**\n'
        '- The code expires after 10 minutes — re-register if it expires.\n'
        '- Already-active accounts will return a 400 error.\n'
        '- The `code` field must be exactly 5 digits (e.g. `"04821"`).'
    ),
    request=EmailVerificationSerializer,
    responses={
        200: inline_serializer(
            name='EmailVerificationResponse',
            fields={
                'detail': serializers.CharField(
                    help_text='Confirmation that the email was verified and the account is now active.'
                ),
            },
        ),
        400: inline_serializer(
            name='EmailVerificationErrorResponse',
            fields={
                'detail': serializers.CharField(
                    help_text='Reason for failure: invalid code, expired code, or account already active.'
                ),
            },
        ),
    },
    examples=[
        OpenApiExample(
            name='Valid verification request',
            summary='Submit the 5-digit code received by email',
            value={
                'email': 'john@example.com',
                'code': '04821',
            },
            request_only=True,
        ),
        OpenApiExample(
            name='200 – Email verified',
            summary='Account successfully activated',
            value={'detail': 'Email verified successfully.'},
            response_only=True,
            status_codes=['200'],
        ),
        OpenApiExample(
            name='400 – Invalid or expired code',
            summary='Code is wrong or has expired',
            value={'detail': 'Invalid or expired verification code.'},
            response_only=True,
            status_codes=['400'],
        ),
        OpenApiExample(
            name='400 – Code format wrong',
            summary='Code must be exactly 5 digits',
            value={'code': ['This value does not match the required pattern.']},
            response_only=True,
            status_codes=['400'],
        ),
    ],
    auth=[],
)
def verify_email(request):
    serializer = EmailVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = User.objects.filter(email=serializer.validated_data['email']).first()
    if user is None or user.is_active:
        return Response(
            {'detail': 'Invalid or expired verification code.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    code_is_valid = check_password(
        serializer.validated_data['code'],
        user.email_verification_code,
    )
    code_is_expired = (
        user.email_verification_code_expires_at is None
        or user.email_verification_code_expires_at <= timezone.now()
    )
    if not code_is_valid or code_is_expired:
        return Response(
            {'detail': 'Invalid or expired verification code.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.is_active = True
    user.email_verification_code = ''
    user.email_verification_code_expires_at = None
    user.save(update_fields=[
        'is_active',
        'email_verification_code',
        'email_verification_code_expires_at',
    ])
    return Response({'detail': 'Email verified successfully.'}, status=status.HTTP_200_OK)


#NOTE: that not available 
@api_view(['POST'])
def register(request):
    #TODO: add url pattern for this view in urls.py 
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        return Response(
            {
                'message': 'User registered successfully',
                'user_id': user.id
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id='users_login_create',
        tags=['Authentication'],
        summary='Log in and obtain JWT tokens',
        description=(
            'Authenticates a user and returns a **JWT access token** and a **refresh token**.\n\n'
            'You must supply **either** `username` **or** `email` — not both.\n\n'
            '**Token lifetimes** (default drf-simplejwt settings):\n'
            '- `access` token: 5 minutes\n'
            '- `refresh` token: 1 day\n\n'
            '**Important:** The account must be active (email verified) before login is allowed. '
            'Inactive accounts receive a 401 with a descriptive message.\n\n'
            'Use the `access` token as a **Bearer token** in the `Authorization` header for '
            'protected endpoints:\n'
            '```\nAuthorization: Bearer <access_token>\n```'
        ),
        request=LoginSerializer,
        responses={
            200: inline_serializer(
                name='LoginResponse',
                fields={
                    'refresh': serializers.CharField(
                        help_text='JWT refresh token. Use this to obtain a new access token via /api/token/refresh/.'
                    ),
                    'access': serializers.CharField(
                        help_text='JWT access token. Pass this as a Bearer token in the Authorization header.'
                    ),
                },
            ),
            400: inline_serializer(
                name='LoginValidationErrorResponse',
                fields={
                    'username': serializers.ListField(
                        child=serializers.CharField(),
                        help_text='Returned when both username and email are provided, or neither is provided.',
                    ),
                },
            ),
            401: inline_serializer(
                name='LoginErrorResponse',
                fields={
                    'detail': serializers.CharField(
                        help_text='Authentication failure reason: wrong credentials or inactive account.'
                    ),
                },
            ),
        },
        examples=[
            OpenApiExample(
                name='Login with username',
                summary='Authenticate using a username',
                value={
                    'username': 'john_doe',
                    'password': 'SecurePass123',
                },
                request_only=True,
            ),
            OpenApiExample(
                name='Login with email',
                summary='Authenticate using an email address',
                value={
                    'email': 'john@example.com',
                    'password': 'SecurePass123',
                },
                request_only=True,
            ),
            OpenApiExample(
                name='200 – Login successful',
                summary='JWT tokens returned',
                value={
                    'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwMDAwMDAwMCwiaWF0IjoxNjk5OTEzNjAwLCJqdGkiOiJhYmMxMjMiLCJ1c2VyX2lkIjoiMTIzZTQ1NjctZTg5Yi0xMmQzLWE0NTYtNDI2NjE0MTc0MDAyIn0.signature',
                    'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk5OTE2NjAwLCJpYXQiOjE2OTk5MTM2MDAsImp0aSI6Inhjejk4NyIsInVzZXJfaWQiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDIifQ.signature',
                },
                response_only=True,
                status_codes=['200'],
            ),
            OpenApiExample(
                name='401 – Invalid credentials',
                summary='Wrong username/email or password',
                value={'detail': 'Invalid username/email or password.'},
                response_only=True,
                status_codes=['401'],
            ),
            OpenApiExample(
                name='401 – Account not verified',
                summary='Email not yet verified',
                value={'detail': 'Account is inactive. Verify your email before logging in.'},
                response_only=True,
                status_codes=['401'],
            ),
            OpenApiExample(
                name='400 – Both username and email provided',
                summary='Only one identifier is allowed',
                value={'username': ['Provide either a username or an email address.']},
                response_only=True,
                status_codes=['400'],
            ),
        ],
        auth=[],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        refresh = RefreshToken.for_user(serializer.validated_data['user'])
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(
    operation_id='users_current_retrieve',
    tags=['User'],
    summary='Get the currently authenticated user',
    description=(
        'Returns the profile data of the user who owns the **JWT access token** '
        'supplied in the `Authorization` header.\n\n'
        '**Authentication:** Bearer token required.\n\n'
        '**Returned fields:** `username`, `email`, `phone_number`.\n\n'
        'Use this endpoint to populate a "My Profile" page or to verify that a '
        'token is still valid.'
    ),
    parameters=[
        OpenApiParameter(
            name='Authorization',
            location=OpenApiParameter.HEADER,
            required=True,
            type=OpenApiTypes.STR,
            description='JWT Bearer token. Format: `Bearer <access_token>`',
            examples=[
                OpenApiExample(
                    name='Bearer token header',
                    value='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                ),
            ],
        ),
    ],
    responses={
        200: UserSerializer,
        401: inline_serializer(
            name='CurrentUserUnauthorizedResponse',
            fields={
                'detail': serializers.CharField(
                    help_text='Authentication credentials were not provided or the token is invalid/expired.'
                ),
            },
        ),
    },
    examples=[
        OpenApiExample(
            name='200 – Current user profile',
            summary='Authenticated user data',
            value={
                'username': 'john_doe',
                'email': 'john@example.com',
                'phone_number': '+201012345678',
            },
            response_only=True,
            status_codes=['200'],
        ),
        OpenApiExample(
            name='401 – Missing or invalid token',
            summary='No valid Bearer token provided',
            value={'detail': 'Authentication credentials were not provided.'},
            response_only=True,
            status_codes=['401'],
        ),
    ],
)
def current_user(request):
    
    user = UserSerializer(request.user, many=False)
    return Response(user.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user
    data = request.data
    user.username = data['username']
    user.email = data['email']

    if data['password'] != "":
        user.password =  make_password(data['password'])

    user.save()
    serializer = UserSerializer(user,many=False)
    return Response(serializer.data)


def get_current_host(request):
    protocol = request.is_secure() and 'https' or 'http'
    host = request.get_host()
    return "{protocol}://{host}/".format(protocol=protocol, host=host)


@api_view(['POST'])
@extend_schema(
    operation_id='forgot_password',
    tags=['Password Reset'],
    summary='Request a password reset link',
    description=(
        'Sends a **password reset link** to the registered email address.\n\n'
        'The link contains a unique 40-character token and is valid for **30 minutes**. '
        'After expiry the token is unusable and a new request must be made.\n\n'
        '**Flow:**\n'
        '1. POST the registered `email` here\n'
        '2. An email is sent with a link like: `http://<host>/api/reset_password/<token>`\n'
        '3. Submit the token + new password to `POST /api/reset_password/<token>`\n\n'
        '**Note:** Returns 404 if the email is not registered.'
    ),
    request=inline_serializer(
        name='ForgotPasswordRequest',
        fields={
            'email': serializers.EmailField(
                help_text='The email address associated with the account that needs a password reset.'
            ),
        },
    ),
    responses={
        200: inline_serializer(
            name='ForgotPasswordResponse',
            fields={
                'details': serializers.CharField(
                    help_text='Confirmation that the reset email was dispatched.'
                ),
            },
        ),
        404: inline_serializer(
            name='ForgotPasswordNotFoundResponse',
            fields={
                'detail': serializers.CharField(
                    help_text='No user account found with the provided email address.'
                ),
            },
        ),
    },
    examples=[
        OpenApiExample(
            name='Forgot password request',
            summary='Submit the registered email address',
            value={'email': 'john@example.com'},
            request_only=True,
        ),
        OpenApiExample(
            name='200 – Reset email sent',
            summary='Email dispatched successfully',
            value={'details': 'Password reset sent to john@example.com'},
            response_only=True,
            status_codes=['200'],
        ),
        OpenApiExample(
            name='404 – Email not found',
            summary='No account with that email',
            value={'detail': 'No User matches the given query.'},
            response_only=True,
            status_codes=['404'],
        ),
    ],
    auth=[],
)
def forgot_password(request):

    data = request.data
    user = get_object_or_404(User,email=data['email'])
    token = get_random_string(40)
    expire_date = timezone.now() + datetime.timedelta(minutes  =30)
    user.profile.reset_password_token = token
    user.profile.reset_password_expire = expire_date
    user.profile.save()
    
    # host = get_current_host(request)
    # link = "{host}/api/reset_password/{token}".format(token=token, host=host)
    # link = "http://localhost:8000/api/reset_password/{token}".format(token=token)
    # body = "Your password reset link is : {link}".format(link=link)

    # link = request.build_absolute_uri(
    # f"/api/reset_password/{token}"    
    # )
    # body = f"Your password reset link is: {link}"

    # send_mail(
    #     "Password reset from locallink",
    #     body,
    #     settings.DEFAULT_FROM_EMAIL,
    #     [data['email']]
    # )


    # Then send your email, e.g. from a view
    #? بدل ال get host ب request.build_absolute_uri() عشان يجيب ال host من ال request نفسه بدل ما يكون ثابت
    link = request.build_absolute_uri(
        f"/api/reset_password/{token}"
    )

    body = (
        f"Hello {user.username},\n\n"
        f"You requested to reset your password.\n\n"
        f"Click the link below to reset your password:\n"
        f"{link}\n\n"
        f"This link expires in 30 minutes."
    )

    message = EmailMessage(
        subject="Password Reset - locallink ",
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
        reply_to=["support@example.com"],
    )

    message.esp_extra = {
        "category": "Password Reset",
        "custom_variables": {
            "user_id": str(user.id),
            "email_type": "password_reset",
        },
    }

    message.send()


    
    return Response({'details': 'Password reset sent to {email}'.format(email=data['email'])})



@api_view(['POST'])
@extend_schema(
    operation_id='reset_password',
    tags=['Password Reset'],
    summary='Reset user password using a reset token',
    description=(
        'Sets a new password for the user identified by the **reset token** in the URL path.\n\n'
        'The token is obtained from the password-reset email sent by `POST /api/forgot_password/`.\n\n'
        '**URL path parameter:** `token` — the 40-character reset token from the email link.\n\n'
        '**Body parameters:**\n'
        '- `password` — the new password (minimum 8 characters)\n'
        '- `confirmPassword` — must match `password` exactly\n\n'
        '**Token rules:**\n'
        '- Valid for **30 minutes** from the time the reset email was sent\n'
        '- Single-use: the token is cleared after a successful reset\n\n'
        '**Returns 400** if the token is expired or the passwords do not match.\n'
        '**Returns 404** if the token does not match any user.'
    ),
    parameters=[
        OpenApiParameter(
            name='token',
            location=OpenApiParameter.PATH,
            required=True,
            type=OpenApiTypes.STR,
            description='The 40-character password reset token received in the reset email.',
            examples=[
                OpenApiExample(
                    name='Example token',
                    value='a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0',
                ),
            ],
        ),
    ],
    request=inline_serializer(
        name='ResetPasswordRequest',
        fields={
            'password': serializers.CharField(
                min_length=8,
                help_text='The new password. Must be at least 8 characters long.',
            ),
            'confirmPassword': serializers.CharField(
                min_length=8,
                help_text='Must exactly match the `password` field.',
            ),
        },
    ),
    responses={
        200: inline_serializer(
            name='ResetPasswordResponse',
            fields={
                'details': serializers.CharField(
                    help_text='Confirmation that the password was reset successfully.'
                ),
            },
        ),
        400: inline_serializer(
            name='ResetPasswordErrorResponse',
            fields={
                'error': serializers.CharField(
                    help_text='Reason for failure: expired token or mismatched passwords.'
                ),
            },
        ),
        404: inline_serializer(
            name='ResetPasswordNotFoundResponse',
            fields={
                'detail': serializers.CharField(
                    help_text='No user found with the provided reset token.'
                ),
            },
        ),
    },
    examples=[
        OpenApiExample(
            name='Valid reset request',
            summary='Submit matching passwords with a valid token',
            value={
                'password': 'NewSecurePass99!',
                'confirmPassword': 'NewSecurePass99!',
            },
            request_only=True,
        ),
        OpenApiExample(
            name='200 – Password reset successful',
            summary='Password updated',
            value={'details': 'Password reset done '},
            response_only=True,
            status_codes=['200'],
        ),
        OpenApiExample(
            name='400 – Token expired',
            summary='The reset token has passed its 30-minute window',
            value={'error': 'Token is expired'},
            response_only=True,
            status_codes=['400'],
        ),
        OpenApiExample(
            name='400 – Passwords do not match',
            summary='password and confirmPassword are different',
            value={'error': 'Password are not same'},
            response_only=True,
            status_codes=['400'],
        ),
        OpenApiExample(
            name='404 – Token not found',
            summary='No user matches this reset token',
            value={'detail': 'No User matches the given query.'},
            response_only=True,
            status_codes=['404'],
        ),
    ],
    auth=[],
)
def reset_password(request,token):
    data = request.data
    user = get_object_or_404(User,profile__reset_password_token = token)
    #? compare the expire date with the current date and time to check if the token is expired or not
    if user.profile.reset_password_expire < timezone.now():
        return Response({'error': 'Token is expired'},status=status.HTTP_400_BAD_REQUEST)
    
    if data['password'] != data['confirmPassword']:
        return Response({'error': 'Password are not same'},status=status.HTTP_400_BAD_REQUEST)
    #! لازم يعدي على سيليزي علشان يتاكد من باسورد هيتخزن صح و يطبق ال validation rules بتاعته
    #? اظن كدانا اتخليت عن مبدا dRY علشان كررت في validate_password و make_password في ال register view و reset password view. ممكن اعمل function helper عشان اعمل validate و make password و ارجع ال user object بعد ما اعمله save.
    # try:
    #     validate_password(data['password'], user)
    # except ValidationError:
    #     return Response({'error': 'Password is not valid'},status=status.HTTP_400_BAD_REQUEST)
    serializer = ResetPasswordSerializer(data={'new_password': data['password']})
    serializer.is_valid(raise_exception=True)

    new_password = serializer.validated_data["new_password"]
    user.password = make_password(new_password)
    # user.set_password(new_password)
    user.save()
    user.profile.reset_password_token = ""
    user.profile.reset_password_expire = None 
    user.profile.save() 
    user.save()
    return Response({'details': 'Password reset done '})
