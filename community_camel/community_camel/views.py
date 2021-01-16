from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import Error, OperationalError
from django.db.transaction import atomic
from psycopg2 import errorcodes
from functools import wraps
import json
import sys
import time

from community_camel.models import *

# Warning: Do not use retry_on_exception in an inner nested transaction.


def retry_on_exception(view, num_retries=3, on_failure=HttpResponse(status=500), delay_=0.5, backoff_=1.5):
    @wraps(view)
    def retry(*args, **kwargs):
        delay = delay_
        for i in range(num_retries):
            try:
                return view(*args, **kwargs)
            except OperationalError as ex:
                if i == num_retries - 1:
                    return on_failure
                elif getattr(ex.__cause__, 'pgcode', '') == errorcodes.SERIALIZATION_FAILURE:
                    time.sleep(delay)
                    delay *= backoff_
                else:
                    return on_failure
            except Error as ex:
                return on_failure
    return retry


class PingView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("python/django", status=200)

@method_decorator(csrf_exempt, name='dispatch')
class SignupView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'signup.html')

    def post(self, request, *args, **kwargs):
        a = request.POST
        '''account = Account(
            emailId=a["email"],
            password=a[password],
            phoneNum=a["phone"],
            firstName=a["fname"],
            lastName=a["lname"],
            dob
        )'''
        request.POST["fname"]
        print(request.body.decode())
        return HttpResponse("workd", status=200)


@method_decorator(csrf_exempt, name='dispatch')
class AccountsView(View):
    def get(self, request, id=None, *args, **kwargs):
        if id is None:
            customers = list(Accounts.objects.values())
        else:
            customers = list(Accounts.objects.filter(id=id).values())
        return JsonResponse(customers, safe=False)

    @retry_on_exception
    @atomic
    def post(self, request, *args, **kwargs):
        form_data = json.loads(request.body.decode())
        name = form_data['name']
        c = Accounts(name=name)
        c.save()
        return HttpResponse(status=200)

    @retry_on_exception
    @atomic
    def delete(self, request, id=None, *args, **kwargs):
        if id is None:
            return HttpResponse(status=404)
        Accounts.objects.filter(id=id).delete()
        return HttpResponse(status=200)

    # The PUT method is shadowed by the POST method, so there doesn't seem
    # to be a reason to include it.


@method_decorator(csrf_exempt, name='dispatch')
class OrderListView(View):
    def get(self, request, id=None, *args, **kwargs):
        if id is None:
            products = list(OrderList.objects.values())
        else:
            products = list(OrderList.objects.filter(id=id).values())
        return JsonResponse(products, safe=False)

    @retry_on_exception
    @atomic
    def post(self, request, *args, **kwargs):
        form_data = json.loads(request.body.decode())
        name, price = form_data['name'], form_data['price']
        p = OrderList(name=name, price=price)
        p.save()
        return HttpResponse(status=200)

    # The REST API outlined in the github does not say that /product/ needs
    # a PUT and DELETE method


@method_decorator(csrf_exempt, name='dispatch')
class OrderItemView(View):
    def get(self, request, id=None, *args, **kwargs):
        if id is None:
            orders = list(OrderItem.objects.values())
        else:
            orders = list(OrderItem.objects.filter(id=id).values())
        return JsonResponse(orders, safe=False)

    @retry_on_exception
    @atomic
    def post(self, request, *args, **kwargs):
        form_data = json.loads(request.body.decode())
        c = Accounts.objects.get(id=form_data['customer']['id'])
        o = OrderItem(subtotal=form_data['subtotal'], customer=c)
        o.save()
        for p in form_data['products']:
            p = OrderList.objects.get(id=p['id'])
            o.product.add(p)
        o.save()
        return HttpResponse(status=200)