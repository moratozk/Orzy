"""Configuração do gunicorn, o servidor do sistema na hospedagem. Ele lê este arquivo sozinho quando liga de dentro da
pasta sistema/ (gunicorn orzy.wsgi).

Um processo só: as sessões com o login e os relatórios em andamento ficam na memória dele. Com dois, cada pedido
cairia num processo diferente e a pessoa perderia o login. Pelo mesmo motivo, o processo não reinicia sozinho depois
de um número de pedidos, e o sistema é carregado dentro dele (as limpezas das sessões precisam estar no mesmo
processo que as sessões).
"""

import os

bind = f"{os.environ.get('ORZY_HOST', '0.0.0.0')}:{os.environ.get('PORT', '8000')}"
workers = 1
worker_class = "gthread"
threads = 8  # pedidos ao mesmo tempo; os relatórios rodam em segundo plano, fora desta conta
preload_app = False
max_requests = 0
control_socket_disable = True  # sem o controle de fora, que poderia ligar um segundo processo
timeout = 60  # um processo travado por 60 segundos é reiniciado (e quem estava dentro conecta de novo)

# Uma linha por pedido: data, método, página sem a busca (o ?code= do Mercado Livre), resposta, tamanho e tempo.
# Sem o IP de quem pediu, como promete a Política de Privacidade.
accesslog = "-"
access_log_format = '%(t)s "%(m)s %(U)s" %(s)s %(B)s %(M)sms'
