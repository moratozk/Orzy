"""
Passo 1: conecta este programa à sua conta do Mercado Livre.

Como usar (no Prompt de Comando, dentro desta pasta):
    python conectar.py             primeira vez, ou para entrar de novo
    python conectar.py --refazer   para digitar o Client ID e o Secret de novo
"""

import getpass
import secrets
import sys
import webbrowser

import ml_api


def perguntar(texto, padrao=None):
    sufixo = f" [Enter = {padrao}]" if padrao else ""
    while True:
        resposta = input(f"{texto}{sufixo}: ").strip()
        if resposta:
            return resposta
        if padrao is not None:
            return padrao
        print("  Esse campo é obrigatório.")


def perguntar_secreto(texto):
    """Como perguntar(), mas sem mostrar o que foi colado, para a chave não aparecer num print da tela."""
    if not sys.stdin.isatty():
        return perguntar(texto)
    print("  Ao colar, a chave não aparece na tela. É normal: cole e aperte Enter.")
    while True:
        resposta = getpass.getpass(f"{texto}: ").strip()
        if resposta:
            return resposta
        print("  Esse campo é obrigatório.")


def configurar():
    print("\n=== Dados do seu app no Mercado Livre ===")
    print("Estão em developers.mercadolivre.com.br > Minhas aplicações > seu app.\n")
    client_id = perguntar("Client ID (o número do app)")
    client_secret = perguntar_secreto("Client Secret (a chave secreta)")
    redirect = perguntar("Redirect URI (idêntica à cadastrada no app)", ml_api.REDIRECT_PADRAO)
    pkce = perguntar("Você ativou o PKCE no app? (s/n)", "n").lower().startswith("s")
    config = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect,
        "usar_pkce": pkce,
    }
    ml_api.salvar_config(config)
    print("Dados salvos em config.json (não compartilhe esse arquivo).")
    return config


def main():
    refazer = "--refazer" in sys.argv
    config = None if refazer else ml_api.carregar_config()
    if not config:
        config = configurar()

    state = secrets.token_urlsafe(16)
    verifier, challenge = ml_api.gerar_pkce() if config.get("usar_pkce") else (None, None)
    url = ml_api.montar_url_autorizacao(config, state, challenge)

    print("\n=== Login no Mercado Livre ===")
    print("1. Vou abrir o navegador. Entre com a conta DONA dos anúncios e clique em Permitir.")
    print(f"2. O navegador vai para {config['redirect_uri']} com um código no endereço (code=TG-...).")
    print("3. Copie o endereço INTEIRO da barra do navegador e cole aqui embaixo.")
    print("   Faça isso logo: o código vale poucos minutos.\n")
    print("Se o navegador não abrir, copie este link e abra manualmente:")
    print(url + "\n")
    webbrowser.open(url)

    colado = perguntar("Cole aqui o endereço")
    try:
        code = ml_api.extrair_code(colado, state)
        tokens = ml_api.trocar_code_por_token(config, code, verifier)
        eu = ml_api.MercadoLivre().obter_usuario()
    except ml_api.ErroML as e:
        print("\nNão deu certo:", e)
        sys.exit(1)

    print(f"\nPronto! Conectado como {eu.get('nickname')} (ID {eu.get('id')}).")
    if tokens.get("refresh_token"):
        print("O login se renova sozinho. Agora rode: python meus_anuncios.py")
    else:
        print("Atenção: o app está sem o fluxo 'Refresh Token', então este login vale só 6 horas.\n"
              "Marque Refresh Token em Fluxos OAuth, no app, e rode python conectar.py de novo.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelado.")
        sys.exit(1)
