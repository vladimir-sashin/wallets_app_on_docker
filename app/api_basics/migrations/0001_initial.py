# Generated by Django 3.2.7 on 2021-10-01 11:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Wallet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "balance",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0.0, max_digits=10
                    ),
                ),
                (
                    "holder",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="users_wallet",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TransactionV2",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[("CRED", "Credit"), ("DEB", "Debit")],
                        default="CRED",
                        max_length=6,
                    ),
                ),
                (
                    "balance_before",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                (
                    "balance_after",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "recipient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipient_wallet",
                        to="api_basics.wallet",
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sender_wallet",
                        to="api_basics.wallet",
                    ),
                ),
                (
                    "wallet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="current_wallet",
                        to="api_basics.wallet",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="wallet",
            index=models.Index(fields=["name"], name="api_basics__name_0e50b5_idx"),
        ),
        migrations.AddIndex(
            model_name="wallet",
            index=models.Index(
                fields=["holder"], name="api_basics__holder__9b1584_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="wallet",
            index=models.Index(
                fields=["balance"], name="api_basics__balance_ab7e9c_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="transactionv2",
            index=models.Index(
                fields=["wallet", "timestamp"], name="api_basics__wallet__e29fc9_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="transactionv2",
            index=models.Index(
                fields=["wallet", "transaction_type", "timestamp"],
                name="api_basics__wallet__a7b189_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="transactionv2",
            index=models.Index(
                fields=["timestamp"], name="api_basics__timesta_5b5da6_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="transactionv2",
            index=models.Index(
                fields=["transaction_type", "timestamp"],
                name="api_basics__transac_333030_idx",
            ),
        ),
    ]
