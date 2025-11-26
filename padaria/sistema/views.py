from django.core.mail import send_mail
from .models import Produto, SolicitacaoNotificacao
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Produto
from .forms import CadastroUsuarioForm, ProdutoForm
from django.contrib.auth import login
import requests, os
from dotenv import load_dotenv
from django.http import HttpResponse


def eh_distribuidor(user):
    return user.eh_distribuidor or user.is_superuser

def notifica(produto_nome,tipo_alteracao, distribuidor):
    load_dotenv()
    url = os.getenv("LAMBDA_URL")
    print(url)
    payload = {
        "tipo_alteracao": tipo_alteracao,
        "distribuidor":     distribuidor,
        "produto_nome":   produto_nome
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
        #notifica('tem em estoque') #ERA PRA TESTAR SÓ provavelmente a notifia vai mandar pra signals 
        produtos = Produto.objects.filter(distribuidor=request.user)
        return render(request, 'html/distribuidor.html', {'produtos': produtos})
    else:
        produtos = Produto.objects.all()
        return render(request, 'html/formulario_interesse.html', {
            'produtos': produtos,
            'email_inicial': request.user.email
        })

@login_required
@user_passes_test(eh_distribuidor) 
def atualizar_estoque(request, produto_id):
    if request.method == 'POST':
        produto = get_object_or_404(Produto, id=produto_id, distribuidor=request.user)
        nova_quantidade = int(request.POST.get('quantidade_adicional'))
        produto.quantidade_estoque += nova_quantidade
        produto.save() 
        
    return redirect('home')


def registro(request):
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
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

        if produto.esta_disponivel:
            try:
                notifica(produto.nome,'disponivel', produto.distribuidor.username)
            except Exception as e:
                print(f"Erro ao chamar notifica: {e}")
            
            send_mail(
                f'Seu item {produto.nome} está disponível!',
                'Olá! O item que você queria está disponível. Venha buscar na padaria.',
                'padaria@exemplo.com',
                [email],
            )
            return HttpResponse('funcionou')

        else:
            try:
                notifica(produto.nome,'chegou', produto.distribuidor.username)
            except Exception as e:
                print(f"Erro ao chamar notifica: {e}")

            SolicitacaoNotificacao.objects.create(
                produto=produto,
                email_cliente=email,
                status='pendente'
            )
            
            return HttpResponse('segura')
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
    produto = get_object_or_404(Produto, id=produto_id, distribuidor=request.user)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProdutoForm(instance=produto)
    
    return render(request, 'html/form_produto.html', {'form': form, 'titulo': f'Editar {produto.nome}'})