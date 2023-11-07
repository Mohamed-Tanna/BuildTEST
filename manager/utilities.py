
from django.db.models import Q
from rest_framework import exceptions
import shipment.models as ship_models
from django.db.models.query import QuerySet
import authentication.models as auth_models
from django.shortcuts import get_object_or_404


def check_manager_can_view_load(load_id, user):
    load = get_object_or_404(ship_models.Load, id=load_id)
    manager = get_object_or_404(
        auth_models.AppUser, user=user)
    company = get_object_or_404(auth_models.Company, manager=manager)
    # just to check if there is an employee of this company has access to this load
    company_employees = auth_models.CompanyEmployee.objects.filter(
        company=company
    ).values_list("app_user", flat=True)
    if (
        load.created_by.id not in company_employees
        and load.customer.app_user.id not in company_employees
        and load.shipper.app_user.id not in company_employees
        and load.consignee.app_user.id not in company_employees
        and load.dispatcher.app_user.id not in company_employees
    ):
        print(load.created_by, company_employees)
        raise exceptions.PermissionDenied(
            detail="You don't have access to view this load's information")
    if load.carrier and load.carrier.app_user.id not in company_employees:
            raise exceptions.PermissionDenied(
                detail="You don't have access to view this load's information")
    return load, company_employees

def check_manager_can_view_load_queryset(queryset: QuerySet, user):
    manager = get_object_or_404(
        auth_models.AppUser, user=user)
    company = get_object_or_404(auth_models.Company, manager=manager)
    queryset = (
            queryset.filter(
                Q(created_by__companyemployee__company=company)
                | Q(customer__app_user__companyemployee__company=company)
                | Q(shipper__app_user__companyemployee__company=company)
                | Q(consignee__app_user__companyemployee__company=company)
                | Q(dispatcher__app_user__companyemployee__company=company)
                | Q(carrier__app_user__companyemployee__company=company)
            )
            .distinct()
            .order_by("-id")
        )

    return queryset

def get_parties_companies(load):
    try:
        created_by_company = auth_models.CompanyEmployee.objects.get(
            app_user=load.created_by
        ).company
    except auth_models.CompanyEmployee.DoesNotExist:
        created_by_company = None

    try:
        customer_company = auth_models.CompanyEmployee.objects.get(
            app_user=load.customer.app_user
        ).company
    except auth_models.CompanyEmployee.DoesNotExist:
        customer_company = None

    try:
        shipper_company = auth_models.CompanyEmployee.objects.get(
            app_user=load.shipper.app_user
        ).company
    except auth_models.CompanyEmployee.DoesNotExist:
        shipper_company = None

    try:
        consignee_company = auth_models.CompanyEmployee.objects.get(
            app_user=load.consignee.app_user
        ).company
    except auth_models.CompanyEmployee.DoesNotExist:
        consignee_company = None

    try:
        dispatcher_company = auth_models.CompanyEmployee.objects.get(
            app_user=load.dispatcher.app_user
        ).company
    except auth_models.CompanyEmployee.DoesNotExist:
        dispatcher_company = None

    try:
        if load.carrier:
            carrier_company = auth_models.CompanyEmployee.objects.get(
                app_user=load.carrier.app_user
            ).company
        else:
            carrier_company = None
    except auth_models.CompanyEmployee.DoesNotExist:
        carrier_company = None
    return created_by_company, customer_company, shipper_company, consignee_company, dispatcher_company, carrier_company