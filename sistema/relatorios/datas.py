"""Datas no horário de Brasília, o do calendário de quem usa o Orzy. O banco guarda em UTC."""

from datetime import datetime, timedelta, timezone

BRASILIA = timezone(timedelta(hours=-3))  # o Brasil não tem horário de verão desde 2019


def agora():
    return datetime.now(timezone.utc)


def hoje(momento=None):
    """O dia de agora (ou do momento) no horário de Brasília."""
    return (momento or agora()).astimezone(BRASILIA).date()


def em_brasilia(momento):
    return momento.astimezone(BRASILIA)
