import datetime
import token
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail ,EmailMessage
from django.conf import settings
from rest_framework.views import APIView # for class based view
from rest_framework.decorators import api_view, permission_classes # for function based view
from rest_framework.response import Response
from rest_framework import request, status
from .serializer import LoginSerializer, UserSerializer
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny , IsAuthenticated
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta


# Create your views here.
class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id='users_register_create',
        tags=['Authentication'],
        summary='Register a user',
        request=UserSerializer,
        responses={
            201: inline_serializer(
                name='RegisterResponse',
                fields={
                    'msg': serializers.CharField(),
                    'user': UserSerializer(read_only=True),
                    'refresh': serializers.CharField(),
                    'access': serializers.CharField(),
                },
            ),
            400: inline_serializer(
                name='RegisterErrorResponse',
                fields={'error': serializers.CharField()},
            ),
        },
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
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        summary='Log in with a username or email',
        request=LoginSerializer,
        responses={
            200: inline_serializer(
                name='LoginResponse',
                fields={
                    'refresh': serializers.CharField(),
                    'access': serializers.CharField(),
                },
            ),
            400: inline_serializer(
                name='LoginValidationErrorResponse',
                fields={'username': serializers.ListField(child=serializers.CharField())},
            ),
            401: inline_serializer(
                name='LoginErrorResponse',
                fields={'detail': serializers.CharField()},
            ),
        },
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
        tags=['Authentication'],
        summary='Get current user',
        request=UserSerializer,
        responses={
            200: inline_serializer(
                name='CurrentUserResponse',
                fields={
                    'user': UserSerializer(read_only=True),
                },
            ),
            400: inline_serializer(
                name='RegisterErrorResponse',
                fields={'error': serializers.CharField()},
            ),
        },
        auth=[],
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



# @api_view(['POST'])
# def reset_password(request,token):
#     data = request.data
#     user = get_object_or_404(User,profile__reset_password_token = token)

    #     if user.profile.reset_password_expire < timezone.now():
#         return Response({'error': 'Token is expired'},status=status.HTTP_400_BAD_REQUEST)
    
#     if data['password'] != data['confirmPassword']:
#         return Response({'error': 'Password are not same'},status=status.HTTP_400_BAD_REQUEST)
    
#     user.password = make_password(data['password'])
#     user.profile.reset_password_token = ""
#     user.profile.reset_password_expire = None 
#     user.profile.save() 
#     user.save()
#     return Response({'details': 'Password reset done '})
