from django.core.mail import send_mail
from .models import Produto, SolicitacaoNotificacao
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Produto
from .forms import CadastroUsuarioForm, ProdutoForm
from django.contrib.auth import login
import requests, os
from dotenv import load_dotenv



def eh_distribuidor(user):
    return user.eh_distribuidor or user.is_superuser

def notifica(crud):
    # if crud == 'create':
    #     print("Criou um novo produto")
    # elif crud == 'tem em estoque':
    #     print("Atualizou um produto")
    # elif crud == 'delete':
    #     print("Deletou um produto")
    # elif crud == 'saiu estoque':
    #     print("Produto saiu do estoque")
    load_dotenv()
    url = os.getenv("LAMBD_URL")
    print(url)
    payload = {
        "tipo_alteracao": "chegou",
        "distribuidor": "Pãozinho bom",
        "produto_nome": "Açucar"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Sucesso!")
            print(response.json()) 
        else:
            print(f"Erro {response.status_code}:")
            print(response.text)

    except Exception as e:
        print(f"Erro na requisição: {e}")




@login_required
def home(request):
    if request.user.eh_distribuidor:
        notifica('tem em estoque') #ERA PRA TESTAR SÓ provavelmente a notifia vai mandar pra signals 
        produtos = Produto.objects.filter(distribuidor=request.user)
        return render(request, 'html/distribuidor.html', {'produtos': produtos})
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
        # MUDANÇA 4: Segurança aqui também. Só repõe estoque do que é seu.
        produto = get_object_or_404(Produto, id=produto_id, distribuidor=request.user)
        
        nova_quantidade = int(request.POST.get('quantidade_adicional'))
        produto.quantidade_estoque += nova_quantidade
        produto.save() 
        
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


@login_required
@user_passes_test(eh_distribuidor)
def cadastrar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.distribuidor = request.user
            produto.save()
            return redirect('home')
    else:
        form = ProdutoForm()
    
    return render(request, 'html/form_produto.html', {'form': form, 'titulo': 'Novo Produto'})

@login_required
@user_passes_test(eh_distribuidor)
def editar_produto(request, produto_id):
    # MUDANÇA 3: Só permite pegar o produto se o ID for correto E o dono for o usuário logado
    # Se ele tentar editar o produto de outro, vai dar Erro 404 (Não encontrado)
    produto = get_object_or_404(Produto, id=produto_id, distribuidor=request.user)
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProdutoForm(instance=produto)
    
    return render(request, 'html/form_produto.html', {'form': form, 'titulo': f'Editar {produto.nome}'})