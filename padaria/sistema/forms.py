from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Produto

class CadastroUsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'eh_distribuidor')

class ProdutoForm(forms.ModelForm):
    arquivo_imagem = forms.FileField(required=False, label="Imagem do Produto")

    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'quantidade_estoque'] 
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }