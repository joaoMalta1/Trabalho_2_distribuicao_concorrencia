from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Produto

class CadastroUsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'eh_distribuidor')

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        # Listamos os campos que o distribuidor pode mexer
        fields = ['nome', 'descricao', 'quantidade_estoque', 'imgem']
        
        # Opcional: deixar o visual mais bonito com widgets
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }