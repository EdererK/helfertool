from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from copy import deepcopy

from .settings import BadgeSettings
from .permission import BadgePermission


@python_2_unicode_compatible
class BadgeRole(models.Model):
    badge_settings = models.ForeignKey(
        BadgeSettings,
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
    )

    latex_name = models.CharField(
        max_length=200,
        verbose_name=_("Name for LaTeX template"),
        help_text=_("This name is used for the LaTeX template."),
    )

    permissions = models.ManyToManyField(
        BadgePermission,
        blank=True,
    )

    def __str__(self):
        return self.name

    def duplicate(self, settings, permission_map):
        new_role = deepcopy(self)
        new_role.pk = None
        new_role.badge_settings = settings
        new_role.save()

        # update permissions to new objects
        new_permissions = []
        for perm in self.permissions.all():
            new_permissions.append(permission_map[perm])
        new_role.permissions.clear()
        new_role.permissions.add(*new_permissions)

        return new_role
