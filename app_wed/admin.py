from django.contrib import admin
from app_wed.models import (
    Servicio, Categoria, Post, 
    CarritoItem, Carrito, 
    Articulo, ArticuloVariante, Categoria_articulo, PedidoItem, Pedido
)

# Servicio
class ServicioAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')

# Categoría (BLOG)
class CategoriaAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')

# Post
class PostAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')

# Categoría de Artículos (TIENDA)
class CategoriaArticuloAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

# Artículo
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'creado')
    search_fields = ('nombre',)
    list_filter = ('categorias',)

# Variantes de artículo
class ArticuloVarianteAdmin(admin.ModelAdmin):
    list_display = ('articulo', 'color', 'talla', 'precio', 'cantidad')
    search_fields = ('articulo__nombre', 'color')
    list_filter = ('color', 'talla')

# Carrito
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario',)
    search_fields = ('usuario__user__username',)

# CarritoItem
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ('carrito', 'articulo', 'cantidad', 'subtotal')
    search_fields = ('articulo__articulo__nombre',)

class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    extra = 0
    readonly_fields = ('nombre_articulo', 'cantidad', 'precio', 'subtotal_display')

    # Mostrar subtotal en readonly
    def subtotal_display(self, obj):
        return obj.subtotal()
    subtotal_display.short_description = "Subtotal"


class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'total', 'estado', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('usuario__nombre', 'usuario__apellido')
    inlines = [PedidoItemInline]


# Registro en el panel de administración
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(Categoria, CategoriaAdmin)  # BLOG
admin.site.register(Post, PostAdmin)            # BLOG
admin.site.register(Categoria_articulo, CategoriaArticuloAdmin)  # ✅ TIENDA
admin.site.register(Articulo, ArticuloAdmin)
admin.site.register(ArticuloVariante, ArticuloVarianteAdmin)
admin.site.register(Carrito, CarritoAdmin)
admin.site.register(CarritoItem, CarritoItemAdmin)
