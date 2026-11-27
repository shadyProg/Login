from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email' , 'password' , 'phone_number' )
        extra_kwargs = {

        'username': {'required':True ,'allow_blank':False}, # required for must full  
        'email' : {'required':True ,'allow_blank':False }, # unique for email
        'password' : {'required':True ,'allow_blank':False,'min_length':8},
        'phone_number' : {'required':False ,}, # unique for phone number
        

        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=False,
        help_text='Username or email address',
        trim_whitespace=True,
    )
    email = serializers.EmailField(required=False, write_only=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        if bool(username) == bool(email):
            raise serializers.ValidationError(
                {'username': 'Provide either a username or an email address.'}
            )

        identifier = username or email
        request = self.context.get('request')
        user = User.objects.filter(username=identifier).first()

        if user is None:
            email_matches = list(User.objects.filter(email__iexact=identifier)[:2])
            if len(email_matches) == 1:
                user = email_matches[0]

        if user is not None:
            if not user.is_active:
                raise AuthenticationFailed(
                    'Account is inactive. Verify your email before logging in.'
                )
            user = authenticate(
                request=request,
                username=user.get_username(),
                password=attrs['password'],
            )
        else:
            authenticate(
                request=request,
                username=identifier,
                password=attrs['password'],
            )

        if user is None:
            raise AuthenticationFailed('Invalid username/email or password.')

        attrs['user'] = user
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.RegexField(regex=r'^\d{5}$')


class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()


def validate_password_length(password):
    if len(password) < 8:
        return False

    return True

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    
    def validate_new_password(self, value):
        if not validate_password_length(value):
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )

        return value
# class ResetPasswordSerializer(serializers.Serializer):
#     new_password = serializers.CharField(min_length=8)