
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
import time

from django.urls import reverse
# Create your views here.
from utils.clases import Carrito, Busqueda
from GestionPedidos.models import Producto, Promocion
from GestionUsuarios.Usuario import Cliente
from vivanda_web.conexion import conexion


def add_product(request, sku):

    cart = Carrito(request)
    product = get_object_or_404(Producto, pk=sku)
    if product.cod_prom:
        prom = get_object_or_404(Promocion, pk=product.cod_prom)
        cart.agregar(product, prom)
    else:
        cart.agregar(product)

    return redirect('productos:index')
    
    

def remove_product(request, sku):
    cart = Carrito(request)
    product = get_object_or_404(Producto, pk=sku)
    cart.eliminar(product)
    return redirect("listado_productos")


def decrement_product(request, sku):
    cart = Carrito(request)
    product = get_object_or_404(Producto, pk=sku)
    cart.restar(product)
    return redirect('productos:index')


def clear_cart(request):
    cart = Carrito(request)
    cart.limpiar()
    return redirect("listado_productos")


def principal(request):
    return render(request, 'principalProducto.html', {'bebida': 'liquor'})


def listado_productos(request):
    products = Producto.objects.order_by('sku')
    return render(request, "tienda.html", {"products": products})


def finalizar(request):
    cart = Carrito(request)
    client = Cliente(request)
    
    inserts = ''
    try:
        with conexion:
            with conexion.cursor() as cursor:
                for key1, value1 in request.session.get("cliente").items():
                    inserts = '''INSERT INTO pedido (id_pedido,fecha_creacion_pedido,hora_creacion_pedido,id_usuario) 
                                    VALUES (nextval('SEQ01'),to_date('%s','MM/DD/YY'),'%s','%s');''' %(time.strftime('%x'),time.strftime('%X'),value1["id_usuario"])
                    for key, value in request.session.get("carrito").items():
                        inserts += '''INSERT INTO orden_pedido (id_pedido,cod_producto,cantidad,precio_unitario,descuento)
                                    VALUES (currval('SEQ01'),'%s',%s,%s,%s);''' %(value["producto_id"],value["cantidad"],value["precio"],value["descuento"])
                    cursor.execute(inserts)
                    break
    except Exception as e:
        return HttpResponse(e)
    cart.limpiar()
    return redirect('index')


def listaPedidos(request):
    try:
        with conexion:
            with conexion.cursor() as cursor:
                cursor.execute('''SELECT PE.ID_PEDIDO, PE.FECHA_CREACION_PEDIDO, PE.HORA_CREACION_PEDIDO, 
                                SUM(TRUNC((OP.PRECIO_UNITARIO*OP.CANTIDAD)-OP.DESCUENTO,2))
                                FROM PEDIDO PE, ORDEN_PEDIDO OP
                                WHERE PE.ID_PEDIDO=OP.ID_PEDIDO
                                GROUP BY PE.ID_PEDIDO,PE.FECHA_CREACION_PEDIDO
                                ORDER BY PE.FECHA_CREACION_PEDIDO, PE.HORA_CREACION_PEDIDO;''')
                registro = cursor.fetchall()
                if registro:
                    return render(request, 'listaPedidos.html', {'registro': registro})
                else:
                    return HttpResponse('No hay pedidos')
    except Exception as e:
        return HttpResponse('error: %' %(e,))
