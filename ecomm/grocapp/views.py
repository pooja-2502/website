from django.shortcuts import render, redirect,HttpResponse
from django.http import JsonResponse
import json
import datetime
# import razorpay
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created= Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items=[]
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
        
    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created= Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items=[]
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
           
    context = {'items': items, 'order':order, 'cartItems':cartItems}
    return render(request, 'cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created= Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # create Empty cart for none-logged in users
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
        
    context = {'items': items, 'order':order, 'cartItems':cartItems}
    return render(request, 'checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('productId:', productId)
    
    
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created= Order.objects.get_or_create(customer=customer, complete=False)
    
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action=='add':
        orderItem.quantity=(orderItem.quantity + 1)
    elif action =='remove':
        orderItem.quantity=(orderItem.quantity - 1)
    
    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created= Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id
        
        if total == order.get_cart_total:
            order.complete = True
        order.save()
        
        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )
        
    else:
        print('User is not logged in..')
    return JsonResponse('Payment Submitted..', safe=False)


# def makepayment(request):
#     client = razorpay.Client(auth=("rzp_test_hYihu0U4ekyKG1", "kpLAwJKNB4eeskT6U1kzCd20"))

#     DATA = {
#         "amount": 100,
#         "currency": "INR",
#         "receipt": "receipt#1",
#         "notes": {
#             "key1": "value3",
#             "key2": "value2"
#         }
#     }
    
#     payment = client.order.create(data=DATA)
#     print(payment)
#     return HttpResponse("success")

def reg(request):
    if request.method == 'GET':
        
        return render(request, 'registration.html')
    else:
        uname = request.POST['uname']
        uemail = request.POST['uemail']
        upass = request.POST['upass']
        cpass = request.POST['cpass']
        
        if uname == "" or upass == "" or cpass == "":
            
            context = {}
            
            context['msg']= 'Fields Can not be empty'
            
            return render(request, 'registration.html', context)
        
        elif upass != cpass:
            context = {}
            context['msg']= 'Password and Confirm password should Be Same'
            return render(request, 'registration.html', context)
        
        else:
            u= User.objects.create(username=uname, email= uemail)
            u.set_password(upass)
        
            u.save()
            
            context = {}
            context['msg'] = "User Registered Successfully"
            return render(request, 'login.html', context)
        
        
def user_login(request):
    
    if request.method == 'GET':
        
        return render(request, 'login.html')
    else:
        uname = request.POST['uname']
        upass = request.POST['upass']
        
        u = authenticate(username = uname, password = upass)
        
        
        if u is not None:
                login(request, u)
                return redirect('/')
            
        else:
            
            return HttpResponse ("User not found")
        
def user_logout(request):
    logout(request)
    
    return redirect("/")