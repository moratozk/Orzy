"""Configuração do Django para o sistema do Orzy. Os valores do site vêm das variáveis de ambiente (configuracao.py)."""

import secrets
from pathlib import Path

from django.utils.csp import CSP

from . import configuracao

PASTA = Path(__file__).resolve().parent.parent  # sistema/
RAIZ = PASTA.parent  # a pasta do Orzy

ORZY = configuracao.carregar()

# Sorteada a cada vez que o servidor liga: nada guardado depende dela (as sessões ficam só na memória e somem ao
# reiniciar, e o histórico não é assinado).
SECRET_KEY = secrets.token_urlsafe(50)
DEBUG = False
ALLOWED_HOSTS = [ORZY.host]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "publico",
    "contas",
    "relatorios",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Os arquivos de /static/ saem daqui, já comprimidos, sem passar pelo resto.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # As páginas saem comprimidas: menos dados até o Brasil, que a hospedagem cobra por GiB.
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Confere o endereço (Host) de todo pedido com o de ORZY_URL_BASE: o resto recebe 400.
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.csp.ContentSecurityPolicyMiddleware",
    "orzy.seguranca.SemGuardarNoNavegador",
]

ROOT_URLCONF = "orzy.urls"
WSGI_APPLICATION = "orzy.wsgi.application"
APPEND_SLASH = False

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": ["orzy.contexto.orzy"]},
}]

DATABASES = {"default": {
    **ORZY.banco,
    "CONN_MAX_AGE": 60,  # reaproveita a conexão com o banco por 1 minuto (o banco fica em outro servidor)
    "CONN_HEALTH_CHECKS": True,
}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "pt-br"
USE_I18N = False
TIME_ZONE = "UTC"  # as datas ficam em UTC; as páginas mostram o horário de Brasília (relatorios/datas.py)
USE_TZ = True

# Arquivos de /static/ com o resumo do conteúdo no nome: o navegador guarda e só baixa de novo quando mudam.
STATIC_URL = "static/"
STATIC_ROOT = PASTA / "static-pronto"  # onde o collectstatic junta os arquivos (fora do Git)
STORAGES = {"staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}}

# Sessões só na memória do servidor (contas/sessoes.py): o login do Mercado Livre nunca vai para disco nem navegador.
SESSION_ENGINE = "contas.sessoes"
SESSION_COOKIE_NAME = "orzy_sessao"  # o único cookie do site, como promete a Política de Privacidade
SESSION_COOKIE_AGE = ORZY.horas_sessao * 3600
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = ORZY.seguro

# Proteção contra pedidos de outros sites: o código fica na sessão (sem um segundo cookie) e a origem é conferida.
CSRF_USE_SESSIONS = True
CSRF_TRUSTED_ORIGINS = [ORZY.origem]
CSRF_FAILURE_VIEW = "publico.views.recusado"

SECURE_CONTENT_TYPE_NOSNIFF = True
# "same-origin" e não "no-referrer": com "no-referrer" o navegador manda "Origin: null" nos formulários do próprio
# site e todo pedido seria recusado. Com "same-origin", outros sites continuam sem receber o endereço de onde a
# pessoa veio (nem o código do Mercado Livre do /retorno).
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
# Nada de estilo ou script escrito dentro da página: só os arquivos do próprio site.
SECURE_CSP = {
    "default-src": [CSP.SELF],
    "script-src": [CSP.SELF],
    "style-src": [CSP.SELF],
    "img-src": [CSP.SELF, "data:"],
    "form-action": [CSP.SELF],
    "frame-ancestors": [CSP.NONE],
    "base-uri": [CSP.NONE],
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 10_000  # bytes: os formulários do site são pequenos

# A Política de Privacidade e os Termos de Uso: o site lê os textos daqui a cada pedido (publico/legal.py).
ORZY_PASTA_LEGAL = RAIZ / "docs" / "legal"

# Registro do servidor: data, hora, página pedida e erros, sem a busca do endereço (o ?code= do Mercado Livre).
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simples": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}},
    "filters": {"sem_busca": {"()": "orzy.seguranca.SemBuscaNoRegistro"},
                "uma_linha": {"()": "orzy.seguranca.UmaLinhaSo"}},
    "handlers": {"tela": {"class": "logging.StreamHandler", "formatter": "simples"}},
    "root": {"handlers": ["tela"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": [], "level": "INFO", "propagate": True},
        "django.security.DisallowedHost": {"handlers": ["tela"], "filters": ["uma_linha"], "propagate": False},
        # O servidor de teste (runserver) escreve o endereço inteiro de cada pedido: o filtro tira a busca.
        "django.server": {"handlers": ["tela"], "filters": ["sem_busca"], "level": "INFO", "propagate": False},
    },
}

TEST_RUNNER = "orzy.testes.Executor"
