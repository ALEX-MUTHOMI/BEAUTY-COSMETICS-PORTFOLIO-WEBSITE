# Generated manually for Phase 2B customer-to-beautician settlement verification.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="beautician_name",
            field=models.CharField(default="Assigned beautician", max_length=128),
        ),
        migrations.AddField(
            model_name="booking",
            name="beautician_payout_phone",
            field=models.CharField(default="+254700000000", max_length=15),
        ),
        migrations.AddField(
            model_name="booking",
            name="paid_to_beautician_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
