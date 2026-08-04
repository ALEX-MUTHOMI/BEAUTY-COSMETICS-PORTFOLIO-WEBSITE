# Generated manually for CI makemigrations --check (receipt_download audit choices).

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0021_privacy_rights_request"),
    ]

    operations = [
        migrations.AlterField(
            model_name="staffactionauditevent",
            name="action",
            field=models.CharField(
                choices=[
                    ("contact_reveal", "Contact Reveal"),
                    ("status_override", "Status Override"),
                    ("receipt_download", "Receipt Download"),
                ],
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="staffsecurityaudit",
            name="event_type",
            field=models.CharField(
                choices=[
                    ("login_success", "Login Success"),
                    ("login_failure", "Login Failure"),
                    ("login_rate_limited", "Login Rate Limited"),
                    ("logout", "Logout"),
                    ("session_expired", "Session Expired"),
                    ("password_reset_requested", "Password Reset Requested"),
                    ("password_reset_completed", "Password Reset Completed"),
                    ("reauth_success", "Reauth Success"),
                    ("reauth_failure", "Reauth Failure"),
                    ("contact_reveal", "Contact Reveal"),
                    ("receipt_download", "Receipt Download"),
                    ("permission_denied", "Permission Denied"),
                ],
                max_length=64,
            ),
        ),
    ]
