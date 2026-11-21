from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email' , 'password' , 'phone_number' )


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