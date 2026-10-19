"""Cada relatório guardado passa a ser de uma conta (contas.Conta) e sai com ela, pelo próprio banco.

Os relatórios que já estavam guardados (de antes do passo 2 da fase 4) ganham uma conta com o mesmo número, sem acesso
guardado: quem conectar de novo encontra o histórico; quem não conectar sai com a limpeza das contas sem acesso.
"""

import django.db.models.deletion
from django.db import migrations, models
from django.utils import timezone


def criar_as_contas(apps, schema_editor):
    Conta = apps.get_model("contas", "Conta")
    RelatorioGuardado = apps.get_model("relatorios", "RelatorioGuardado")
    agora = timezone.now()
    numeros = RelatorioGuardado.objects.values_list("ml_user_id", flat=True).distinct()
    for numero in numeros:
        conta, _ = Conta.objects.get_or_create(
            ml_user_id=numero,
            defaults={"criada_em": agora, "conectada_em": agora, "sem_acesso_desde": agora})
        RelatorioGuardado.objects.filter(ml_user_id=numero).update(conta=conta)


def voltar_os_numeros(apps, schema_editor):
    RelatorioGuardado = apps.get_model("relatorios", "RelatorioGuardado")
    for guardado in RelatorioGuardado.objects.select_related("conta"):
        guardado.ml_user_id = guardado.conta.ml_user_id
        guardado.save(update_fields=["ml_user_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("contas", "0001_initial"),
        ("relatorios", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="relatorioguardado",
            name="ml_user_id",
            field=models.BigIntegerField(db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="relatorioguardado",
            name="conta",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.DB_CASCADE,
                related_name="relatorios",
                to="contas.conta",
            ),
        ),
        migrations.RunPython(criar_as_contas, voltar_os_numeros),
        migrations.AlterField(
            model_name="relatorioguardado",
            name="conta",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DB_CASCADE,
                related_name="relatorios",
                to="contas.conta",
            ),
        ),
        migrations.RemoveField(
            model_name="relatorioguardado",
            name="ml_user_id",
        ),
        migrations.AlterField(
            model_name="anuncioguardado",
            name="relatorio",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DB_CASCADE,
                related_name="anuncios",
                to="relatorios.relatorioguardado",
            ),
        ),
    ]
