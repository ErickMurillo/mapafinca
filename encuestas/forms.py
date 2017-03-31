# -*- coding: utf-8 -*-
from django import forms
from .models import *
from lookups import *
import selectable.forms as selectable

class ProductorAdminForm(forms.ModelForm):

    class Meta(object):
        model = Encuesta
        fields = '__all__'
        widgets = {
            'entrevistado': selectable.AutoCompleteSelectWidget(lookup_class=ProductorLookup),
        }

class TipoEnergiaForm(forms.ModelForm):
    class Meta:
        model = TipoEnergia
        fields = '__all__'
        widgets = {
            'tipo': forms.CheckboxSelectMultiple(attrs={'size':'10'})
        }

class EnergiaSolarCocinarForm(forms.ModelForm):
    class Meta:
        model = EnergiaSolarCocinar
        fields = '__all__'
        widgets = {
            'fuente': forms.CheckboxSelectMultiple(attrs={'size':'10'})
        }

class TipoCocinasForm(forms.ModelForm):
    class Meta:
        model = TipoCocinas
        fields = '__all__'
        widgets = {
            'cocina': forms.CheckboxSelectMultiple(attrs={'size':'10'})
        }

class AccesoAguaForm(forms.ModelForm):
    class Meta:
        model = AccesoAgua
        fields = '__all__'
        widgets = {
            'agua': forms.CheckboxSelectMultiple(attrs={'size':'10'})
        }

CHOICE_SEXO = (
                (1, 'Mujer'),
                (2, 'Hombre'),
              )

def fecha_choice():
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    return list(sorted(set(years)))

class ConsultarForm(forms.Form):
    #fecha = forms.MultipleChoiceField(choices=fecha_choice(), label="Años", required=True)
    estacion = forms.ChoiceField(choices=CHOICES_ESTACIONES, required=True)
    pais = forms.ModelChoiceField(queryset=Pais.objects.all(), required=True)
    organizacion = forms.ModelMultipleChoiceField(queryset=OrganizacionResp.objects.all(), required=False)
    departamento = forms.ModelMultipleChoiceField(queryset=Departamento.objects.filter(entrevistados__gt=1).distinct(), required=False)
    municipio = forms.ModelMultipleChoiceField(queryset=Municipio.objects.all(), required=False)
    comunidad = forms.ModelMultipleChoiceField(queryset=Comunidad.objects.all(), required=False)
    #sexo = forms.ChoiceField(choices=CHOICE_SEXO, required=False)

class ConsultarGaleriaForm(forms.Form):
    fecha = forms.ChoiceField(choices=fecha_choice(), label="Años", required=True)
    pais = forms.ModelChoiceField(queryset=Pais.objects.all(), required=True)
    organizacion = forms.ModelMultipleChoiceField(queryset=OrganizacionResp.objects.all(), required=False)