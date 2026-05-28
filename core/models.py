import uuid

from django.db import models


class AuditMixin(models.Model):
    """
    Abstract model mixin implementing:
    - Secure UUID4 primary keys to prevent numerical resource scraping and ID guessing.
    - Automatic creation and update auditing timestamps.
    - Soft-delete status flag to support GDPR 'Right to be Forgotten' without violating
      financial ledger and foreign key referential integrity constraints.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Cryptographically secure unique identifier.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        help_text="Timestamp when the database record was initialized.",
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when the database record was last saved."
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft-delete flag to support GDPR compliance while maintaining transaction records.",
    )

    class Meta:
        abstract = True
