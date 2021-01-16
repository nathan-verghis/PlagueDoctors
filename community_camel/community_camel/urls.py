"""community_camel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url

from .views import AccountsView, OrderItemView, OrderListView, PingView, SignupView

urlpatterns = [
    url('admin/', admin.site.urls),

    url('ping/', PingView.as_view()),
    url('signup/',SignupView.as_view() ),

    # Endpoints for customers URL.
    url('accounts/', AccountsView.as_view(), name='accounts'),
    url('accounts/<int:id>/', AccountsView.as_view(), name='accounts'),

    # Endpoints for customers URL.
    url('orderItem/', OrderItemView.as_view(), name='orderItem'),
    url('orderItem/<int:id>/', OrderItemView.as_view(), name='orderItem'),

    url('orderList/', OrderListView.as_view(), name='orderList'),
]

