from django.contrib import admin
from app_wed.models import Servicio, Categoria, Post

# Register your models here.
class Servicioadmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')

class Categoriaadmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')

class Postadmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')

admin.site.register(Servicio, Servicioadmin)
admin.site.register(Categoria, Categoriaadmin)
admin.site.register(Post, Postadmin)