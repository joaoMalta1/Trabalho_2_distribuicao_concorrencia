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
from django.contrib import messages
from django.conf import settings
import base64

def eh_distribuidor(user):
    return user.eh_distribuidor or user.is_superuser

def notifica(produto_nome, tipo_alteracao, distribuidor):
    load_dotenv()
    url = os.getenv("LAMBDA_URL")
    payload = {
        "tipo_alteracao": tipo_alteracao,
        "distribuidor":     distribuidor,
        "produto_nome":   produto_nome
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
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
            return redirect('home')

        else:
            try:
                notifica(produto.nome,'sem estoque', produto.distribuidor.username)
            except Exception as e:
                print(f"Erro ao chamar notifica: {e}")
            SolicitacaoNotificacao.objects.create(
                produto=produto,
                email_cliente=email,
                status='pendente'
            )
            return redirect('home')
    produtos = Produto.objects.all()
    return render(request, 'formulario_interesse.html', {'produtos': produtos})


@login_required
@user_passes_test(eh_distribuidor)
def cadastrar_produto(request):
    if request.method == 'POST':
        load_dotenv()
        form = ProdutoForm(request.POST, request.FILES)

        if form.is_valid():
            produto = form.save(commit=False)
            arquivo_upload = request.FILES.get('arquivo_imagem')
            if arquivo_upload:
                try:
                    arquivos = {
                        'file': (arquivo_upload.name, arquivo_upload, arquivo_upload.content_type)}

                    response = requests.post(
                        os.getenv("LAMBD_IMG"), 
                        files=arquivos,
                        timeout=10
                    )

                    if response.status_code == 200:
                        dados = response.json()
                        produto.imagem_base64 = dados.get('base64')
                        print("--- Conversão feita com sucesso pela AWS! ---")
                    else:
                        print(f"Erro Lambda: {response.text}")
                        messages.error(request, "A AWS recusou a imagem. Verifique o formato.")
                        return render(request, 'html/form_produto.html', {'form': form, 'titulo': 'Novo Produto'})
                
                except requests.exceptions.RequestException as e:
                    print(f"Erro de conexão com AWS: {e}")
                    messages.error(request, "Erro ao conectar com a nuvem.")
                    return render(request, 'html/form_produto.html', {'form': form, 'titulo': 'Novo Produto'})
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