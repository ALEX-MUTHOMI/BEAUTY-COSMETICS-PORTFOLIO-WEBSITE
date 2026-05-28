# Generated manually for Phase 2B booking duration unit testing.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0002_booking_beautician_settlement"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="duration_minutes",
            field=models.PositiveSmallIntegerField(default=60),
        ),
    ]
