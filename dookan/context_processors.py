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

def summary_data(request):
    
    return {
        "pending_orders": get_order_info(),
        "total_customers": get_customer_info(),
    }
    