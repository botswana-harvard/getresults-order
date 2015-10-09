from django import forms

from getresults_aliquot.models import Aliquot

from .models import Order


class OrderForm(forms.ModelForm):

    def clean_aliquot_identifier(self):
        aliquot_identifier = self.cleaned_data.get('aliquot_identifier')
        try:
            Aliquot.objects.get(aliquot_identifier=aliquot_identifier)
        except Aliquot.DoesNotExist:
            raise forms.ValidationError('Invalid Aliquot Identifier. Got {}'.format(aliquot_identifier))

    class Meta:
        model = Order
