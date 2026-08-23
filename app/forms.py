# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
from django import forms
from django.forms import formset_factory

from .models import CableCal, CableLineItem, ReelsList, TransportList


class CableCalForm(forms.ModelForm):
    """Order header: identity, transport, optional per-calc overrides."""

    class Meta:
        model = CableCal
        fields = ["order_num", "transport", "margin_override", "packing_override"]
        widgets = {
            "order_num": forms.TextInput(attrs={"class": "form-control"}),
            "transport": forms.Select(attrs={"class": "form-select"}),
            "margin_override": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1"}
            ),
            "packing_override": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
        }


class CableLineItemForm(forms.ModelForm):
    """One cable line in an order (entered via a formset).

    Fields are not required at the form level so that empty extra rows in the
    formset pass validation; the view skips rows without a diameter and
    compute_line() raises a user-facing error for rows missing other data.
    """

    class Meta:
        model = CableLineItem
        fields = ["cod", "name", "con_num", "order_len", "max_len", "mass", "diameter"]
        widgets = {
            "cod": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "con_num": forms.NumberInput(attrs={"class": "form-control"}),
            "order_len": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "max_len": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "mass": forms.NumberInput(attrs={"class": "form-control", "step": "0.001"}),
            "diameter": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False


CableLineItemFormSet = formset_factory(CableLineItemForm, extra=1, can_delete=True)


class ReelsListForm(forms.ModelForm):
    class Meta:
        model = ReelsList
        fields = [
            "name",
            "height",
            "width",
            "diameter",
            "diameter_neck",
            "length_neck",
            "reel_type",
            "mass",
            "max_load",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "height": forms.NumberInput(attrs={"class": "form-control"}),
            "width": forms.NumberInput(attrs={"class": "form-control"}),
            "diameter": forms.NumberInput(attrs={"class": "form-control"}),
            "diameter_neck": forms.NumberInput(attrs={"class": "form-control"}),
            "length_neck": forms.NumberInput(attrs={"class": "form-control"}),
            "reel_type": forms.Select(attrs={"class": "form-select"}),
            "mass": forms.NumberInput(attrs={"class": "form-control"}),
            "max_load": forms.NumberInput(attrs={"class": "form-control"}),
        }


class TransportListForm(forms.ModelForm):
    class Meta:
        model = TransportList
        fields = ["name", "length", "width", "height", "max_load"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "length": forms.NumberInput(attrs={"class": "form-control"}),
            "width": forms.NumberInput(attrs={"class": "form-control"}),
            "height": forms.NumberInput(attrs={"class": "form-control"}),
            "max_load": forms.NumberInput(attrs={"class": "form-control"}),
        }