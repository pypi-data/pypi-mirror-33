from django.urls import path, include
from rest_framework import routers
from tabula_auth.views import *
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token, obtain_jwt_token
from rest_framework.authtoken import views as rest_framework_views

router = routers.DefaultRouter()
router.register('user', viewset=UserView, base_name='user')
urlpatterns = [
    path('generate/', GenerateOTP.as_view(), name="generate"),
    path('validate/', ValidateOTP.as_view(), name="validate"),
    path('user/', UserView.as_view(), name="user"),
    path('accept_terms/', AcceptTerms.as_view(), name="accept_terms"),
    path('gdpr/', GDPRView.as_view(), name="gdpr"),
    path('api-token-refresh/', refresh_jwt_token),
    path('api-token-verify/', verify_jwt_token),
    path('jwt-login/', obtain_jwt_token, name='login'),
    path('base-login/', rest_framework_views.obtain_auth_token, name='login'),

]
