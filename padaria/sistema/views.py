from django.shortcuts import render

# Create your views here.
def home(request):
    # 1. Busca todos os produtos salvos no banco de dados
    produtos = Produto.objects.all()

    # 2. Cria um "contexto" (um dicionário) para enviar os dados ao template
    contexto = {
        'produtos': produtos
    }

    # 3. Renderiza o template, passando os dados do contexto
    return render(request, 'html/formulario_interesse.html', contexto)


# Em views.py (exemplo simplificado)
from django.shortcuts import render
from django.core.mail import send_mail
from .models import Produto, SolicitacaoNotificacao

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