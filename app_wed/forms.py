from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['foto', 'nombre', 'apellido', 'cedula', 'telefono', 'direccion', 'latitud', 'longitud']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'cedula': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cédula'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección exacta'}),
            'latitud': forms.HiddenInput(),   # Se llenará desde el mapa
            'longitud': forms.HiddenInput(),  # Se llenará desde el mapa
        }

    foto = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))