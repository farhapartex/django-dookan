import datetime
from dookan.models import *
from system.models import *

def get_order_info():
    try:
        order_queryset = Order.objects.all()
        pending_orders = order_queryset.filter(order_confirm=False).count()
        return pending_orders
    except:
        return 0

def get_customer_info():
    try:
        customer_queryset = Customer.objects.all()
        total_customers = customer_queryset.count()
        return total_customers
    except:
        return 0

def get_total_order_today():
    today = datetime.date.today()
    try:
        order_queryset = Order.objects.all()
        total_orders = order_queryset.filter(created_at__date=today).count()
        return total_orders
    except:
        return 0

def get_recent_orders():
    try:
        order_queryset = Order.objects.all()
        return order_queryset if order_queryset.count() > 10 else order_queryset[:10]
    except:
        return []


def summary_data(request):
    
    return {
        "pending_orders": get_order_info(),
        "total_customers": get_customer_info(),
        "total_order_today": get_total_order_today(),
        "recent_orders": get_recent_orders(),
    }
    