from django import forms

from .models import FichierAdherents

class TéléversementDuFichierAdherentForm(forms.ModelForm):

	class Meta:
		model = FichierAdherents
		fields = ('fichier_csv', 'date')
		widgets = {
			'fichier_csv': forms.FileInput(attrs={'class': 'form-control'}),
			'date': forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD', 'class': 'form-control'}),
		}
