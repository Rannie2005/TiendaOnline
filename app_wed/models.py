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
