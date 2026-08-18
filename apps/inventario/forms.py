from django import forms
from .models import Producto, Categoria


class FormProducto(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'categoria', 'precio_base',
                  'stock_actual', 'stock_minimo', 'sku', 'imagen', 'es_insumo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }


class FormCategoria(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'padre']
