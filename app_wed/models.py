from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Servicio(models.Model):
    titulo = models.CharField(max_length=50)
    contenido = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to='servicio')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'servicio'
        verbose_name_plural = 'servicios'

    def __str__(self):
        return self.titulo
    

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.nombre
    

class Post(models.Model):
    titulo = models.CharField(max_length=70)
    contenido = models.CharField(max_length=300)
    imagen = models.ImageField(upload_to='blog', null=True, blank=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria =models.ManyToManyField(Categoria)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def __str__(self):
        return self.titulo
    

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='fotos/', blank=True, null=True)  
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=30)
    cedula = models.IntegerField()
    telefono = models.CharField(max_length=15)  
    direccion = models.CharField(max_length=255, blank=True, null=True)
    latitud = models.FloatField(blank=True, null=True)   # Para Google Maps
    longitud = models.FloatField(blank=True, null=True)  # Para Google Maps

    def __str__(self):
        return f"{self.user.username} - {self.nombre} {self.apellido}"



class Categoria_articulo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre


class Articulo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    categorias = models.ManyToManyField(Categoria_articulo, related_name="articulos")
    imagen_principal = models.ImageField(upload_to="articulos/", blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    # 👇 Métodos útiles para mostrar rangos de precios
    def precio_minimo(self):
        return self.variantes.aggregate(models.Min("precio"))["precio__min"]

    def precio_maximo(self):
        return self.variantes.aggregate(models.Max("precio"))["precio__max"]


class ArticuloVariante(models.Model):
    TALLAS = [
        ("XS", "XS"),
        ("S", "S"),
        ("M", "M"),
        ("L", "L"),
        ("XL", "XL"),
        ("XXL", "XXL"),
        ("UNICA", "Talla Única"),
    ]

    articulo = models.ForeignKey(Articulo, related_name="variantes", on_delete=models.CASCADE)
    color = models.CharField(max_length=30)
    talla = models.CharField(max_length=10, choices=TALLAS)
    cantidad = models.PositiveIntegerField(default=0)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    imagen = models.ImageField(upload_to="articulos/variantes/", blank=True, null=True)

    def __str__(self):
        return f"{self.articulo.nombre} - {self.color} - {self.talla}"

    # 🚨 Alerta de stock bajo
    def stock_alerta(self):
        if self.cantidad == 0:
            return "❌ Agotado"
        elif self.cantidad < 10:
            return f"⚠️ Casi agotado: quedan {self.cantidad}"
        return ""


class Carrito(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Carrito de {self.usuario.nombre}"

    def total(self):
        return sum(item.subtotal() for item in self.items.all())


class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name="items")
    articulo = models.ForeignKey(ArticuloVariante, on_delete=models.CASCADE)  # ✅ apunta a variante
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('carrito', 'articulo')

    def subtotal(self):
        return self.cantidad * self.articulo.precio

    def __str__(self):
        return f"{self.cantidad} x {self.articulo}"
    

# Tabla para registrar los pedidos/pagos
class Pedido(models.Model):
    ESTADOS = [
    ('pendiente', 'Pendiente'),
    ('pagado', 'Pagado'),
    ('enviado', 'Enviado'),
    ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    stripe_payment_id = models.CharField(max_length=100, blank=True, null=True)  # ID de Stripe

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.user.username} - {self.estado}"


# Tabla para registrar cada item de un pedido
class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    articulo = models.ForeignKey(ArticuloVariante, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def subtotal(self):
        if self.precio is None:
            return 0
        return self.cantidad * self.precio
    
    def nombre_articulo(self):
        return f"{self.articulo.articulo.nombre} - {self.articulo.color} - {self.articulo.talla}"
    nombre_articulo.short_description = "Artículo"