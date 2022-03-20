import json
from decimal import Decimal
from msilib.schema import Class

# CLASE PARA FORMATEAR LOS REGISTROS OBTENIDOS POR LA 
# TABLA Categoria DE LA BASE DE DATOS
class Categoria:
    def __init__(self,tupla):
        self.id_categoria = tupla[0]
        self.descripcion_categoria = tupla[1]
        self.nombre_cat = tupla[1]
        self.id_departamento = tupla[3]

# CLASE PARA FORMATEAR LOS REGISTROS OBTENIDOS POR LA 
# TABLA Producto DE LA BASE DE DATOS
class Producto():
    def __init__(self,tupla,request):
        cantidad = 0
        if "carrito" in request.session.keys():
            for key, value in request.session.get("carrito").items():
                if tupla[0] == value["producto_id"]:
                    cantidad = value["cantidad"]
        self.cod_producto = tupla[0]
        self.nombre_producto = tupla[1]
        self.tipo_producto = tupla[2]
        self.informacion_producto = tupla[3]
        self.unidad_medida = tupla[4]
        self.precio_unitario_producto = str(round(tupla[5],2)).replace(',','.')
        self.modelo_prod = tupla[6]
        self.marca_prod = tupla[7]
        self.id_sub_categoria = tupla[8]
        self.id_categoria = tupla[9]
        self.id_departamento = tupla[10]
        self.cod_prom = tupla[11]
        self.cantidad = cantidad
        self.subtotal = round(cantidad*tupla[5], 2)

# CLASES Y FUNCIONES PARA LA GESTIÓN DEL CARRITO
class fakefloat(float):
    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return str(self._value)

def defaultencode(o):
    if isinstance(o, Decimal):
        return fakefloat(o)
    raise TypeError(repr(o) + " is not JSON serializable")


class Carrito:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        carrito = self.session.get("carrito")
        if not carrito:
            carrito = self.session["carrito"] = {}
        self.carrito = carrito

    def agregar(self, producto, promocion=None):
        if producto.cod_producto not in self.carrito.keys():
            descuento = 0
            if promocion:
                try:
                    descuento = float(json.dumps(promocion.desc_precio_producto, default=defaultencode))
                except:
                    pass
            
                
            self.carrito[producto.cod_producto] = {
                "producto_id": producto.cod_producto,
                "nombre": producto.nombre_producto,
                "cantidad": 1,
                "precio": float(json.dumps(producto.precio_unitario_producto, default=defaultencode)),
                "acumulado": float(json.dumps(producto.precio_unitario_producto, default=defaultencode)),
                "descuento": descuento,
                "marca": producto.marca_prod
            }
        else:
            for key, value in self.carrito.items():
                if key == str(producto.cod_producto):
                    value["cantidad"] += 1
                    value["acumulado"] += value["precio"]
                    break
        self.guardar_carrito()

    def guardar_carrito(self):
        self.session["carrito"] = self.carrito
        self.session.modified = True

    def eliminar(self, producto):
        sku = producto.cod_producto
        if sku in self.carrito:
            del self.carrito[sku]
            self.guardar_carrito()

    def restar(self, producto):
        for key, value in self.carrito.items():
            if key == producto.cod_producto:
                value["cantidad"] -= 1
                value["acumulado"] -= value["precio"]
                if value["cantidad"] < 1:
                    self.eliminar(producto)
                else:
                    self.guardar_carrito()
                break
            else:
                print("El producto no existe en el carrito")

    def limpiar(self):
        self.session["carrito"] = {}
        self.session.modified = True


class Busqueda:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        busqueda = self.session.get("busqueda")
        if not busqueda:
            busqueda = self.session["busqueda"] = {}
        self.busqueda = busqueda
    
    def agregar(self, busqueda):
        if busqueda not in self.busqueda.keys():
            self.busqueda['1']={
                "nombre_producto": busqueda
            }
        else:
            self.session["busqueda"] = {}
            self.session.modified = True
            self.busqueda['1']={
                "nombre_producto": busqueda
            }
        self.guardar_busqueda()


    def guardar_busqueda(self):
        self.session["busqueda"] = self.busqueda
        self.session.modified = True

    def eliminar(self):        
        del self.busqueda['1']
        self.guardar_busqueda()