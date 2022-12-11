from email.headerregistry import Address
from multiprocessing import context
from venv import create
from django.shortcuts import render
from django.http import JsonResponse
import datetime
import json
from .models import *
from .utils import cookieCart, cartData ,guestOrder

# Create your views here.
def store(request):

     data = cartData(request)
     cartItems = data['cartItems']
     
     products = Product.objects.all()
     context = {'products':products, 'cartItems':cartItems}
     return render(request, 'store/store.html', context)
  
     


def cart(request):

     data = cartData(request)
     cartItems = data['cartItems']
     order = data['order']
     items = data['items']
          
     context = {'items':items, 'order':order, 'cartItems':cartItems}
     return render(request, 'store/cart.html', context)


def checkout(request):
     
     data = cartData(request)
     cartItems = data['cartItems']
     order = data['order']
     items = data['items']
      
     context = {'items':items, 'order':order, 'cartItems':cartItems}
     return render(request, 'store/checkout.html', context)


def UpdateItem(request):
     data = json.loads(request.data)
     productId = data['productId']
     action = data['action']
     print('Action:', action)
     print('Product:', productId)

     customer = request.user.customer
     product = Product.objects.get(id=productId)
     order, created = Order.objects.get_or_create(customer=customer, complete=False)

     OrderItem, create = OrderItem.objects.get_or_create(order=order, product=product)

     if action == 'add':
          OrderItem.quantity = (OrderItem.quantity + 1)
     elif action == 'remove':
          OrderItem.quantity = (OrderItem.quantity - 1)
     
     OrderItem.save()

     if OrderItem.quantity <= 0:
          OrderItem.delete()
          
     return JsonResponse('Item was added', safe=False)

def processOrder(request):
     transaction_id = datetime.datetime.now().timestamp()
     data = json.loads(request.body)

     if request.user.is_authenticated:
          customer = request.user.customer
          order, created = Order.objects.get_or_create(customer=customer, complete=False)

     else:
          customer, order = guestOrder(request, data)

     total = float(data['form']['total'])
     order.transaction_id = transaction_id

     if total == float(order.get_cart_total):
          order.complete = True
     order.save()

     if order.shipping == True:
               ShippingAddress.objects.create(
                    customer=customer,
                    order=order,
                    Address=data['shipping']['addres'],
                    city=data['shipping']['city'],
                    state=data['shipping']['state'],
                    zipcode=data['shipping']['zipcode'],
               )


     return JsonResponse('Payment subbmited..',safe=False)


#if request.user.is_authenticated:
     #     customer = request.user.customer
     #     order, created = Order.objects.get_or_create(customer=customer, complete=False)
     #     items = order.get_cart_items
     #     cartItems = order.get_cart_items
     #else:
     #     items = []
     #     order = {'get_cart_total':0, 'get_cart_items':0}
     #     cartItems = order['get_cart_items']

     #products = Product.objects.all()
     #context = {'Product':Product, 'cartItems':cartItems}
     #return render(request, 'store/store.html', context)


#def store(request):
#     products = Product.objects.all()
#     context = {'products':products}
#     return render(request, 'store/store.html', context)



########################################################################


#  <script type="text/javascripts">
#    var user = '{{request.user}}'
#    function getCookie(name) {
#      let cookieValue = null;
#      if (document.cookie && document.cookie !== '') {
#         const cookies = document.cookie.split(';');
#          for (let i = 0; i < cookies.length; i++) {
#              const cookie = cookies[i].trim();
#             // Does this cookie string begin with the name we want?
#              if (cookie.substring(0, name.length + 1) === (name + '=')) {
#                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
#                 break;
#              }
#          }
#      }
#      return cookieValue;
#  }
#  const csrftoken = getCookie('csrftoken');
#  </script>