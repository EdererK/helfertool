from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
import uuid


class Link(models.Model):
    """ Link to some shifts for registration

    Columns:
        :id: Primary key, UUID
        :event: The event
        :shifts: Shifts that are linked
        :creator: User that created the link
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    event = models.ForeignKey(
        'Event',
    )

    shifts = models.ManyToManyField(
        'Shift',
    )

    creator = models.ForeignKey(
        User,
    )

    usage = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Usage"),
    )
