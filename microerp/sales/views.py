from django.shortcuts import render, get_object_or_404

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from sales.models import Product, SalesOrder, SalesLine


def index(request):
    n_products = Product.objects.raw(
        "SELECT 1 AS id, COUNT(id) AS count FROM sales_product")[0].count
    n_sales_orders = SalesOrder.objects.raw(
        "SELECT 1 AS id, COUNT(id) AS count FROM sales_salesorder")[0].count
    n_sales_lines = SalesLine.objects.raw(
        "SELECT 1 AS id, COUNT(id) AS count FROM sales_salesline")[0].count
    return render(request, 'sales/index.html', context = {
        'n_products' : n_products,
        'n_sales_orders' : n_sales_orders,
        'n_sales_lines' : n_sales_lines})

def products(request):
    # aeglane >
    '''
        SELECT P.id, P.name, TOTAL(SL.quantity) AS popularity
        FROM sales_product AS P
        LEFT OUTER JOIN sales_salesline AS SL 
            ON SL.product_id_id = P.id 
        GROUP BY P.id, P.name
        ORDER BY popularity DESC;
    '''
    # < aeglane
    
    all_products = Product.objects.raw('''
        SELECT id, name, TOTAL(popularity) AS popularity
        FROM sales_product AS P
        LEFT OUTER JOIN sales_popularity AS SP 
            ON SP.product_id = P.id 
        GROUP BY id, name
        ORDER BY popularity DESC;
        ''')
    all_products.count = lambda : Product.objects.raw("SELECT 1 AS id, COUNT(id) AS count FROM sales_product")[0].count
    paginator = Paginator(all_products, 50)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    return render(request, 'sales/products.html', context = {'products' : products})
    
def sales_orders(request):
    paginator = Paginator(SalesOrder.objects.all(), 50)
    page = request.GET.get('page')
    try:
        sales_orders = paginator.page(page)
    except PageNotAnInteger:
        sales_orders = paginator.page(1)
    except EmptyPage:
        sales_orders = paginator.page(paginator.num_pages)
    return render(request, 'sales/orders.html', context = {'orders' : sales_orders})
    
def sales_order(request, order_id):
    o = get_object_or_404(SalesOrder, pk=order_id)
    lines = SalesLine.objects.raw("""
        SELECT SL.id AS id, SP.id AS product, SP.name AS productName, SL.quantity AS quantity
        FROM sales_salesline AS SL
        JOIN sales_product AS SP
            ON SL.product_id_id = SP.id
        WHERE SL.order_id_id = '{}'
        """.format(order_id))
    context = {'order' : o, 'lines' : lines}
    return render(request, 'sales/order.html', context)
    
def related_products(request, order_id, product_id):
    o = get_object_or_404(SalesOrder, pk=order_id)
    p = get_object_or_404(Product, pk=product_id)
    lines = SalesLine.objects.raw('''
        SELECT OL.id, P.id AS p_id, P.name AS p_name, TOTAL(quantity) AS popularity
        FROM sales_salesline AS OL
        JOIN sales_product AS P
            on P.id = OL.product_id_id
        WHERE product_id_id in (SELECT product_id_id FROM sales_salesline WHERE order_id_id = {})
            AND product_id_id <> '{}'
        GROUP BY OL.product_id_id, P.name
        ORDER BY popularity DESC;
        '''.format(order_id, product_id))
    return render(request, 'sales/related_products.html',context={
        'order' : o,
        'product' : p,
        'lines' : lines})