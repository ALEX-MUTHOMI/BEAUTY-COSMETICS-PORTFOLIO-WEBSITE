from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("checkout", "0001_initial"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="checkoutsession",
            name="checkout_se_customer_b2a808_idx",
        ),
        migrations.AddIndex(
            model_name="checkoutsession",
            index=models.Index(fields=["customer", "status"], name="checkout_sess_cust_status_idx"),
        ),
    ]
