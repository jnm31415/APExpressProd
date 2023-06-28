from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *

class CreateUserForm(UserCreationForm):
  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class UA10NAForm(ModelForm):
  class Meta: 
    model = Auftrag
    fields = ['auftragsnummer_ID','auftraggeber','auftragsdatum','ausgeführt_bis','auftragsfirma','auftragstext','fahrer','angenommen']
    widgets = {
      'auftragsnummer_ID': forms.TextInput(attrs={'class':'form-control mx-auto','readonly':'readonly'}),
      'auftraggeber': forms.TextInput(attrs={'class':'form-control mx-auto'}),
      'auftragsdatum': forms.TextInput(attrs={'class':'form-control mx-auto', 'type':'date'}),
      'ausgeführt_bis': forms.TextInput(attrs={'class':'form-control mx-auto', 'type':'date'}),
      'auftragsfirma': forms.Select(attrs={'class':'form-select mx-auto'}),
      'fahrer': forms.Select(attrs={'class':'form-select mx-auto'}),
      'auftragstext':forms.Textarea(attrs={'class':'form-control','rows':'1'}),
      'angenommen': forms.CheckboxInput(attrs={'class':'check-box-input'})
    }

class Position(ModelForm):
  class Meta:
    model = Auftragspositionen
    fields = '__all__'
    widgets={
      'auftragsnummer': forms.TextInput(attrs={'class':'form-control mx-auto','readonly':'readonly'}),
      'von': forms.Select(attrs={'class':'form-select mx-auto'}),
      'nach': forms.Select(attrs={'class':'form-select mx-auto'}),
      'kostenstelle':forms.TextInput(attrs={'class':'form-control mx-auto'}),
      'referenz': forms.Textarea(attrs={'class':'form-control mx-auto','rows':'1'}),
      'position_abgeschlossen': forms.CheckboxInput(attrs={'class':'check-box-input'}),
      'empfänger': forms.TextInput(attrs={'class':'form-control'}),
      'einzelpreis': forms.NumberInput(attrs={'class':'form-control'}),
      'mwst': forms.NumberInput(attrs={'class':'form-control'}),
      'anzahl': forms.NumberInput(attrs={'class':'form-control'}),
      'unterschrift_datum':forms.TextInput(attrs={'class':'form-control mx-auto','readonly':'readonly'}),
      'unterschrift':forms.Textarea(attrs={'class':'form-control mx-auto','rows':'1','readonly':'readonly'})

    }  


    
class UA20NRForm(ModelForm):

  def __init__(self, *args, **kwargs):
      super(UA20NRForm, self).__init__(*args, **kwargs)
      self.fields["auftragsnummer"].queryset = Auftrag.objects.filter(auftrag_abgeschlossen=False)

  class Meta: 
    model = Rechnung
    fields = ['auftragsnummer','rechnungsnummer','rechnungsdatum','empfänger','rechnungstext']
    widgets={
      'auftragsnummer': forms.Select(attrs={'class':'form-select mx-auto'}),
      'rechnungsnummer': forms.TextInput(attrs={'class':'form-control mx-auto'}),
      'rechnungsdatum': forms.TextInput(attrs={'class':'form-control mx-auto', 'type':'date'}),
      'empfänger': forms.Select(attrs={'class':'form-select mx-auto'}),
      'rechnungstext':forms.Textarea(attrs={'class':'form-control','rows':'4'}),
    }


