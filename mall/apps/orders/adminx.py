import xadmin
class OrderAdmin(object):
    data_charts = {
        "order_amount": {'title': '订单金额', "x-field": "create_time", "y-field": ('total_amount',),
                         "order": ('create_time',)},
        "order_count": {'title': '订单量', "x-field": "create_time", "y-field": ('total_count',),
                        "order": ('create_time',)},
    }

from .models import OrderInfo
xadmin.site.register(OrderInfo,OrderAdmin)
