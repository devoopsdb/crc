from django import forms
from django.forms import ModelForm
from .models import *


class ReelsListForm(forms.ModelForm):
    class Meta:
        model = ReelsList
        fields = ['name', 'height', 'width', 'diameter', 'diameter_neck', 'length_neck', 'reel_type', 'mass', 'max_load']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'style': 'width: 200px; border: 0px; height: 30px;'}),
            'height': forms.NumberInput(attrs={'class': 'form-input', 'style': 'width: 70px; border: 0px; height: 30px;'}),
            'width': forms.NumberInput(attrs={'class': 'form-input', 'style': 'width: 70px; border: 0px; height: 30px;'}),
            'diameter': forms.NumberInput(attrs={'class': 'form-input', 'style': 'width: 70px; border: 0px; height: 30px;'}),
            'diameter_neck': forms.NumberInput(attrs={'class': 'form-input', 'style': 'width: 70px; border: 0px; height: 30px;'}),
            'length_neck': forms.NumberInput(attrs={'class': 'form-input', 'style': 'width: 70px; border: 0px; height: 30px;'}),
            'reel_type': forms.Select(attrs={'class': 'form-input', 'style': 'width: 150px; border: 0px; height: 30px;'}),
            'mass': forms.NumberInput(attrs={'class': 'form-input', 'style': 'width: 70px; border: 0px; height: 30px;'}),
            'max_load': forms.NumberInput(attrs={'class': 'form-input', 'style': 'width: 70px; border: 0px; height: 30px;'}),
        }

        def clean_title(self):
            name = self.clean_title['name']
            return name


class TransportListForm(forms.ModelForm):
    class Meta:
        model = TransportList
        fields = ['name', 'length', 'width', 'height', 'max_load']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'style': 'width: 300px; border: 0px; height: 30px;'}),
            'length': forms.NumberInput(attrs={'class': 'form-input', 'style': 'width: 100px; border: 0px; height: 30px;'}),
            'width': forms.NumberInput(attrs={'class': 'form-input', 'style': 'width: 100px; border: 0px; height: 30px;'}),
            'height': forms.NumberInput(attrs={'class': 'form-input', 'style': 'width: 100px; border: 0px; height: 30px;'}),
            'max_load': forms.NumberInput(attrs={'class': 'form-input', 'style': 'width: 100px; border: 0px; height: 30px;'}),
        }

        def clean_title(self):
            name = self.clean_title['name']
            return name


class CableCalForm(forms.ModelForm):
    class Meta:
        model = CableCal
        fields = ['order_num', 'cod', 'name', 'mass', 'diameter', 'con_num', 'order_len', 'max_len', 'transport', ]
        widgets = {
            'order_num': forms.TextInput(attrs={'class': 'form-input', 'style': 'width: 200px; height: 25px;'}),
            'cod': forms.TextInput(attrs={'class': 'form-input', 'style': 'width: 150px; border: 0px; height: 30px;'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'style': 'width: 200px; border: 0px; height: 30px;'}),
            'mass': forms.TextInput(attrs={'class': 'form-input', 'style': 'width: 70px; border: 0px; height: 30px;'}),
            'diameter': forms.TextInput(attrs={'class': 'form-input', 'style': 'width: 70px; border: 0px; height: 30px;'}),
            'con_num': forms.NumberInput(attrs={'class': 'form-input', 'style': 'width: 70px; border: 0px; height: 30px;'}),
            'order_len': forms.NumberInput(attrs={'class': 'form-input', 'style': 'width: 70px; border: 0px; height: 30px;'}),
            'max_len': forms.NumberInput(attrs={'class': 'form-input', 'style': 'width: 70px; border: 0px; height: 30px;'}),
            'transport': forms.Select(attrs={'class': 'form-input', 'style': 'width: 120px; height: 25px;'}),
        }

        def clean_title(self):
            order_num = self.clean_title['order_num']
            return order_num
