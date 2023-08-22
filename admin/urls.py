from django.urls import path, include
import admin.views as views

urlpatterns = [

    path("contacts/", views.ContactsView.as_view(), name="contacts-list"),
    
]
