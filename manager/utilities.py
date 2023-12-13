from datetime import datetime

from django.db.models import Q, Sum, Count, F
from rest_framework import exceptions
import shipment.models as ship_models
from django.db.models.query import QuerySet
import authentication.models as auth_models
from django.shortcuts import get_object_or_404

from freightmonster.constants import AWAITING_CUSTOMER, ASSIGNING_CARRIER, AWAITING_CARRIER, AWAITING_DISPATCHER, \
    IN_TRANSIT, READY_FOR_PICKUP


def check_manager_can_view_load(load_id, user):
    load = get_object_or_404(ship_models.Load, id=load_id)
    manager = get_object_or_404(
        auth_models.AppUser, user=user)
    company = get_object_or_404(auth_models.Company, manager=manager)
    # just to check if there is an employee of this company has access to this load
    company_employees = auth_models.CompanyEmployee.objects.filter(
        company=company
    ).values_list("app_user", flat=True)

    not_created_by_employee = load.created_by.id not in company_employees
    not_customer_employee = load.customer.app_user.id not in company_employees
    not_shipper_employee = load.shipper.app_user.id not in company_employees
    not_consignee_employee = load.consignee.app_user.id not in company_employees
    not_dispatcher_employee = load.dispatcher.app_user.id not in company_employees

    if load.carrier:
        not_carrier_employee = load.carrier.app_user.id not in company_employees
    else:
        not_carrier_employee = True

    if (
            not_created_by_employee
            and not_customer_employee
            and not_shipper_employee
            and not_consignee_employee
            and not_dispatcher_employee
            and not_carrier_employee
    ):
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


def create_dashboard_cards(filter_query, delivered_loads):
    cards = dict()
    cards["total"] = filter_query.count()
    cards["pending"] = filter_query.filter(
        status__in=[
            "Created",
            AWAITING_CUSTOMER,
            ASSIGNING_CARRIER,
            AWAITING_CARRIER,
            AWAITING_DISPATCHER,
        ]
    ).count()

    cards["ready_for_pick_up"] = filter_query.filter(
        status=READY_FOR_PICKUP).count()
    cards["in_transit"] = filter_query.filter(status=IN_TRANSIT).count()
    cards["delivered"] = delivered_loads.count()
    cards["canceled"] = filter_query.filter(status="Canceled").count()
    return cards


def create_dashboard_chart(filter_query):
    result = []
    year = datetime.now().year
    for i in range(1, 13):
        monthly_loads = filter_query.filter(
            created_at__month=i, created_at__year=year)
        obj = dict()
        obj["name"] = datetime.strptime(str(i), "%m").strftime("%b")
        if monthly_loads.exists() is False:
            obj["total"] = 0
            obj["pending"] = 0
            obj["ready_for_pick_up"] = 0
            obj["in_transit"] = 0
            obj["delivered"] = 0
            obj["canceled"] = 0
        else:
            obj["total"] = monthly_loads.count()
            obj["pending"] = monthly_loads.filter(
                status__in=[
                    "Created",
                    AWAITING_CUSTOMER,
                    ASSIGNING_CARRIER,
                    AWAITING_CARRIER,
                    AWAITING_DISPATCHER,
                ]
            ).count()

            obj["ready_for_pick_up"] = monthly_loads.filter(
                status=READY_FOR_PICKUP
            ).count()
            obj["in_transit"] = monthly_loads.filter(status=IN_TRANSIT).count()
            obj["delivered"] = monthly_loads.filter(status="Delivered").count()
            obj["canceled"] = monthly_loads.filter(status="Canceled").count()
        result.append(obj)
    return result


def create_dashboard_load_types(filter_query):
    ftl = filter_query.filter(load_type="FTL").count()
    ltl = filter_query.filter(load_type="LTL").count()
    heavy_haul = filter_query.filter(weight__gte=80000).count()
    return {
        "ftl": ftl,
        "ltl": ltl,
        "hhl": heavy_haul,
    }


def create_dashboard_offers_info(delivered_loads):
    result = dict()
    year = datetime.now().year
    carrier_offers = ship_models.Offer.objects.filter(
        load__in=delivered_loads, status="Accepted", to="carrier"
    )

    carriers = carrier_offers.values_list("party_2", flat=True).distinct()
    result["carrier_offers"] = []

    result["carriers_chart"] = []

    for carrier in carriers:
        carrier_queryset = carrier_offers.filter(
            party_2=carrier)
        aggregates = carrier_queryset.aggregate(sum=Sum("current"))
        carrier = auth_models.AppUser.objects.get(id=carrier).user
        obj = dict()
        obj["name"] = carrier.username
        if aggregates["sum"] is None:
            obj["total"] = 0
            result["carrier_offers"].append(obj)
            continue
        obj["total"] = aggregates["sum"]
        result["carrier_offers"].append(obj)

        # THIS SECTION IS FOR MONTHLY CHARTS FOR EACH CARRIER
        # result["carriers_chart"][carrier.username] = []
        # for i in range(1, 13):
        #     monthly_loads = filter_query.filter(
        #         created_at__month=i, created_at__year=year)
        #     carriers_monthly_loads = carrier_queryset.filter(
        #         load__in=monthly_loads)
        #     obj = {}
        #     obj["name"] = datetime.strptime(str(i), "%m").strftime("%b")
        #     if carriers_monthly_loads.exists() is False:
        #         obj["total"] = 0
        #         result["carriers_chart"][carrier.username].append(obj)
        #         continue
        #     obj["total"] = carriers_monthly_loads.aggregate(sum=Sum("current"))[
        #         "sum"]
        #     result["carriers_chart"][carrier.username].append(obj)

    # Get bar charts for cost of shipping to each customer
    customer_offers = ship_models.Offer.objects.filter(
        load__in=delivered_loads, status="Accepted", to="customer"
    )

    customers = customer_offers.values_list(
        "party_2", flat=True).distinct()
    result["customer_offers"] = []

    result["customers_chart"] = []

    for customer in customers:
        aggregates = customer_offers.filter(
            party_2=customer).aggregate(sum=Sum("current"))
        customer = auth_models.AppUser.objects.get(id=customer).user
        obj = dict()
        obj["name"] = customer.username
        if aggregates["sum"] is None:
            obj["total"] = 0
            result["customer_offers"].append(obj)
            continue
        obj["total"] = aggregates["sum"]
        result["customer_offers"].append(obj)

        # THIS SECTION IS FOR MONTHLY CHARTS FOR EACH CUSTOMER
        # result["customers_chart"][customer.username] = []
        # for i in range(1, 13):
        #     monthly_loads = filter_query.filter(
        #         created_at__month=i, created_at__year=year)
        #     carriers_monthly_loads = carrier_queryset.filter(
        #         load__in=monthly_loads)
        #     obj = {}
        #     obj["name"] = datetime.strptime(str(i), "%m").strftime("%b")
        #     if carriers_monthly_loads.exists() is False:
        #         obj["total"] = 0
        #         result["customers_chart"][customer.username].append(obj)
        #         continue
        #     obj["total"] = carriers_monthly_loads.aggregate(sum=Sum("current"))[
        #         "sum"]
        #     result["customers_chart"][customer.username].append(obj)

    # Profit Analysis
    total_paid = carrier_offers.aggregate(sum=Sum("current"))["sum"]
    total_received = customer_offers.aggregate(sum=Sum("current"))["sum"]
    revenue = total_received - total_paid
    result["total_paid"] = total_paid
    result["total_received"] = total_received
    # TODO: Revenue should be calculated based on the date range (this_month, this_year)
    result["revenue"] = revenue

    result["profit_summary_chart"] = {}

    result["profit_summary_chart"]["year"] = []
    for i in range(1, 13):
        total_paid = carrier_offers.filter(
            created_at__month=i, created_at__year=year).aggregate(sum=Sum("current"))["sum"]
        if total_paid is None:
            total_paid = 0
        total_received = customer_offers.filter(
            created_at__month=i, created_at__year=year).aggregate(sum=Sum("current"))["sum"]
        if total_received is None:
            total_received = 0
        revenue = total_received - total_paid
        obj = dict()
        obj["name"] = datetime.strptime(str(i), "%m").strftime("%b")
        obj["total_paid"] = total_paid
        obj["total_received"] = total_received
        obj["revenue"] = revenue

        result["profit_summary_chart"]["year"].append(obj)

    month = datetime.now().month
    result["profit_summary_chart"]["month"] = []
    for i in range(1, 32):
        total_paid = carrier_offers.filter(
            created_at__day=i, created_at__month=month, created_at__year=year).aggregate(sum=Sum("current"))["sum"]
        if total_paid is None:
            total_paid = 0
        total_received = customer_offers.filter(
            created_at__day=i, created_at__month=month, created_at__year=year).aggregate(sum=Sum("current"))["sum"]
        if total_received is None:
            total_received = 0
        revenue = total_received - total_paid
        obj = dict()
        obj["name"] = datetime.strptime(str(i), "%d").strftime("%d")
        obj["total_paid"] = total_paid
        obj["total_received"] = total_received
        obj["revenue"] = revenue
        result["profit_summary_chart"]["month"].append(obj)

    return result


def create_dashboard_equipment(filter_query):
    equipments = filter_query.values("equipment").annotate(
        equipment_count=Count("equipment")).order_by("-equipment_count")[:5]
    result = dict()
    count = 0
    for equipment in equipments:
        result[count] = {
            "name": equipment["equipment"],
            "count": equipment["equipment_count"]
        }
        count += 1
    return result


def create_dashboard_top_employees(delivered_loads):
    dispatchers = delivered_loads.values("dispatcher").annotate(
        load_count=Count("dispatcher")).order_by("-load_count")[:5]
    result = dict()
    count = 0
    for dispatcher in dispatchers:
        # Get Revenue for each dispatcher
        received_from_customers = ship_models.Offer.objects.filter(
            load__in=delivered_loads, status="Accepted", to="customer", party_1=dispatcher["dispatcher"]
        ).aggregate(sum=Sum("current"))['sum']
        paid_to_carriers = ship_models.Offer.objects.filter(
            load__in=delivered_loads, status="Accepted", to="carrier", party_1=dispatcher["dispatcher"]
        ).aggregate(sum=Sum("current"))['sum']
        if received_from_customers is None:
            received_from_customers = 0
        if paid_to_carriers is None:
            paid_to_carriers = 0
        revenue_for_dispatcher = received_from_customers - paid_to_carriers
        dispatcher_user = auth_models.Dispatcher.objects.get(
            id=dispatcher["dispatcher"]).app_user.user

        result[count] = {
            "name": dispatcher_user.username,
            "email": dispatcher_user.email,
            "load_count": dispatcher["load_count"],
            "revenue": revenue_for_dispatcher
        }
        count += 1
    return result


def get_dashboard_delivery_performance(delivered_loads):
    on_time = delivered_loads.filter(
        actual_delivery_date__lte=F("delivery_date")).count()
    late = delivered_loads.filter(
        actual_delivery_date__gt=F("delivery_date")).count()
    return {
        "on_time": on_time,
        "late": late,
        "missed": 0,  # TODO: Implement this
    }
