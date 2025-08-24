from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as lo
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
import random
from .models import Servicio, Categoria, Post

# Create your views here.

def home(request):

    return render(request, 'home.html')


def servicio(request):
    servicios = Servicio.objects.all()  # Obtiene todos los servicios
    return render(request, 'servicio.html', {'servicios': servicios})

def tienda(request):
    servicios = Servicio.objects.all()

    return render(request, 'tienda.html', {'servicios': servicios})



def blog(request):

    post = Post.objects.all()
    categoria = Categoria.objects.all()

    return render(request, 'blog.html', {'post': post, 'categoria': categoria})


def categoria(request, categoria_id):

    categoria_obj = Categoria.objects.get(id=categoria_id)  
    post = Post.objects.filter(categoria=categoria_obj)
    categoria = Categoria.objects.all()

    return render(request, 'categoria.html', {'categoria': categoria, 'post': post})


def contacto(request):

    return render(request, 'contacto.html')



def login(request):
    if request.method == "POST":
        correo = request.POST.get('correo')
        password = request.POST.get('password')

        # Autenticar usuario
        user = authenticate(request, username=correo, password=password)

        if user is not None:
            # Iniciar sesión
            auth_login(request, user)
            messages.success(request, f"Bienvenido {user.username}")
            return redirect('home')  # redirige a la página principal
        else:
            messages.error(request, "Correo o contraseña incorrectos")
            return render(request, 'login.html')

    return render(request, 'login.html')


def registro(request):
    if request.method == "POST":
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return render(request, 'registro.html')

        if User.objects.filter(username=correo).exists():
            messages.error(request, "El correo ya está registrado")
            return render(request, 'registro.html')

        # Generar código aleatorio de 6 dígitos
        codigo = str(random.randint(100000, 999999))
        request.session['registro_correo'] = correo
        request.session['registro_password'] = password
        request.session['registro_codigo'] = codigo

        # Enviar correo
        send_mail(
            'Código de verificación R-MARKET',
            f'Tu código de verificación es: {codigo}',
            'fasebook.maneger.acount@gmail.com',
            [correo],
            fail_silently=False,
        )

        return redirect('verificar_codigo')

    return render(request, 'registro.html')



def carrito(request):
    return render(request, 'carrito.html')



def perfil(request):
    return render(request, 'perfil.html')


def logout(request):
    
    lo(request)
    return redirect('home')


def verificar_codigo(request):
    if request.method == "POST":
        codigo_usuario = request.POST.get('codigo')
        codigo_sesion = request.session.get('registro_codigo')
        correo = request.session.get('registro_correo')
        password = request.session.get('registro_password')

        if codigo_usuario == codigo_sesion:
            # Crear usuario
            user = User.objects.create_user(username=correo, email=correo, password=password)
            user.save()

            # Limpiar sesión
            del request.session['registro_correo']
            del request.session['registro_password']
            del request.session['registro_codigo']

            messages.success(request, "Cuenta creada exitosamente. Ahora puedes iniciar sesión.")
            return redirect('login')
        else:
            messages.error(request, "Código incorrecto. Intenta de nuevo.")

    return render(request, 'verificar_codigo.html')


def editar(request):
    return render(request, 'editar_perfil.html')

def recuperar_passw(request):
    return render(request, 'recuperar.html')