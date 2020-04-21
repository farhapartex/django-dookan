from django.db.models import Sum
from dookan.models import *
from system.models import *
import datetime


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
    
def get_sell_information():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    last_week = today - datetime.timedelta(days=7)
    try:
        order_queryset = Order.objects.all()
        today_sell = order_queryset.filter(created_at__date=today).aggregate(Sum('cost'))['cost__sum']
        yesterday_sell = order_queryset.filter(created_at__date=yesterday).aggregate(Sum('cost'))['cost__sum']
        last7days_sell = order_queryset.filter(created_at__date__gte=last_week, created_at__date__lte=today).aggregate(Sum('cost'))['cost__sum']
        
        today_sell = 0 if today_sell is None else today_sell
        yesterday_sell = 0 if yesterday_sell is None else yesterday_sell
        last7days_sell = 0 if last7days_sell is None else last7days_sell
        return (today_sell, yesterday_sell,last7days_sell)
    except:
        return (0.0, 0.0, 0.0)
    

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
        "sell_info": get_sell_information(),
        "recent_orders": get_recent_orders(),
    }
    