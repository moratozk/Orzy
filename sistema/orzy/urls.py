"""Endereços do sistema. Os de /static/ são do WhiteNoise (ver settings.py)."""

from django.urls import path

from contas import views as contas
from publico import views as publico
from relatorios import views as relatorios

urlpatterns = [
    path("", publico.inicio),
    path("privacidade", publico.texto_legal, {"rota": "privacidade"}),
    path("termos", publico.texto_legal, {"rota": "termos"}),
    path("robots.txt", publico.robots),
    path("saude", publico.saude),
    path("entrar", contas.entrar),
    path("retorno", contas.retorno),
    path("sair", contas.sair),
    path("relatorio", relatorios.formulario),
    path("relatorio/gerar", relatorios.gerar),
    path("relatorio/<str:relatorio_id>", relatorios.ver),
    path("relatorio/<str:relatorio_id>/andamento.json", relatorios.andamento),
    path("relatorio/<str:relatorio_id>/csv", relatorios.planilha),
    path("historico", relatorios.historico),
    path("historico/apagar", relatorios.apagar_historico),
    path("historico/<int:guardado_id>", relatorios.ver_historico),
    path("contagens", relatorios.contagens_do_beta),
]

handler400 = "publico.views.pedido_invalido"
handler403 = "publico.views.proibido"
handler404 = "publico.views.nao_encontrado"
handler500 = "publico.views.erro_interno"
