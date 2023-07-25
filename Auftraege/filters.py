import django_filters
from .models import *
from .forms import *
from django import forms
from django_filters import CharFilter,ModelChoiceFilter,DateFilter

class SearchPosition(django_filters.FilterSet):

    auftragsnummer = ModelChoiceFilter(queryset=Auftrag.objects.all(),field_name="auftragsnummer", widget=forms.Select(attrs={'class':'form-select form-select-sm mx-auto'}))
    von = ModelChoiceFilter(queryset=Adressen.objects.all(),field_name="von", widget=forms.Select(attrs={'class':'form-select form-select-sm mx-auto'}))
    nach = ModelChoiceFilter(queryset=Adressen.objects.all(),field_name="nach", widget=forms.Select(attrs={'class':'form-select form-select-sm mx-auto'}))
    kostenstelle = CharFilter(field_name="kostenstelle", widget=forms.TextInput(attrs={'class':'form-control form-control-sm'}))
    referenz = CharFilter(field_name="referenz", lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control form-control-sm'}))
    empfänger = CharFilter(field_name="empfänger", widget=forms.TextInput(attrs={'class':'form-control form-control-sm'}))
    unterschrift_datum = DateFilter(field_name='unterschrift_datum',widget=forms.TextInput(attrs={'class':'form-control form-control-sm','type':'date'}))
    "start_date = DateFilter(field_name='unterschrift_datum',lookup_expr=('lt'),widget=forms.TextInput(attrs={'class':'form-control form-control-sm','type':'date'}))"
    "end_date = DateFilter(field_name='unterschrift_datum',lookup_expr=('gt'),widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'type':'date'}))"
    class Meta: 
        model = Auftragspositionen
        fields=['auftragsnummer','von', 'nach','kostenstelle','referenz','empfänger','unterschrift_datum']


