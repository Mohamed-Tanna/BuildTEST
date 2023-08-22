from django.urls import path
import employees_contacts.views as views

urlpatterns = [
     path("retrieve-contacts/", views.RetrieveEmployeesContactsView.as_view(), name="retrieve-employees-contacts"),

]
