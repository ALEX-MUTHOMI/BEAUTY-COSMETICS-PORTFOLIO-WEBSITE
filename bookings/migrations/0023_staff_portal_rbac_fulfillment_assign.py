# Generated for staff portal RBAC, fulfillment, assignment, and search indexes.

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("bookings", "0022_alter_staffactionauditevent_action_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="assigned_staff",
            field=models.ForeignKey(
                blank=True,
                help_text="Beautician (or staff) assigned for people routing — independent of resource capacity.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="assigned_bookings",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="booking",
            name="fulfillment_status",
            field=models.CharField(
                choices=[
                    ("not_started", "Not Started"),
                    ("attended", "Attended"),
                    ("in_service", "In Service"),
                    ("completed", "Completed"),
                    ("no_show", "No Show"),
                ],
                db_index=True,
                default="not_started",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="booking",
            name="fulfillment_updated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="booking",
            name="fulfillment_updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="fulfillment_updates",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterModelOptions(
            name="booking",
            options={
                "permissions": [
                    ("view_staff_portal", "Can view staff booking portal schedule"),
                    ("view_staff_booking", "Can view staff booking detail"),
                    ("view_staff_payment_summary", "Can view staff payment summary"),
                    ("view_staff_contact_details", "Can reveal staff contact details"),
                    ("manage_staff_booking_notes", "Can manage staff booking notes"),
                    ("confirm_staff_attendance", "Can confirm staff booking fulfillment / attendance"),
                    ("assign_staff_booking", "Can assign bookings to beauticians"),
                    ("download_staff_receipt", "Can download staff booking receipt PDF"),
                    ("view_staff_payments_desk", "Can access staff payments desk"),
                ],
            },
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(fields=["assigned_staff", "local_booking_date"], name="bookings_assigned_date_idx"),
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(fields=["fulfillment_status", "local_booking_date"], name="bookings_fulfill_date_idx"),
        ),
        migrations.AddIndex(
            model_name="customerprofile",
            index=models.Index(fields=["full_name_display"], name="bk_cust_display_name_idx"),
        ),
        migrations.AlterField(
            model_name="staffactionauditevent",
            name="action",
            field=models.CharField(
                choices=[
                    ("contact_reveal", "Contact Reveal"),
                    ("status_override", "Status Override"),
                    ("receipt_download", "Receipt Download"),
                    ("attendance_confirm", "Attendance Confirm"),
                    ("staff_assign", "Staff Assign"),
                ],
                max_length=64,
            ),
        ),
        migrations.CreateModel(
            name="StaffProfile",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Cryptographically secure unique identifier.",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        editable=False,
                        help_text="Timestamp when the database record was initialized.",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Timestamp when the database record was last saved.",
                    ),
                ),
                (
                    "is_deleted",
                    models.BooleanField(
                        default=False,
                        help_text="Soft-delete flag to support GDPR compliance while maintaining transaction records.",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("owner", "Owner"),
                            ("receptionist", "Receptionist"),
                            ("beautician", "Beautician"),
                        ],
                        db_index=True,
                        default="receptionist",
                        max_length=32,
                    ),
                ),
                ("display_name", models.CharField(blank=True, max_length=80)),
                (
                    "bookable_resource",
                    models.ForeignKey(
                        blank=True,
                        help_text="Optional link to a beautician BookableResource for capacity continuity.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="staff_profiles",
                        to="bookings.bookableresource",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="staff_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "booking_staff_profiles",
                "indexes": [models.Index(fields=["role"], name="staff_profile_role_idx")],
            },
        ),
    ]
