from django.shortcuts import render
from vivanda_web.conexion import conexion
from utils.clases import Carrito
# Create your views here.

def pago(request):
    cart = Carrito(request)
    return render(request, 'pago.html')