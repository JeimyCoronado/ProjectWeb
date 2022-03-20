from django.http import HttpResponse
from django.shortcuts import render
from vivanda_web.conexion import conexion
from utils import clases


# Create your views here.
def index(request):
    nombre_producto=''
    if "busqueda" in request.session.keys():
        for key, value in request.session.get("busqueda").items():
            nombre_producto = value["nombre_producto"]
    if request.GET.get('productos_buscar'):
        nombre_producto = request.GET.get('productos_buscar')
        busqueda = clases.Busqueda(request)
        busqueda.agregar(nombre_producto)
    elif request.GET.get('productos_buscar') == '':
        nombre_producto = ''
        busqueda = clases.Busqueda(request)
        busqueda.eliminar()
    conexion
    try:
        with conexion.cursor() as cursor:
            # OBTENER CATEGORIAS
            cursor.execute('SELECT c.* FROM categoria as c;')
            categorias_sql = cursor.fetchall()
            categorias = []
            for categoria_sql in categorias_sql:
                categorias.append(clases.Categoria(categoria_sql))
            # OBTENER PRODUCTOS
            if nombre_producto:
                busqueda = clases.Busqueda(request)
                busqueda.agregar(nombre_producto)
                cursor.execute('''SELECT * 
                            FROM Producto 
                            WHERE unaccent(nombre_producto) ILIKE unaccent('%{}%');
                            '''.format(nombre_producto))
            else:
                cursor.execute('SELECT p.* FROM Producto as p;')
                nombre_producto = ""
            productos_sql = cursor.fetchall()
            productos = []
            for producto_sql in productos_sql:
                productos.append(clases.Producto(producto_sql, request))
            # FORMATEAR PRODUCTOS
            arrProductos = []
            for categoria in categorias:
                dictAxu = {}
                dictAxu[categoria.id_categoria] = []
                arrProductos.append(dictAxu)
            for categoria in categorias:
                for producto in productos:
                    if producto.id_categoria == categoria.id_categoria:
                        count = 0
                        for categProd in arrProductos:
                            key_list = list(categProd.keys())
                            categoryAux = key_list[0]
                            if categoryAux == categoria.id_categoria:
                                arrProductos[count][categoryAux].append(producto)
                            count += 1
            return render(request, 'productos/index.html',{'categorias': categorias, 'productos': arrProductos})
    except Exception as e:
        return HttpResponse('Ocurrio un error: %s' % (e,))

def demo(request):
    conexion
    try:
        with conexion.cursor() as cursor:
            cursor.execute('SELECT p.* FROM producto as p;')
            productos = cursor.fetchall()
            return render(request, 'productos/demoRead.html',{'productos': productos})
    except Exception as e:
        return HttpResponse('Ocurrio un error: %s' % (e,))