from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Item, Inventory

from badges.models import Badge
from registration.forms.fields import UserSelectField


class InventoryBarcodeForm(forms.Form):
    barcode = forms.CharField(
        label=_("Barcode"),
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'autofocus': ''}),
    )

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        self.item = None

        super(InventoryBarcodeForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(InventoryBarcodeForm, self).__init__()

        barcode = self.cleaned_data.get('barcode')

        # check if badge exists
        try:
            available = self.event.inventory_settings.available_inventory. \
                values('id')
            self.item = Item.objects.get(inventory__in=available,
                                         barcode=barcode)
        except Item.DoesNotExist:
            raise ValidationError(_("There is no item with this barcode for "
                                    "this event."))


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        exclude = []
        field_classes = {
            'admins': UserSelectField,
        }


class InventoryDeleteForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = []

    def delete(self):
        self.instance.delete()


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = ['inventory', ]

    def __init__(self, *args, **kwargs):
        self.inventory = kwargs.pop('inventory')

        super(ItemForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ItemForm, self).save(False)  # inventory is missing

        instance.inventory = self.inventory

        if commit:
            instance.save()

        return instance


class ItemDeleteForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = []

    def delete(self):
        self.instance.delete()
