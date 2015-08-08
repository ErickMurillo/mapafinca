# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView
from .forms import ConsultarForm
from .models import *
import json as simplejson
from django.db.models import Sum, Avg
from clima.models import *
# Create your views here.

def _queryset_filtrado(request):
    params = {}
    if request.session['sexo']:
        params['entrevistado__sexo'] = request.session['sexo']

    if request.session['organizacion']:
        params['org_responsable'] = request.session['organizacion']

    return Encuesta.objects.filter(**params)

def IndexView(request,template="index.html"):
    if request.method == 'POST':
        mensaje = None
        form = ConsultarForm(request.POST)
        if form.is_valid():
            request.session['sexo'] = form.cleaned_data['sexo']
            request.session['organizacion'] = form.cleaned_data['organizacion']
            mensaje = "Todas las variables estan correctamente :)"
            request.session['activo'] = True
            centinela = 1

            return redirect('/mapa/')

        else:
            centinela = 0

    else:
        form = ConsultarForm()
        mensaje = "Existen alguno errores"
        centinela = 0
        try:
            del request.session['sexo']
            del request.session['organizacion']
        except:
            pass

    return render(request, template, locals())

def obtener_mapa_dashboard(request):
    if request.is_ajax():
        lista = []
        for objeto in Encuesta.objects.all().distinct('entrevistado_id'):
            dicc = dict(nombre=objeto.entrevistado.nombre, id=objeto.id,
                        lon=float(objeto.entrevistado.municipio.longitud),
                        lat=float(objeto.entrevistado.municipio.latitud)
                        )
            lista.append(dicc)

        serializado = simplejson.dumps(lista)
        return HttpResponse(serializado, content_type='application/json')

class GalleryView(TemplateView):
    template_name = "galeria.html"

class DetailIndicadorView(TemplateView):
    template_name = "detalle_indicador.html"

class FirstMapaView(TemplateView):
    template_name = "primer_mapa.html"

    def get_context_data(self, **kwargs):
        context = super(FirstMapaView, self).get_context_data(**kwargs)
        context['nicaragua'] = Encuesta.objects.filter(entrevistado__pais_id=1).count()
        context['elsalvado'] = 2#Encuesta.objects.filter(entrevistado__pais_id=2).count()
        context['honduras'] = 3#Encuesta.objects.filter(entrevistado__pais_id=3).count()
        context['guatemala'] = 4#Encuesta.objects.filter(entrevistado__pais_id=4).count()
        return context


class MapaView(TemplateView):
    template_name = "mapa.html"

    def get_context_data(self, **kwargs):
        context = super(MapaView, self).get_context_data(**kwargs)
        context['nicaragua'] = Encuesta.objects.filter(entrevistado__pais_id=1).count()
        context['elsalvado'] = 0#Encuesta.objects.filter(entrevistado__pais_id=2).count()
        context['honduras'] = 0#Encuesta.objects.filter(entrevistado__pais_id=3).count()
        context['guatemala'] = 0#Encuesta.objects.filter(entrevistado__pais_id=4).count()
        return context

def principal_dashboard(request, template='dashboard.html', departamento_id=None):
    #a = _queryset_filtrado(request)
    ahora = Encuesta.objects.filter(entrevistado__departamento=departamento_id).distinct('entrevistado__id')
    depart = Departamento.objects.get(id=departamento_id)
    request.session['departamento'] = depart
    geolat = []
    geolong = []
    for obj in depart.municipio_set.all():
        geolat.append(obj.latitud)
        geolong.append(obj.longitud)

    latitud = geolat[-2]
    longitud = geolong[-2]

    # grafico de patron de gastos
    gasto_finca = Encuesta.objects.filter(entrevistado__departamento=departamento_id).aggregate(t=Sum('totalingreso__total_gasto'))['t']
    gasto_fuera_finca = Encuesta.objects.filter(entrevistado__departamento=departamento_id).aggregate(t=Sum('totalingreso__total_gasto_fuera_finca'))['t']

    # grafico de ingresos
    tradicional = Encuesta.objects.filter(entrevistado__departamento=departamento_id).aggregate(t=Sum('cultivostradicionales__total'))['t']

    huertos = Encuesta.objects.filter(entrevistado__departamento=departamento_id).aggregate(t=Sum('cultivoshuertosfamiliares__total'))['t']

    fuente = Encuesta.objects.filter(entrevistado__departamento=departamento_id).aggregate(t=Sum('fuentes__total'))['t']

    ganado = Encuesta.objects.filter(entrevistado__departamento=departamento_id).aggregate(t=Sum('ganaderia__total'))['t']

    procesamiento = Encuesta.objects.filter(entrevistado__departamento=departamento_id).aggregate(t=Sum('procesamiento__total'))['t']

    #grafico de kcalorias aun esta en proceso

    # grafico sobre algo mas

    #grafico sobre clima
    lista_precipitacion = []
    lista_temperatura = []
    for mes in CHOICES_MESES:
        precipitacion = Precipitacion.objects.filter(departamento=departamento_id,mes=mes[0]).aggregate(p=Avg('precipitacion'))['p']
        temperatura = Temperatura.objects.filter(departamento=departamento_id,mes=mes[0]).aggregate(p=Avg('temperatura'))['p']
        if precipitacion == None:
            precipitacion = 0
        lista_precipitacion.append(precipitacion)
        if temperatura == None:
            temperatura = 0
        lista_temperatura.append(temperatura)

    return render(request,template,locals())

def detalle_finca(request, template='detalle_finca.html', entrevistado_id=None):
    detalle = Encuesta.objects.filter(entrevistado_id=entrevistado_id).order_by('year')

    tabla_educacion = []
    grafo = []
    suma = 0
    for e in CHOICE_ESCOLARIDAD:
        objeto = detalle.filter(escolaridad__sexo = e[0]).aggregate(num_total = Sum('escolaridad__total'),
                no_leer = Sum('escolaridad__no_leer'),
                p_incompleta = Sum('escolaridad__pri_incompleta'),
                p_completa = Sum('escolaridad__pri_completa'),
                s_incompleta = Sum('escolaridad__secu_incompleta'),
                bachiller = Sum('escolaridad__bachiller'),
                universitario = Sum('escolaridad__uni_tecnico'))
        try:
            suma = int(objeto['p_completa'] or 0) + int(objeto['s_incompleta'] or 0) + int(objeto['bachiller'] or 0) + int(objeto['universitario'] or 0)
        except:
            pass
        variable = round(saca_porcentajes(suma,objeto['num_total']))
        grafo.append([e[1],variable])
        fila = [e[1], objeto['num_total'],
                saca_porcentajes(objeto['no_leer'], objeto['num_total'], False),
                saca_porcentajes(objeto['p_incompleta'], objeto['num_total'], False),
                saca_porcentajes(objeto['p_completa'], objeto['num_total'], False),
                saca_porcentajes(objeto['s_incompleta'], objeto['num_total'], False),
                saca_porcentajes(objeto['bachiller'], objeto['num_total'], False),
                saca_porcentajes(objeto['universitario'], objeto['num_total'], False)]
        tabla_educacion.append(fila)

    return render(request, template, locals())

def indicadores(request, template='indicadores.html'):
    #a = _queryset_filtrado(request)
    indicadores = Encuesta.objects.filter(entrevistado__departamento=request.session['departamento']).distinct('entrevistado__id')
    porcentaje_hombres = '80%'
    porcentaje_mujeres = '20%'


    return render(request, template, locals())

#FUNCIONES UTILITARIAS
def saca_porcentajes(dato, total, formato=True):
    if dato != None:
        try:
            porcentaje = (dato/float(total)) * 100 if total != None or total != 0 else 0
        except:
            return 0
        if formato:
            return porcentaje
        else:
            return '%.2f' % porcentaje
    else:
        return 0
