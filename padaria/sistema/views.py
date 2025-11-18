from django.core.mail import send_mail
from .models import Produto, SolicitacaoNotificacao
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Produto
from .forms import CadastroUsuarioForm 
from django.contrib.auth import login



def eh_distribuidor(user):
    return user.eh_distribuidor or user.is_superuser

@login_required
def home(request):
    if request.user.eh_distribuidor:
        produtos = Produto.objects.all()
        return render(request, 'html/dashboard_distribuidor.html', {'produtos': produtos})
    else:
        produtos = Produto.objects.all()
        return render(request, 'html/formulario_interesse.html', {
            'produtos': produtos,
            'email_inicial': request.user.email
        })

# View exclusiva para Distribuidores atualizarem estoque
@login_required
@user_passes_test(eh_distribuidor) # Bloqueia se não for distribuidor
def atualizar_estoque(request, produto_id):
    if request.method == 'POST':
        produto = get_object_or_404(Produto, id=produto_id)
        nova_quantidade = int(request.POST.get('quantidade_adicional'))
        
        # Atualiza o estoque
        produto.quantidade_estoque += nova_quantidade
        produto.save() 
        # O sinal (signals.py) será disparado aqui automaticamente!
        
    return redirect('home')


def registro(request):
    if request.method == 'POST':
        # Usamos o nosso form customizado
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            # O campo eh_distribuidor já foi salvo automaticamente pelo form!
            login(request, user)
            return redirect('home')
    else:
        form = CadastroUsuarioForm()

    return render(request, 'registration/register.html', {'form': form})


def solicitar_produto(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        produto_id = request.POST.get('produto_id')
        
        produto = Produto.objects.get(id=produto_id)

        # AQUI ESTÁ A LÓGICA PRINCIPAL:
        
        if produto.esta_disponivel:
            # CENÁRIO 1: Item está disponível
            send_mail(
                f'Seu item {produto.nome} está disponível!',
                'Olá! O item que você queria está disponível. Venha buscar na padaria.',
                'padaria@exemplo.com',
                [email],
            )
            # Retorna uma página de sucesso
            return render(request, 'sucesso_disponivel.html')

        else:
            # CENÁRIO 2: Item não está disponível
            
            # Cria um registro de "lista de espera"
            SolicitacaoNotificacao.objects.create(
                produto=produto,
                email_cliente=email,
                status='pendente'
            )
            
            # Apenas informa o usuário que ele será notificado
            return render(request, 'sucesso_indisponivel.html')

    # Se for GET, apenas mostra a página com o formulário
    produtos = Produto.objects.all()
    return render(request, 'formulario_interesse.html', {'produtos': produtos})