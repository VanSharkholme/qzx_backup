from django import forms


class UserImportForm(forms.Form):
    xlsx = forms.FileField()
