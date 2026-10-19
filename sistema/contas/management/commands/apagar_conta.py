"""Apagar uma conta a pedido, para quem pede por e-mail: o mesmo que o "Desconectar e apagar tudo" da página Sua conta.

    python manage.py apagar_conta 123456789

Apaga a conta, o acesso guardado e todo o histórico, pelo banco, e pede ao Mercado Livre para tirar a permissão do
Orzy. Pergunta antes; com --no-input apaga sem perguntar (na hospedagem, onde ninguém digita).

O comando roda fora do servidor, e as sessões ficam na memória dele: uma sessão aberta da conta continua até Sair, até
8 horas depois do login ou até o servidor reiniciar. Sem a conta, ela não guarda mais nada.
"""

from contas import acesso
from contas.models import Conta
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Apaga uma conta com tudo o que é dela, como o "Desconectar e apagar tudo" (para pedidos por e-mail).'

    def add_arguments(self, parser):
        parser.add_argument("numero", type=int, help="o número da conta no Mercado Livre")
        parser.add_argument("--no-input", "--noinput", action="store_false", dest="perguntar",
                            help="apaga sem perguntar")

    def handle(self, *args, numero, perguntar, **opcoes):
        conta = Conta.objects.filter(ml_user_id=numero).first()
        if conta is None:
            raise CommandError(f"Não existe conta com o número {numero} no Orzy. Nada foi apagado.")
        n = conta.relatorios.count()
        historico = f"o histórico ({n} relatório{'' if n == 1 else 's'})"
        if perguntar:
            try:
                resposta = input(f"Apagar a conta {numero} ({conta.apelido or 'sem apelido'}), o acesso guardado e "
                                 f"{historico}? Para confirmar, digite o número da conta: ")
            except EOFError:
                raise CommandError("Nada foi apagado: ninguém para confirmar. Para apagar sem perguntar, use "
                                   "--no-input.") from None
            if resposta.strip() != str(numero):
                raise CommandError("Nada foi apagado.")
        confirmou = acesso.desconectar(numero)
        self.stdout.write(f"Apaguei a conta {numero}, o acesso guardado e {historico}.")
        if confirmou:
            self.stdout.write("O Mercado Livre confirmou que tirou a permissão do Orzy.")
        else:
            self.stdout.write("Não consegui tirar a permissão do Orzy no Mercado Livre: a pessoa pode tirar por lá.")
