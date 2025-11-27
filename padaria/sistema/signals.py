# Crie um arquivo signals.py no seu app
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Produto, SolicitacaoNotificacao
from .views import notifica

@receiver(post_save, sender=Produto)
def notificar_clientes_na_reposicao(sender, instance, created, **kwargs):
    produto = instance

    if produto.esta_disponivel:
        solicitacoes_pendentes = SolicitacaoNotificacao.objects.filter(
            produto=produto, 
            status='pendente'
        )
        emails_para_enviar = []
        for solicitacao in solicitacoes_pendentes:
            emails_para_enviar.append(solicitacao.email_cliente)
            notifica(produto.nome,'abastecido', produto.distribuidor.username)
            solicitacao.status = 'notificado'
            solicitacao.save()


