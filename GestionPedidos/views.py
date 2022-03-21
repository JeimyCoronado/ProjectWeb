from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
import time

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
    

def decrement_product(request, sku):
    cart = Carrito(request)
    product = get_object_or_404(Producto, pk=sku)
    cart.restar(product)
    return redirect('productos:index')


def principal(request):
    total = 0
    try:
        with conexion:
            with conexion.cursor() as cursor:
                cursor.execute('''SELECT PE.ID_PEDIDO, PE.FECHA_CREACION_PEDIDO, PE.HORA_CREACION_PEDIDO, 
                                OP.COD_PRODUCTO,P.NOMBRE_PRODUCTO, OP.PRECIO_UNITARIO, OP.CANTIDAD, 
                                OP.DESCUENTO, TRUNC((OP.PRECIO_UNITARIO*OP.CANTIDAD)-OP.DESCUENTO,2)
                                FROM PEDIDO PE, ORDEN_PEDIDO OP, PRODUCTO P
                                WHERE PE.ID_PEDIDO=OP.ID_PEDIDO AND OP.COD_PRODUCTO=P.COD_PRODUCTO
                                AND PE.ID_PEDIDO=cast(currval('SEQ01') as varchar);''')
                registro = cursor.fetchall()
                #if registro:
                for dato in registro:
                    total += dato[5]*dato[6]-dato[7]
                return render(request, 'principalProducto.html', {'registro': registro, 'total': total})
    except Exception as e:
        return HttpResponse(e)
    
    


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
                    inserts = '''INSERT INTO pedido (id_pedido,fecha_creacion_pedido,hora_creacion_pedido,nro_factura,id_usuario) 
                                    VALUES (nextval('SEQ01'),to_date('%s','MM/DD/YY'),'%s',currval('SEQ01'),'%s');''' %(time.strftime('%x'),time.strftime('%X'),value1["id_usuario"])
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
    client = Cliente(request)
    for key1, value1 in request.session.get("cliente").items():
        id_usuario = value1["id_usuario"]
    try:
        with conexion:
            with conexion.cursor() as cursor:
                cursor.execute('''SELECT PE.ID_PEDIDO, PE.FECHA_CREACION_PEDIDO, PE.HORA_CREACION_PEDIDO, 
                                SUM(TRUNC((OP.PRECIO_UNITARIO*OP.CANTIDAD)-OP.DESCUENTO,2))
                                FROM PEDIDO PE, ORDEN_PEDIDO OP
                                WHERE PE.ID_PEDIDO=OP.ID_PEDIDO AND PE.ID_USUARIO='%s'
                                GROUP BY PE.ID_PEDIDO,PE.FECHA_CREACION_PEDIDO
                                ORDER BY PE.FECHA_CREACION_PEDIDO, PE.HORA_CREACION_PEDIDO;''' %(id_usuario,))
                registro = cursor.fetchall()
                if registro:
                    return render(request, 'listaPedidos.html', {'registro': registro})
                else:
                    return HttpResponse('No hay pedidos')
    except Exception as e:
        return HttpResponse('error: %' %(e,))


def detallePedido(request, id_pedido):
    total=0
    try:
        with conexion:
            with conexion.cursor() as cursor:
                cursor.execute('''SELECT PE.ID_PEDIDO, PE.FECHA_CREACION_PEDIDO, PE.HORA_CREACION_PEDIDO, 
                                OP.COD_PRODUCTO,P.NOMBRE_PRODUCTO, OP.PRECIO_UNITARIO, OP.CANTIDAD, 
                                OP.DESCUENTO, TRUNC((OP.PRECIO_UNITARIO*OP.CANTIDAD)-OP.DESCUENTO,2)
                                FROM PEDIDO PE, ORDEN_PEDIDO OP, PRODUCTO P
                                WHERE PE.ID_PEDIDO=OP.ID_PEDIDO AND OP.COD_PRODUCTO=P.COD_PRODUCTO
                                AND PE.ID_PEDIDO='%s';''' %(id_pedido, ))
                registro = cursor.fetchall()
                if registro:
                    for dato in registro:
                        total += dato[8]
                    return render(request, 'detallePedido.html', {'registro': registro, 'total': total})
                else:
                    return HttpResponse('Error')
    except Exception as e:
        return HttpResponse('error: %' %(e,))
