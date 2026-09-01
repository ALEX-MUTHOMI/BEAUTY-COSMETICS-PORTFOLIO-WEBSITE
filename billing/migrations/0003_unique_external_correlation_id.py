from django.db import migrations, models


def _apply_unique_correlation(apps, schema_editor):
    table = "billing_ledger_transactions"
    index_name = "uniq_ledger_external_correlation_id"
    old_index = "billing_led_externa_6c94fc_idx"
    with schema_editor.connection.cursor() as cursor:
        if schema_editor.connection.vendor == "postgresql":
            cursor.execute(f"DROP INDEX IF EXISTS {old_index}")
            cursor.execute(
                f"CREATE UNIQUE INDEX {index_name} ON {table} (external_correlation_id) "
                "WHERE external_correlation_id IS NOT NULL"
            )
        else:
            # SQLite: avoid remake_table (other apps use Postgres EXCLUDE constraints).
            cursor.execute(f"DROP INDEX IF EXISTS {old_index}")
            cursor.execute(
                f"CREATE UNIQUE INDEX IF NOT EXISTS {index_name} ON {table} (external_correlation_id) "
                "WHERE external_correlation_id IS NOT NULL"
            )


def _revert_unique_correlation(apps, schema_editor):
    table = "billing_ledger_transactions"
    index_name = "uniq_ledger_external_correlation_id"
    old_index = "billing_led_externa_6c94fc_idx"
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
        if schema_editor.connection.vendor == "postgresql":
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {old_index} ON {table} (external_correlation_id)")
        else:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {old_index} ON {table} (external_correlation_id)")


class Migration(migrations.Migration):
    dependencies = [
        ("billing", "0002_financial_truth_layer"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveIndex(
                    model_name="ledgertransaction",
                    name="billing_led_externa_6c94fc_idx",
                ),
                migrations.AddConstraint(
                    model_name="ledgertransaction",
                    constraint=models.UniqueConstraint(
                        condition=models.Q(("external_correlation_id__isnull", False)),
                        fields=("external_correlation_id",),
                        name="uniq_ledger_external_correlation_id",
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(_apply_unique_correlation, _revert_unique_correlation),
            ],
        ),
    ]
