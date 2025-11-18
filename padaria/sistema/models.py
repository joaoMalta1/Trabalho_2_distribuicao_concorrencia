from django.db import models
from django.contrib.auth.models import AbstractUser

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    quantidade_estoque = models.PositiveIntegerField(default=0)
    imgem = models.ImageField(upload_to='produtos/', blank=True, null=True)

    def __str__(self):
        return self.nome

    @property
    def esta_disponivel(self):
        return self.quantidade_estoque > 0

class Usuario(AbstractUser):
    eh_distribuidor = models.BooleanField(default=False, verbose_name="Sou Distribuidor")

    def __str__(self):
        return self.username

class SolicitacaoNotificacao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    email_cliente = models.EmailField()
    status = models.CharField(max_length=20, default='pendente') # pendente, notificado

    def __str__(self):
        return f"{self.email_cliente} quer {self.produto.nome}"