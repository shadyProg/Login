from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    LoginView,
    RegisterView,
    current_user,
    forgot_password,
    reset_password,
    verify_email,
    resend_otp,
)


app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', verify_email, name='verify_email'),
    path('resend_otp/', resend_otp, name='resend_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('userinfo/', current_user,name='user_info'), 
    #path('userinfo/update/', update_user,name='update_user'), 
    
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forgot_password/', forgot_password,name='forgot_password'), 
    path('reset_password/<str:token>', reset_password,name='reset_password'),
]  