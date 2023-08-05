from rest_framework import response
from rest_framework.permissions import IsAuthenticated
from tabula_auth.serializers import *
from rest_framework.generics import CreateAPIView, RetrieveAPIView, DestroyAPIView
from tabula_auth.models import PhoneNumberUser

__all__ = ['UserView', 'AcceptTerms', 'GDPRView']


class UserView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserRetrieveSerializer
    queryset = PhoneNumberUser.objects.all()

    def retrieve(self, request, *args, **kwargs):
        ser = UserRetrieveSerializer(request.user)
        return response.Response(ser.data, status=200)


class AcceptTerms(CreateAPIView):
    """
    Подтвердить правила пользования
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = AcceptTermsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        accept_terms_value = serializer.data['accept_terms']
        request.user.accept_terms = accept_terms_value
        request.user.save()
        return response.Response(
            UserRetrieveSerializer(request.user).data, status=202)


class GDPRView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = PhoneNumberUser.objects.all()

    def destroy(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return response.Response({'status': 'ok'}, status=200)
