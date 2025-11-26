# Crie um arquivo signals.py no seu app
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Produto, SolicitacaoNotificacao

@receiver(post_save, sender=Produto)
def notificar_clientes_na_reposicao(sender, instance, created, **kwargs):
    produto = instance

    if produto.esta_disponivel:
        # Busca todas as solicitações pendentes para este produto
        solicitacoes_pendentes = SolicitacaoNotificacao.objects.filter(
            produto=produto, 
            status='pendente'
        )
        
        emails_para_enviar = []
        for solicitacao in solicitacoes_pendentes:
            emails_para_enviar.append(solicitacao.email_cliente)

            solicitacao.status = 'notificado'
            solicitacao.save()

        if emails_para_enviar:
            # Envia o e-mail para todos os clientes de uma vez
            send_mail(
                f'O item {produto.nome} chegou!',
                f'Olá! O item {produto.nome} que você estava esperando chegou na padaria.',
                'padaria@exemplo.com',
                emails_para_enviar, # Lista de e-mails
            )