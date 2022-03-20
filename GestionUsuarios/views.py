import random
import string
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from werkzeug.security import generate_password_hash, check_password_hash
# Create your views here.
from GestionUsuarios.Usuario import Cliente
from vivanda_web import settings
from vivanda_web.conexion import conexion
from django.contrib.sessions.models import Session


def obtenerCodigo(id_usuario):
    numero = random.randint(100000, 999999)
    try:
        with conexion:
            with conexion.cursor() as cursor1:
                cursor1.execute("SELECT * FROM verificacion WHERE cod_verif=%s;",(str(numero),))
                registro = cursor1.fetchall()
                if registro:
                    return obtenerCodigo(id_usuario)
                else:
                    try:
                        with conexion:
                            with conexion.cursor() as cursor2:
                                cursor2.execute("INSERT INTO verificacion (id_usuario,cod_verif) VALUES (%s,%s)", (id_usuario,str(numero)))
                    except Exception as e2:
                        return 'Ocurrio un error: %s' % (e2,)
                    return numero
    except Exception as e:
        return 'Ocurrio un error: %s' % (e,)


def loginCliente(request):
    if request.method == 'POST':
        usuario_o_correo = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')
        try:
            with conexion:
                with conexion.cursor() as cursor:
                    cursor.execute('''SELECT u.id_usuario, cl.estado, u.correo_electronico, u.password, u.nombre_usuario 
                                    FROM usuario u, cliente cl WHERE u.id_usuario=cl.id_cliente
                                    AND (u.nombre_usuario=%s OR u.correo_electronico=%s);''', (usuario_o_correo, usuario_o_correo))
                    registro = cursor.fetchall()
                    if registro:
                        if check_password_hash(registro[0][3], contrasena):
                            if registro[0][1] == 'A':
                                usur = Cliente(request)
                                usur.agregar_cliente(registro[0][0])
                                return redirect('/productos')
                            elif registro[0][1] == 'D':
                                numero = obtenerCodigo(registro[0][0])
                                send_mail("Codigo de confirmación","Tu código de confirmación es %s" %(numero,), settings.EMAIL_HOST_USER,
                                          [registro[0][2]])
                                return render(request, 'confirmacion.html', {'numero': numero, 'info': '''El cliente con 
                                                            nombre de usuario %s ya está registrado. Para activar su cuenta ingrese el código enviado a su correo
                                                            %s''' % (registro[0][4], registro[0][2])})
                        else:
                            return render(request, 'login.html', {'invalido': 'Contraseña incorrecta'})
                    else:
                        return render(request,'login.html',{'invalido':'Nombre de Usuario o correo incorrecto'})

        except Exception as e:
            return HttpResponse('Ocurrio un error: %s' %(e,))

    else:
        Session.objects.all().delete()
        return render(request,'login.html',{'invalido': ''})

def loginEmpleado(request):
    if request.method == 'POST':
        codigo_empleado = request.POST.get('codigo_empleado')
        contrasena = request.POST.get('contrasena')
        try:
            with conexion:
                with conexion.cursor() as cursor:
                    cursor.execute('''SELECT u.id_usuario, u.password FROM usuario u, empleado e WHERE u.id_usuario=e.id_empleado
                                    AND e.id_empleado=%s;''',(codigo_empleado,))
                    registro = cursor.fetchall()
                    if registro:
                        if registro[0][1]:
                            if check_password_hash(registro[0][1], contrasena):
                                return HttpResponse('Bienvenido a Vivanda')
                            else:
                                return render(request, 'loginEmpleado.html', {'invalido': 'Contraseña incorrecta'})
                        else:
                            return render(request, 'loginEmpleado.html', {'invalido2': 'El empledo no está registrado. Por favor, regístrese.'})

                    else:
                        return render(request,'loginEmpleado.html',{'invalido':'Código de empleado incorrecto'})
        except Exception as e:
            return HttpResponse('Ocurrio un error: %s' %(e,))

    else:
        return render(request,'loginEmpleado.html',{'invalido': ''})

def registrarEmpleado(request):
    if request.method == 'POST':
        codigo_empleado = request.POST.get('usuario')
        contrasena1 = request.POST.get('contrasena1')
        contrasena2 = request.POST.get('contrasena2')
        try:
            with conexion:
                with conexion.cursor() as cursor1:
                    cursor1.execute('''SELECT u.password FROM usuario u, empleado e 
                                    WHERE u.id_usuario=e.id_empleado AND u.id_usuario=%s''', (codigo_empleado,))
                    registro = cursor1.fetchall()
                    if registro:
                        if registro[0][0]:
                            return render(request, 'registrarEmpleado.html', {'invalido2': 'El empleado con codigo %s ya está registrado' %(codigo_empleado,)})
                    else:
                        return render(request, 'registrarEmpleado.html', {'invalido2': 'No existe un empleado con codigo %s' %(codigo_empleado,)})
        except Exception as e1:
            return HttpResponse('Ocurrio un error: %s' %(e1,))
        if contrasena1 != contrasena2:
            return render(request,'registrarEmpleado.html',{'invalido':'Las contraseñas no coindiden'})
        else:
            contrasena1 = generate_password_hash(contrasena1)
        try:
            with conexion:
                with conexion.cursor() as cursor:
                    cursor.execute("UPDATE USUARIO SET password=%s WHERE id_usuario=%s;",(contrasena1, codigo_empleado))
                    return redirect('Bienvenido a Vivanda')
        except Exception as e:
            return HttpResponse('Ocurrio un error: %s' %(e,))
    else:
        return render(request, 'registrarEmpleado.html', {'invalido':''})

def registrarCliente(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        correo=request.POST.get('correo')
        tipo_documento = request.POST.get('tipo_documento')
        cod_documento = request.POST.get('numero_documento')
        contrasena1 = request.POST.get('contrasena1')
        contrasena2 = request.POST.get('contrasena2')
        id_usuario='SP%s' %(cod_documento,)
        try:
            with conexion:
                with conexion.cursor() as cursor1:
                    cursor1.execute('''SELECT cl.estado FROM usuario u, cliente cl WHERE u.id_usuario=cl.id_cliente
                                    AND u.cod_documento=%s;''', (cod_documento,))
                    registro = cursor1.fetchall()
                    if registro:
                        if registro[0][0] == 'A':
                            return render(request, 'registroCliente.html', {'invalido2': 'El cliente con codigo de documento %s ya está registrado' %(cod_documento,)})
                        elif registro[0][0] == 'D':
                            return render(request, 'registroCliente.html', {'info':'''El cliente con 
                            codigo de documento %s ya está registrado. Para activar su cuenta debe Iniciar Sesión.''' %(cod_documento,)})
        except Exception as e:
            return HttpResponse('Ocurrio un error: %s' % (e,))
        try:
            with conexion:
                with conexion.cursor() as cursor1:
                    cursor1.execute('''SELECT nombre_usuario, correo_electronico FROM USUARIO WHERE nombre_usuario=%s
                                    OR correo_electronico=%s''',(usuario, correo))
                    registro=cursor1.fetchall()
                    if registro:
                        if registro[0][0] == usuario:
                            return render(request, 'registroCliente.html',
                                          {'invalido2': 'El nombre de usuario ya existe. Por favor ingrese otro.'})
                        if registro[0][1] == correo:
                            return render(request, 'registroCliente.html',
                                          {'invalido3': 'El correo electrónico ya registrado. Por favor ingrese otro.'})
        except Exception as e:
            return HttpResponse('Ocurrio un error: %s' % (e,))
        if contrasena1 != contrasena2:
            return render(request, 'registroCliente.html', {'invalido':'Las contraseñas no coinciden'})
        else:
            contrasena1 = generate_password_hash(contrasena1)
        if tipo_documento == 'D':
            tipo_cliente = 'P'
        else:
            tipo_cliente='E'

        try:
            with conexion:
                with conexion.cursor() as cursor:
                    cursor.execute('''INSERT INTO USUARIO (id_usuario,tipo_documento,cod_documento,correo_electronico,password,nombre_usuario) 
                                   VALUES %s;
                                   INSERT INTO CLIENTE (id_cliente,tipo_cliente,estado) VALUES %s;''',
                                   ((id_usuario, tipo_documento, cod_documento, correo, contrasena1,usuario), (id_usuario,tipo_cliente,'D')))
        except Exception as e:
            return HttpResponse('Ocurrio un error: %s' % (e,))
        numero = obtenerCodigo(id_usuario)
        send_mail("Codigo de confirmación","Tu código de confirmación es %s" %(numero,), settings.EMAIL_HOST_USER,
                  [correo])

        return render(request, 'confirmacion.html', {'numero': numero})
    else:
        return render(request, 'registroCliente.html',{'invalido':''})


def confirmacion(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        try:
            with conexion:
                with conexion.cursor() as cursor:
                    cursor.execute("SELECT id_usuario FROM verificacion WHERE cod_verif=%s", (codigo,))
                    registro = cursor.fetchall()
                    if registro:
                        with conexion:
                            with conexion.cursor() as cursor1:
                                cursor1.execute("UPDATE cliente SET estado='A' WHERE id_cliente=%s", (registro[0],))
                        usur = Cliente(request)
                        usur.agregar_cliente(str(registro[0][0]))
        except Exception as e:
            return HttpResponse('Ocurrio un error: %s' % (e,))
        
        return redirect('/productos')


def recuperacion(request):
    if request.method == 'POST':
        usuario_o_correo = request.POST.get('usuario')
        try:
            with conexion:
                with conexion.cursor() as cursor:
                    cursor.execute('''SELECT u.correo_electronico FROM usuario u, cliente c WHERE  u.id_usuario=c.id_cliente AND
                                    (u.nombre_usuario=%s OR correo_electronico=%s);''', (usuario_o_correo, usuario_o_correo))
                    registro = cursor.fetchall()
                    if registro:
                        newPassword = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(15))
                        send_mail("Recuperación de contraseña", '''Estimado cliente, su nueva contraseña es: %s \n
                                    Se le recomienda cambiar sude contraseña luego de Iniciar Sesión. Saludos.''' % (newPassword,),
                                  settings.EMAIL_HOST_USER, [registro[0][0]])
                        newPassword = generate_password_hash(newPassword)
                        with conexion:
                            with conexion.cursor() as cursor1:
                                cursor1.execute('''UPDATE usuario SET password=%s WHERE nombre_usuario=%s 
                                                OR correo_electronico=%s;''', (newPassword, usuario_o_correo, usuario_o_correo))
                                return render(request, 'login.html', {'recuperacion': 'Su nueva contraseña se envío a su correo electrónico'})
                    else:
                        return render(request, 'login.html',{'invalido': 'Nombre de Usuario o correo incorrecto'})

        except Exception as e:
            return HttpResponse(e)


def salirSesion(request):
    usur = Cliente(request)
    usur.eliminar_cliente()
    return redirect('/login')


def recuperaEmpleado(request):
    if request.method == 'POST':
        codigo_empleado = request.POST.get('codigo_empleado')
        try:
            with conexion:
                with conexion.cursor() as cursor:
                    cursor.execute('''SELECT u.correo_electronico FROM usuario u, empleado e WHERE u.id_usuario=e.id_empleado
                                    AND e.id_empleado=%s;''', (codigo_empleado, ))
                    registro = cursor.fetchall()
                    if registro:
                        newPassword = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(15))
                        send_mail("Recuperación de contraseña", '''Estimado cliente, su nueva contraseña es: %s \n
                                    Se le recomienda cambiar sude contraseña luego de Iniciar Sesión. Saludos.''' % (newPassword,),
                                  settings.EMAIL_HOST_USER, [registro[0][0]])
                        newPassword = generate_password_hash(newPassword)
                        with conexion:
                            with conexion.cursor() as cursor1:
                                cursor1.execute('''UPDATE usuario SET password_usuario=%s 
                                                WHERE id_usuario=%s;''', (newPassword, codigo_empleado))
                                return render(request, 'loginEmpleado.html', {'recuperacion': 'Su nueva contraseña se envío a su correo electrónico'})
                    else:
                        return render(request, 'loginEmpleado.html', {'invalido': 'Código de empleado incorrecto'})
        except Exception as e:
            return HttpResponse(e)




def nuevoPassword():
    password = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(15))

