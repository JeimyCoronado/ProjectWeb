"""vivanda_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, include
from django.views.generic.base import TemplateView

from GestionPedidos.views import principal, listado_productos, add_product, decrement_product, \
    finalizar, listaPedidos, detallePedido
from GestionUsuarios.views import loginCliente, loginEmpleado, registrarEmpleado, registrarCliente, confirmacion, \
    recuperacion, recuperaEmpleado, salirSesion


urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('productos/', include('productos.urls'), name='productos'),
    path('admin/', admin.site.urls),
    path('login/', loginCliente),
    path('loginEmpleado/', loginEmpleado),
    path('registroEmpleado/', registrarEmpleado),
    path('principalProducto/', principal, name='index'),
    path('registroCliente/', registrarCliente),
    path('confirmacion/', confirmacion),
    path('recuperar/', recuperacion),
    path('recuperaEmpleado/', recuperaEmpleado),
    path('listado_producto', listado_productos, name='listado_productos'),
    path('agregar/<sku>', add_product, name='Add'),
    path('restar/<sku>', decrement_product, name='Sub'),
    path('finalizar/', finalizar, name='finalizar'),
    path('salir/', salirSesion),
    path('listaPedidos/', listaPedidos),
    path('detallePedido/<id_pedido>',detallePedido)
]
