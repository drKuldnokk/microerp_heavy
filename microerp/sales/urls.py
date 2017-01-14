from django.conf.urls import url

from sales import views

urlpatterns = [
    url(r'^products/$', views.products, name='products'),
    url(r'^orders/$', views.sales_orders, name='orders'),
    url(r'^orders/(?P<order_id>[0-9]+)/$', views.sales_order, name='order'),
    url(r'^orders/(?P<order_id>[0-9]+)/related_products/(?P<product_id>[0-9,A-Z]+)/$',
        views.related_products, name='related_products'),
    url(r'^$', views.index, name='index'),
]