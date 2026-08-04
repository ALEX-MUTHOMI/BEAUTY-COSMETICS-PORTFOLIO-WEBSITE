from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0015_alter_booking_booking_type_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="booking",
            options={
                "permissions": [
                    ("view_staff_portal", "Can view staff booking portal schedule"),
                    ("view_staff_booking", "Can view staff booking detail"),
                    ("view_staff_payment_summary", "Can view staff payment summary"),
                    ("view_staff_contact_details", "Can reveal staff contact details"),
                    ("manage_staff_booking_notes", "Can manage staff booking notes"),
                ],
            },
        ),
    ]
