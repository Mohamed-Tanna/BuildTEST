from django.shortcuts import render


from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from authentication.models import AppUser, CompanyEmployee
from authentication.serializers import CompanyEmployeeSerializer

class RetrieveEmployeesContactsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanyEmployeeSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        app_users = AppUser.objects.all()
        contacts = []
        for app_user in app_users:
            employee = CompanyEmployee.objects.filter(app_user=app_user).first()
            if employee:
                contacts.append(employee)
        return contacts
