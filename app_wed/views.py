from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as lo
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
import random
import stripe
from django.db.models import Q, Min, Max
from .models import Articulo, ArticuloVariante, Carrito, CarritoItem, Usuario, Categoria_articulo, Servicio, Categoria, Post, Pedido, PedidoItem
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import UsuarioForm

# Create your views here.

def home(request):

    return render(request, 'home.html')


def servicio(request):
    servicios = Servicio.objects.all()  # Obtiene todos los servicios
    return render(request, 'servicio.html', {'servicios': servicios})



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
    if request.method == "POST":
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if email and subject and message:
            try:
                send_mail(
                    subject=f"[Contacto] {subject}",
                    message=f"De: {email}\n\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],  
                )
                messages.success(request, "¡Mensaje enviado correctamente!")
                return redirect('contacto')
            except Exception as e:
                messages.error(request, f"Ocurrió un error al enviar el mensaje: {e}")
        else:
            messages.error(request, "Por favor completa todos los campos.")

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


@login_required
def perfil(request):
    usuario, created = Usuario.objects.get_or_create(
    user=request.user,
    defaults={
        'nombre': request.user.first_name or '',
        'apellido': request.user.last_name or '',
        'cedula': 0,  # temporalmente para evitar el error
        'telefono': '',
    }
)
    return render(request, 'perfil.html', {'usuario': usuario})

@login_required
def editar_perfil(request):
    usuario, created = Usuario.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'editar_perfil.html', {'form': form})



def tienda(request):
    articulos = Articulo.objects.all()
    query = request.GET.get("q")
    if query:
        articulos = articulos.filter(nombre__icontains=query)
    categoria = request.GET.get("categoria")
    if categoria:
        articulos = articulos.filter(categorias__nombre=categoria)
    
    context = {
        "articulos": articulos,
        "categorias": Categoria_articulo.objects.all(),
    }
    return render(request, "tienda.html", context)



def detalle_articulo(request, articulo_id):
    # Obtengo el artículo actual
    articulo = get_object_or_404(Articulo, id=articulo_id)

    # Busco artículos similares (que compartan al menos una categoría, excluyendo el actual)
    articulos_similares = Articulo.objects.filter(
        categorias__in=articulo.categorias.all()
    ).exclude(id=articulo.id).distinct()[:4]  # máximo 4

    return render(request, 'detalle_articulo.html', {
        'articulo': articulo,
        'articulos_similares': articulos_similares
    })



# ➕ Agregar variante al carrito
@login_required
def agregar_al_carrito(request):
    if request.method == "POST":
        variante_id = request.POST.get("variante_id")
        usuario = get_object_or_404(Usuario, user=request.user)
        carrito, created = Carrito.objects.get_or_create(usuario=usuario)
        variante = get_object_or_404(ArticuloVariante, id=variante_id)

        item, created = CarritoItem.objects.get_or_create(
            carrito=carrito,
            articulo=variante,
        )
        if not created:
            item.cantidad += 1
            item.save()
    return redirect("carrito")
# 🛒 Vista del carrito
@login_required
def carrito_view(request):
    usuario, created = Usuario.objects.get_or_create(user=request.user)
    carrito, created = Carrito.objects.get_or_create(usuario=usuario)

    context = {
        "carrito": carrito,
        "items": carrito.items.all(),
        "total": carrito.total(),
    }
    return render(request, "carrito.html", context)


@login_required
def aumentar_cantidad(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id)
    if item.articulo.cantidad > item.cantidad:  # Verifica stock
        item.cantidad += 1
        item.save()
    return redirect('carrito')


@login_required
def reducir_cantidad(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id)
    if item.cantidad > 1:
        item.cantidad -= 1
        item.save()
    else:
        item.delete()
    return redirect('carrito')


@login_required
def confirmar_eliminar(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id)

    if request.method == "POST":
        item.delete()
        return redirect('carrito')

    return render(request, 'confirmar_eliminar.html', {'item': item})


@login_required
def mis_pedidos(request):
    # Obtener el usuario relacionado
    usuario = request.user.usuario  # asumiendo que Usuario tiene OneToOne con User

    # Obtener los pedidos del usuario, ordenados por fecha descendente
    pedidos = Pedido.objects.filter(usuario=usuario).order_by('-fecha')

    context = {
        'pedidos': pedidos
    }
    return render(request, 'mis_pedidos.html', context)


stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def pago_exitoso(request):
    usuario = request.user.usuario
    carrito = Carrito.objects.get(usuario=usuario)
    items = carrito.items.all()

    # Crear Pedido
    pedido = Pedido.objects.create(usuario=usuario, total=carrito.total(), estado='pagado')

    # Crear PedidoItems y reducir stock
    for item in items:
        PedidoItem.objects.create(
            pedido=pedido,
            articulo=item.articulo,
            cantidad=item.cantidad,
            precio=item.articulo.precio
        )
        item.articulo.cantidad -= item.cantidad
        item.articulo.save()

    # Vaciar carrito
    items.delete()

    # 👉 ahora pasamos pedido al contexto
    return render(request, 'pago_exitoso.html', {'pedido': pedido})


@login_required
def pago_fallido(request):
    return render(request, 'pago_fallido.html')


@login_required
def pagar_carrito(request):
    import stripe
    from django.conf import settings

    usuario = request.user.usuario
    carrito = Carrito.objects.get(usuario=usuario)
    items = carrito.items.all()

    if not items:
        return redirect('carrito')

    stripe.api_key = settings.STRIPE_SECRET_KEY
    total = int(carrito.total() * 100)

    intent = stripe.PaymentIntent.create(
        amount=total,
        currency='usd',
        metadata={'usuario_id': usuario.id}
    )

    context = {
        'client_secret': intent.client_secret,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'carrito': carrito,
        'total': carrito.total(),
        'items': items
    }

    return render(request, 'pago.html', context)