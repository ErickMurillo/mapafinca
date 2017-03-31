# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from .forms import ConsultarForm, ConsultarGaleriaForm
from .models import *
import json as simplejson
from django.db.models import Count, Sum, Avg, Value as V
from clima.models import *
from collections import OrderedDict
from django.db.models import Q
from django.db.models.functions import Coalesce
# Create your views here.


def _queryset_filtrado(request):
    params = {}

    #if request.session['fecha']:
    #    params['year__in'] = request.session['fecha']
    if 'estacion' in request.session:
        params['estacion'] = request.session['estacion']

    if 'pais' in request.session:
        params['entrevistado__pais'] = request.session['pais']

    if 'departamento' in request.session:
        params['entrevistado__departamento__in'] = request.session['departamento']

    if 'organizacion' in request.session:
        params['org_responsable__in'] = request.session['organizacion']

    if 'municipio' in request.session:
        params['entrevistado__municipio__in'] = request.session['municipio']

    if 'comunidad' in request.session:
        params['entrevistado__comunidad__in'] = request.session['comunidad']

    #if request.session['sexo']:
    #    params['entrevistado__sexo'] = request.session['sexo']

    unvalid_keys = []
    for key in params:
    	if not params[key]:
    		unvalid_keys.append(key)

    for key in unvalid_keys:
    	del params[key]

    return Encuesta.objects.filter(**params)


def _queryset_galeria(request):
    params = {}

    if request.session['fecha']:
       params['year'] = request.session['fecha']

    if 'pais' in request.session:
        params['entrevistado__pais'] = request.session['pais']

    if 'organizacion' in request.session:
        params['org_responsable__in'] = request.session['organizacion']

    unvalid_keys = []
    for key in params:
        if not params[key]:
            unvalid_keys.append(key)

    for key in unvalid_keys:
        del params[key]

    return Encuesta.objects.filter(**params)


def IndexView(request,template="index.html"):
    paises = {}
    for pais in Pais.objects.all():
        paises[pais] = {}
        for mun in Departamento.objects.all():
            m = Encuesta.objects.filter(entrevistado__departamento=mun, entrevistado__pais=pais).count()
            if m > 0:
                paises[pais][mun.nombre] = (m,mun.id)

    return render(request, template, locals())


def obtener_mapa_dashboard(request):
    if request.is_ajax():
        lista = []
        for objeto in Encuesta.objects.filter(entrevistado__departamento=request.session['departamento']).distinct('entrevistado_id'):
            if objeto.entrevistado.longitud != None and objeto.entrevistado.longitud != '':
                dicc = dict(nombre=objeto.entrevistado.nombre,
                            id=objeto.entrevistado.id,
                            lon=float(objeto.entrevistado.longitud),
                            lat=float(objeto.entrevistado.latitud),
                            finca=objeto.entrevistado.finca,
                            comunidad=objeto.entrevistado.comunidad.nombre,
                            sexo=objeto.entrevistado.get_sexo_display(),
                            )
                lista.append(dicc)

        serializado = simplejson.dumps(lista)
        return HttpResponse(serializado, content_type='application/json')

def obtener_mapa_dashboard_pais(request):
    if request.is_ajax():
        lista = []
        for objeto in Encuesta.objects.filter(entrevistado__pais=request.session['pais']).distinct('entrevistado_id'):
            if objeto.entrevistado.longitud != None and objeto.entrevistado.longitud != '':
                dicc = dict(nombre=objeto.entrevistado.nombre,
                            id=objeto.entrevistado.id,
                            lon=float(objeto.entrevistado.longitud),
                            lat=float(objeto.entrevistado.latitud),
                            finca=objeto.entrevistado.finca,
                            comunidad=objeto.entrevistado.comunidad.nombre,
                            sexo=objeto.entrevistado.get_sexo_display(),
                            )
                lista.append(dicc)

        serializado = simplejson.dumps(lista)
        return HttpResponse(serializado, content_type='application/json')


def galeria_mapas_fincas(request, template='galeria.html'):
    centinela = 0
    if request.method == 'POST':
        mensaje = None
        form = ConsultarGaleriaForm(request.POST)
        if form.is_valid():
            request.session['fecha'] = form.cleaned_data['fecha']
            request.session['pais'] = form.cleaned_data['pais']
            request.session['organizacion'] = form.cleaned_data['organizacion']

            mensaje = "Todas las variables estan correctamente :)"
            centinela = 1

    else:
        form = ConsultarGaleriaForm()

    if centinela == 0:
        object_list = Encuesta.objects.all()
        print len(object_list)
    else:
        object_list = _queryset_galeria(request)
        print len(object_list)

    return render(request, template, locals())

class DetailIndicadorView(TemplateView):
    template_name = "detalle_indicador.html"


class FirstMapaView(TemplateView):
    template_name = "primer_mapa.html"

    def get_context_data(self, **kwargs):
        context = super(FirstMapaView, self).get_context_data(**kwargs)
        context['nicaragua'] = Encuesta.objects.filter(entrevistado__pais_id=1).count()
        context['elsalvado'] = 0  #Encuesta.objects.filter(entrevistado__pais_id=2).count()
        context['honduras'] = 0  #Encuesta.objects.filter(entrevistado__pais_id=3).count()
        context['guatemala'] = 0  #Encuesta.objects.filter(entrevistado__pais_id=4).count()
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

    filtro = Encuesta.objects.filter(entrevistado__municipio__departamento__id=departamento_id) #.distinct('entrevistado__id')
    ahora = filtro.distinct('entrevistado__id')
    dividir_todo = ahora.count()
    depart = Departamento.objects.filter(id=departamento_id)
    pais = Pais.objects.get(departamento=departamento_id)
    request.session['pais'] = pais
    request.session['departamento'] = depart

    request.session['encuestados'] = dividir_todo
    request.session['hombres'] = ahora.filter(entrevistado__sexo=2,entrevistado__jefe=1).count() / filtro.count() * 100
    request.session['mujeres'] = ahora.filter(entrevistado__sexo=1,entrevistado__jefe=1).count() / filtro.count() * 100


    latitud = pais.latitud
    longitud = pais.longitud

    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    muchos_tiempo = list(sorted(set(years)))

    tiempo_patron_gasto = OrderedDict()
    tiempo_ingresos = OrderedDict()
    tiempo_kcalorias = OrderedDict()
    tiempo_gastos_alimentarios = OrderedDict()
    tiempo_clima = OrderedDict()
    tiempo_arana = OrderedDict()
    tiempo_rendimiento = OrderedDict()
    for anio in muchos_tiempo:
        # grafico de patron de gastos
        gasto_finca_verano=0
        gasto_finca_invierno=0
        gasto_fuera_finca_verano=0
        gasto_fuera_finca_invierno=0
        try:
            gasto_finca_verano = float(filtro.filter(year=anio[0],estacion=1,gastohogar__tipo=5).aggregate(t=Sum('gastohogar__total'))['t'] / 12) / float(dividir_todo)
            gasto_finca_invierno = float(filtro.filter(year=anio[0],estacion=2,gastohogar__tipo=5).aggregate(t=Sum('gastohogar__total'))['t'] / 12) / float(dividir_todo)
        except:
            pass
        try:
            gasto_fuera_finca_verano = float(filtro.filter(year=anio[0],estacion=1).aggregate(t=Sum('gastoproduccion__total'))['t'] / 12) / float(dividir_todo)
            gasto_fuera_finca_invierno = float(filtro.filter(year=anio[0],estacion=2).aggregate(t=Sum('gastoproduccion__total'))['t'] / 12) / float(dividir_todo)
        except:
            pass
        tiempo_patron_gasto[anio[0]] = [gasto_finca_verano,gasto_finca_invierno,gasto_fuera_finca_verano,gasto_fuera_finca_invierno]

        # grafico de ingresos
        tradicional_verano = 0
        tradicional_invierno = 0
        huertos_verano = 0
        huertos_invierno = 0
        frutas_verano = 0
        frutas_invierno = 0
        fuente_verano = 0
        fuente_invierno = 0
        ganado_verano = 0
        ganado_invierno = 0
        procesamiento_verano = 0
        procesamiento_invierno = 0

        try:
            tradicional_verano = float(filtro.filter(year=anio[0],estacion=1).aggregate(t=Sum('cultivostradicionales__total'))['t'] / 12) / float(dividir_todo)
            tradicional_invierno = float(filtro.filter(year=anio[0],estacion=2).aggregate(t=Sum('cultivostradicionales__total'))['t'] / 12) / float(dividir_todo)
        except:
            pass

        try:
            huertos_verano = float(filtro.filter(year=anio[0],estacion=1).aggregate(t=Sum('cultivoshuertosfamiliares__total'))['t'] / 12) / float(dividir_todo)
            huertos_invierno = float(filtro.filter(year=anio[0],estacion=2).aggregate(t=Sum('cultivoshuertosfamiliares__total'))['t'] / 12) / float(dividir_todo)
        except:
            pass

        try:
            frutas_verano = float(filtro.filter(year=anio[0],estacion=1).aggregate(t=Sum('cultivosfrutasfinca__total'))['t'] / 12 ) / float(dividir_todo)
            frutas_invierno = float(filtro.filter(year=anio[0],estacion=2).aggregate(t=Sum('cultivosfrutasfinca__total'))['t'] / 12 ) / float(dividir_todo)
        except:
            pass

        try:
            fuente_verano = float(filtro.filter(year=anio[0],estacion=1).aggregate(t=Sum('fuentes__total'))['t'] / 12) / float(dividir_todo)
            fuente_invierno = float(filtro.filter(year=anio[0],estacion=2).aggregate(t=Sum('fuentes__total'))['t'] / 12) / float(dividir_todo)
        except:
            pass

        try:
            ganado_verano = float(filtro.filter(year=anio[0],estacion=1).aggregate(t=Sum('ganaderia__total'))['t'] / 12) / float(dividir_todo)
            ganado_invierno = float(filtro.filter(year=anio[0],estacion=2).aggregate(t=Sum('ganaderia__total'))['t'] / 12) / float(dividir_todo)
        except:
            pass

        try:
            procesamiento_verano = float(filtro.filter(year=anio[0],estacion=1).aggregate(t=Sum('procesamiento__total'))['t'] / 12) / float(dividir_todo)
            procesamiento_invierno = float(filtro.filter(year=anio[0],estacion=2).aggregate(t=Sum('procesamiento__total'))['t'] / 12) / float(dividir_todo)
        except:
            pass
        tiempo_ingresos[anio[1]] = [tradicional_verano,tradicional_invierno,huertos_verano,huertos_invierno,
                                    frutas_verano,frutas_invierno,fuente_verano,fuente_invierno,ganado_verano,
                                    ganado_invierno,procesamiento_verano,procesamiento_invierno]

        #Calculos de los kcalorias
        tiempo_kcalorias[anio[1]] = [envio_calorias(request, anio[0], 1), envio_calorias(request, anio[0], 2)]


        #grafico sobre gastos alimentarios
        tiempo_gastos_alimentarios[anio[1]] = {}
        for obj in ProductosFueraFinca.objects.all():
            try:
                cada_uno_verano = float(filtro.filter(year=anio[0],estacion=1,alimentosfuerafinca__producto=obj).aggregate(t=Avg('alimentosfuerafinca__total'))['t'] / 12) / float(dividir_todo)
            except:
                cada_uno_verano = 0
            if cada_uno_verano == None:
                cada_uno_verano = 0
            try:
                cada_uno_invierno = float(filtro.filter(year=anio[0],estacion=2,alimentosfuerafinca__producto=obj).aggregate(t=Avg('alimentosfuerafinca__total'))['t'] / 12) / float(dividir_todo)
            except:
                cada_uno_invierno = 0
            if cada_uno_invierno == None:
                cada_uno_invierno = 0
            tiempo_gastos_alimentarios[anio[1]][obj]  = (cada_uno_verano, cada_uno_invierno)

        #grafico sobre clima
        lista_precipitacion = []
        lista_temperatura = []
        for mes in CHOICES_MESES:
            precipitacion = Precipitacion.objects.filter(year=anio[0],departamento=departamento_id,mes=mes[0]).aggregate(p=Avg('precipitacion'))['p']
            temperatura = Temperatura.objects.filter(year=anio[0],departamento=departamento_id,mes=mes[0]).aggregate(p=Avg('temperatura'))['p']
            if precipitacion == None:
                precipitacion = 0
            lista_precipitacion.append(precipitacion)
            if temperatura == None:
                temperatura = 0
            lista_temperatura.append(temperatura)
        tiempo_clima[anio[1]] = (lista_precipitacion,lista_temperatura)

        # grafico  de tela de araña : capital natural
        capital_natural_mujer = filtro.filter(year=anio[0],sexomiembros__sexo=1, dueno=1).count()
        capital_natural_hombre = filtro.filter(year=anio[0],sexomiembros__sexo=2, dueno=1).count()
        capital_natural_ambos = filtro.filter(year=anio[0],sexomiembros__sexo=3, dueno=1).count()
        #capital social
        capital_social_mujer = filtro.filter(year=anio[0],sexomiembros__sexo=1, organizacioncomunitaria__pertenece=1).count()
        capital_social_hombre = filtro.filter(year=anio[0],sexomiembros__sexo=2, organizacioncomunitaria__pertenece=1).count()
        capital_social_ambos = filtro.filter(year=anio[0],sexomiembros__sexo=3, organizacioncomunitaria__pertenece=1).count()
        #capital financiero
        capital_financiero_mujer = filtro.filter(year=anio[0],sexomiembros__sexo=1, totalingreso__total__gt=1).count()
        capital_financiero_hombre = filtro.filter(year=anio[0],sexomiembros__sexo=2, totalingreso__total__gt=1).count()
        capital_financiero_ambos = filtro.filter(year=anio[0],sexomiembros__sexo=3, totalingreso__total__gt=1).count()
        #capital fisico
        capital_fisico_mujer = filtro.filter(Q(year=anio[0],sexomiembros__sexo=1), Q(year=anio[0],totalingreso__total__gt=1) |  Q(year=anio[0],tipoenergia__tipo=4)).count()
        capital_fisico_hombre = filtro.filter(Q(year=anio[0],sexomiembros__sexo=2), Q(year=anio[0],totalingreso__total__gt=1) |  Q(year=anio[0],tipoenergia__tipo=4)).count()
        capital_fisico_ambos = filtro.filter(Q(year=anio[0],sexomiembros__sexo=3), Q(year=anio[0],totalingreso__total__gt=1) |  Q(year=anio[0],tipoenergia__tipo=4)).count()
        #capital humano
        capital_humano_mujer = filtro.filter(Q(year=anio[0],sexomiembros__sexo=1),
                                            Q(year=anio[0],escolaridad__pri_completa__gt=1) |  Q(year=anio[0],escolaridad__secu_incompleta__gt=1) | Q(year=anio[0],escolaridad__bachiller__gt=1) |  Q(year=anio[0],escolaridad__uni_tecnico__gt=1)).count()
        capital_humano_hombre = filtro.filter(Q(year=anio[0],sexomiembros__sexo=2),
                                            Q(year=anio[0],escolaridad__pri_completa__gt=1) |  Q(year=anio[0],escolaridad__secu_incompleta__gt=1) | Q(year=anio[0],escolaridad__bachiller__gt=1) |  Q(year=anio[0],escolaridad__uni_tecnico__gt=1)).count()
        capital_humano_ambos = filtro.filter(Q(year=anio[0],sexomiembros__sexo=3),
                                        Q(year=anio[0],escolaridad__pri_completa__gt=1) |  Q(year=anio[0],escolaridad__secu_incompleta__gt=1) | Q(year=anio[0],escolaridad__bachiller__gt=1) |  Q(year=anio[0],escolaridad__uni_tecnico__gt=1)).count()
        tiempo_arana[anio[1]] = (   capital_natural_hombre, capital_natural_mujer, capital_natural_ambos,
                                    capital_social_hombre, capital_social_mujer, capital_social_ambos,
                                    capital_financiero_hombre, capital_financiero_mujer, capital_financiero_ambos,
                                    capital_fisico_hombre, capital_fisico_mujer, capital_fisico_ambos,
                                    capital_humano_hombre, capital_humano_mujer, capital_humano_ambos)

        #Calculo de los rendimientos o productividad del maiz y frijol primera
        total_area_cosechada_maiz_verano = filtro.filter(cultivostradicionales__cultivo=3,
                                    year=anio[0],estacion=1).aggregate(t=Sum('cultivostradicionales__area_cosechada'))['t']
        total_cosecha_maiz_verano = filtro.filter(cultivostradicionales__cultivo=3,
                                    year=anio[0],estacion=1).aggregate(t=Sum('cultivostradicionales__cantidad_cosechada'))['t']
        try:
            rendimiento_maiz_verano = total_cosecha_maiz_verano / total_area_cosechada_maiz_verano
        except:
            rendimiento_maiz_verano = 0

        total_area_cosechada_frijol_verano = filtro.filter(cultivostradicionales__cultivo=2,
                                            year=anio[0],estacion=1).aggregate(t=Sum('cultivostradicionales__area_cosechada'))['t']
        total_cosecha_frijol_verano = filtro.filter(cultivostradicionales__cultivo=2,
                                            year=anio[0],estacion=1).aggregate(t=Sum('cultivostradicionales__cantidad_cosechada'))['t']
        try:
            rendimiento_frijol_verano = total_cosecha_frijol_verano / total_area_cosechada_frijol_verano
        except:
            rendimiento_frijol_verano = 0

        #calculo de los rendimiento invierno
        total_area_cosechada_maiz_invierno = filtro.filter(cultivostradicionales__cultivo=3,
                                    year=anio[0],estacion=2).aggregate(t=Sum('cultivostradicionales__area_cosechada'))['t'] or 0
        total_cosecha_maiz_invierno = filtro.filter(cultivostradicionales__cultivo=3,
                                    year=anio[0],estacion=2).aggregate(t=Sum('cultivostradicionales__cantidad_cosechada'))['t'] or 0
        try:
            rendimiento_maiz_invierno = total_cosecha_maiz_invierno / total_area_cosechada_maiz_invierno
        except:
            rendimiento_maiz_invierno = 0

        total_area_cosechada_frijol_invierno = filtro.filter(cultivostradicionales__cultivo=2,
                                            year=anio[0],estacion=2).aggregate(t=Sum('cultivostradicionales__area_cosechada'))['t'] or 0
        total_cosecha_frijol_invierno = filtro.filter(cultivostradicionales__cultivo=2,
                                            year=anio[0],estacion=2).aggregate(t=Sum('cultivostradicionales__cantidad_cosechada'))['t'] or 0
        try:
            rendimiento_frijol_invierno = total_cosecha_frijol_invierno / total_area_cosechada_frijol_invierno
        except:
            rendimiento_frijol_invierno = 0
        tiempo_rendimiento[anio[1]] = (rendimiento_maiz_verano,
                                       rendimiento_maiz_invierno,
                                       rendimiento_frijol_verano,
                                       rendimiento_frijol_invierno)

    return render(request,template,locals())

def principal_dashboard_pais(request, template='dashboard_pais.html', pais=None,):

    paisid = Pais.objects.get(slug = pais)
    filtro = Encuesta.objects.filter(entrevistado__pais_id=paisid)
    ahora = filtro.distinct('entrevistado__id')
    dividir_todo = ahora.count()

    request.session['departamento'] = None
    request.session['pais'] = paisid
    request.session['encuestados'] = filtro.count()
    request.session['hombres'] = ahora.filter(entrevistado__sexo=2,entrevistado__jefe=1).count() / filtro.count() * 100
    request.session['mujeres'] = ahora.filter(entrevistado__sexo=1,entrevistado__jefe=1).count() / filtro.count() * 100



    latitud = paisid.latitud
    longitud = paisid.longitud

    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    muchos_tiempo = list(sorted(set(years)))

    tiempo_patron_gasto = OrderedDict()
    tiempo_ingresos = OrderedDict()
    tiempo_kcalorias = OrderedDict()
    tiempo_gastos_alimentarios = OrderedDict()
    tiempo_clima = OrderedDict()
    tiempo_arana = OrderedDict()
    tiempo_rendimiento = OrderedDict()
    for anio in muchos_tiempo:
        # grafico de patron de gastos
        gasto_finca_verano=0
        gasto_finca_invierno=0
        gasto_fuera_finca_verano=0
        gasto_fuera_finca_invierno=0
        try:
            gasto_finca_verano = float(filtro.filter(year=anio[0],estacion=1,gastohogar__tipo=5).aggregate(t=Sum('gastohogar__total'))['t'] / 12) / float(dividir_todo)
            gasto_finca_invierno = float(filtro.filter(year=anio[0],estacion=2,gastohogar__tipo=5).aggregate(t=Sum('gastohogar__total'))['t'] / 12) / float(dividir_todo)
        except:
            pass

        try:
            gasto_fuera_finca_verano = float(filtro.filter(year=anio[0],estacion=1).aggregate(t=Sum('gastoproduccion__total'))['t'] / 12) / float(dividir_todo)
            gasto_fuera_finca_invierno = float(filtro.filter(year=anio[0],estacion=2).aggregate(t=Sum('gastoproduccion__total'))['t'] / 12) / float(dividir_todo)
        except:
            pass

        tiempo_patron_gasto[anio[0]] = [gasto_finca_verano,gasto_finca_invierno,gasto_fuera_finca_verano,gasto_fuera_finca_invierno]

        # grafico de ingresos
        tradicional_verano = 0
        tradicional_invierno = 0
        huertos_verano = 0
        huertos_invierno = 0
        frutas_verano = 0
        frutas_invierno = 0
        fuente_verano = 0
        fuente_invierno = 0
        ganado_verano = 0
        ganado_invierno = 0
        procesamiento_verano = 0
        procesamiento_invierno = 0
        try:
            tradicional_verano = float(filtro.filter(year=anio[0],estacion=1).aggregate(t=Sum('cultivostradicionales__total'))['t'] / 12) / float(dividir_todo)
            tradicional_invierno = float(filtro.filter(year=anio[0],estacion=2).aggregate(t=Sum('cultivostradicionales__total'))['t'] / 12) / float(dividir_todo)
        except:
            pass

        try:
            huertos_verano = float(filtro.filter(year=anio[0],estacion=1).aggregate(t=Sum('cultivoshuertosfamiliares__total'))['t'] / 12) / float(dividir_todo)
            huertos_invierno = float(filtro.filter(year=anio[0],estacion=2).aggregate(t=Sum('cultivoshuertosfamiliares__total'))['t'] / 12) / float(dividir_todo)
        except:
            pass

        try:
            frutas_verano = float(filtro.filter(year=anio[0],estacion=1).aggregate(t=Sum('cultivosfrutasfinca__total'))['t'] / 12 ) / float(dividir_todo)
            frutas_invierno = float(filtro.filter(year=anio[0],estacion=2).aggregate(t=Sum('cultivosfrutasfinca__total'))['t'] / 12 ) / float(dividir_todo)
        except:
            pass

        try:
            fuente_verano = float(filtro.filter(year=anio[0],estacion=1).aggregate(t=Sum('fuentes__total'))['t'] / 12) / float(dividir_todo)
            fuente_invierno = float(filtro.filter(year=anio[0],estacion=2).aggregate(t=Sum('fuentes__total'))['t'] / 12) / float(dividir_todo)
        except:
            pass

        try:
            ganado_verano = float(filtro.objects.filter(year=anio[0],estacion=1).aggregate(t=Sum('ganaderia__total'))['t'] / 12) / float(dividir_todo)
            ganado_invierno = float(filtro.objects.filter(year=anio[0],estacion=2).aggregate(t=Sum('ganaderia__total'))['t'] / 12) / float(dividir_todo)
        except:
            pass

        try:
            procesamiento_verano = float(filtro.objects.filter(year=anio[0],estacion=1).aggregate(t=Sum('procesamiento__total'))['t'] / 12) / float(dividir_todo)
            procesamiento_verano = float(filtro.objects.filter(year=anio[0],estacion=2).aggregate(t=Sum('procesamiento__total'))['t'] / 12) / float(dividir_todo)
        except:
            pass

        tiempo_ingresos[anio[1]] = [tradicional_verano,tradicional_invierno,huertos_verano,huertos_invierno,
                                    frutas_verano,frutas_invierno,fuente_verano,fuente_invierno,ganado_verano,
                                    ganado_invierno,procesamiento_verano,procesamiento_invierno]

        #grafico sobre gastos alimentarios
        tiempo_gastos_alimentarios[anio[1]] = {}
        for obj in ProductosFueraFinca.objects.all():
            try:
                cada_uno_verano = float(filtro.filter(year=anio[0],estacion=1,alimentosfuerafinca__producto=obj).aggregate(t=Avg('alimentosfuerafinca__total'))['t'] / 12) / float(dividir_todo)
            except:
                cada_uno_verano = 0
            if cada_uno_verano == None:
                cada_uno_verano = 0
            try:
                cada_uno_invierno = float(filtro.filter(year=anio[0],estacion=2,alimentosfuerafinca__producto=obj).aggregate(t=Avg('alimentosfuerafinca__total'))['t'] / 12) / float(dividir_todo)
            except:
                cada_uno_invierno = 0
            if cada_uno_invierno == None:
                cada_uno_invierno = 0
            tiempo_gastos_alimentarios[anio[1]][obj]  = (cada_uno_verano, cada_uno_invierno)

        #grafico sobre clima
        lista_precipitacion = []
        lista_temperatura = []
        for mes in CHOICES_MESES:
            precipitacion = Precipitacion.objects.filter(pais__slug=pais,year=anio[0],mes=mes[0]).aggregate(p=Avg('precipitacion'))['p']
            temperatura = Temperatura.objects.filter(pais__slug=pais,year=anio[0],mes=mes[0]).aggregate(p=Avg('temperatura'))['p']
            if precipitacion == None:
                precipitacion = 0
            lista_precipitacion.append(precipitacion)
            if temperatura == None:
                temperatura = 0
            lista_temperatura.append(temperatura)
        tiempo_clima[anio[1]] = (lista_precipitacion,lista_temperatura)

        # grafico  de tela de araña : capital natural
        capital_natural_mujer = filtro.filter(year=anio[0],sexomiembros__sexo=1, dueno=1).count()
        capital_natural_hombre = filtro.filter(year=anio[0],sexomiembros__sexo=2, dueno=1).count()
        capital_natural_ambos = filtro.filter(year=anio[0],sexomiembros__sexo=3, dueno=1).count()
        #capital social
        capital_social_mujer = filtro.filter(year=anio[0],sexomiembros__sexo=1, organizacioncomunitaria__pertenece=1).count()
        capital_social_hombre = filtro.filter(year=anio[0],sexomiembros__sexo=2, organizacioncomunitaria__pertenece=1).count()
        capital_social_ambos = filtro.filter(year=anio[0],sexomiembros__sexo=3, organizacioncomunitaria__pertenece=1).count()
        #capital financiero
        capital_financiero_mujer = filtro.filter(year=anio[0],sexomiembros__sexo=1, totalingreso__total__gt=1).count()
        capital_financiero_hombre = filtro.filter(year=anio[0],sexomiembros__sexo=2, totalingreso__total__gt=1).count()
        capital_financiero_ambos = filtro.filter(year=anio[0],sexomiembros__sexo=3, totalingreso__total__gt=1).count()
        #capital fisico
        capital_fisico_mujer = filtro.filter(Q(year=anio[0],sexomiembros__sexo=1), Q(year=anio[0],totalingreso__total__gt=1) |  Q(year=anio[0],tipoenergia__tipo=4)).count()
        capital_fisico_hombre = filtro.filter(Q(year=anio[0],sexomiembros__sexo=2), Q(year=anio[0],totalingreso__total__gt=1) |  Q(year=anio[0],tipoenergia__tipo=4)).count()
        capital_fisico_ambos = filtro.filter(Q(year=anio[0],sexomiembros__sexo=3), Q(year=anio[0],totalingreso__total__gt=1) |  Q(year=anio[0],tipoenergia__tipo=4)).count()
        #capital humano
        capital_humano_mujer = filtro.filter(Q(year=anio[0],sexomiembros__sexo=1),
                                            Q(year=anio[0],escolaridad__pri_completa__gt=1) |  Q(year=anio[0],escolaridad__secu_incompleta__gt=1) | Q(year=anio[0],escolaridad__bachiller__gt=1) |  Q(year=anio[0],escolaridad__uni_tecnico__gt=1)).count()
        capital_humano_hombre = filtro.filter(Q(year=anio[0],sexomiembros__sexo=2),
                                            Q(year=anio[0],escolaridad__pri_completa__gt=1) |  Q(year=anio[0],escolaridad__secu_incompleta__gt=1) | Q(year=anio[0],escolaridad__bachiller__gt=1) |  Q(year=anio[0],escolaridad__uni_tecnico__gt=1)).count()
        capital_humano_ambos = filtro.filter(Q(year=anio[0],sexomiembros__sexo=3),
                                        Q(year=anio[0],escolaridad__pri_completa__gt=1) |  Q(year=anio[0],escolaridad__secu_incompleta__gt=1) | Q(year=anio[0],escolaridad__bachiller__gt=1) |  Q(year=anio[0],escolaridad__uni_tecnico__gt=1)).count()
        tiempo_arana[anio[1]] = (   capital_natural_hombre, capital_natural_mujer, capital_natural_ambos,
                                    capital_social_hombre, capital_social_mujer, capital_social_ambos,
                                    capital_financiero_hombre, capital_financiero_mujer, capital_financiero_ambos,
                                    capital_fisico_hombre, capital_fisico_mujer, capital_fisico_ambos,
                                    capital_humano_hombre, capital_humano_mujer, capital_humano_ambos)

        #Calculo de los rendimientos o productividad del maiz y frijol primera
        total_area_cosechada_maiz_verano = filtro.filter(cultivostradicionales__cultivo=3,
                                    year=anio[0],estacion=1).aggregate(t=Sum('cultivostradicionales__area_cosechada'))['t']
        total_cosecha_maiz_verano = filtro.filter(cultivostradicionales__cultivo=3,
                                    year=anio[0],estacion=1).aggregate(t=Sum('cultivostradicionales__cantidad_cosechada'))['t']
        try:
            rendimiento_maiz_verano = total_cosecha_maiz_verano / total_area_cosechada_maiz_verano
        except:
            rendimiento_maiz_verano = 0

        total_area_cosechada_frijol_verano = filtro.filter(cultivostradicionales__cultivo=2,
                                            year=anio[0],estacion=1).aggregate(t=Sum('cultivostradicionales__area_cosechada'))['t']
        total_cosecha_frijol_verano = filtro.filter(cultivostradicionales__cultivo=2,
                                            year=anio[0],estacion=1).aggregate(t=Sum('cultivostradicionales__cantidad_cosechada'))['t']
        try:
            rendimiento_frijol_verano = total_cosecha_frijol_verano / total_area_cosechada_frijol_verano
        except:
            rendimiento_frijol_verano = 0

        #calculo de los rendimiento invierno
        total_area_cosechada_maiz_invierno = filtro.filter(cultivostradicionales__cultivo=3,
                                    year=anio[0],estacion=2).aggregate(t=Sum('cultivostradicionales__area_cosechada'))['t'] or 0
        total_cosecha_maiz_invierno = filtro.filter(cultivostradicionales__cultivo=3,
                                    year=anio[0],estacion=2).aggregate(t=Sum('cultivostradicionales__cantidad_cosechada'))['t'] or 0
        try:
            rendimiento_maiz_invierno = total_cosecha_maiz_invierno / total_area_cosechada_maiz_invierno
        except:
            rendimiento_maiz_invierno = 0

        total_area_cosechada_frijol_invierno = filtro.filter(cultivostradicionales__cultivo=2,
                                            year=anio[0],estacion=2).aggregate(t=Sum('cultivostradicionales__area_cosechada'))['t'] or 0
        total_cosecha_frijol_invierno = filtro.filter(cultivostradicionales__cultivo=2,
                                            year=anio[0],estacion=2).aggregate(t=Sum('cultivostradicionales__cantidad_cosechada'))['t'] or 0
        try:
            rendimiento_frijol_invierno = total_cosecha_frijol_invierno / total_area_cosechada_frijol_invierno
        except:
            rendimiento_frijol_invierno = 0
        tiempo_rendimiento[anio[1]] = (rendimiento_maiz_verano,
                                       rendimiento_maiz_invierno,
                                       rendimiento_frijol_verano,
                                       rendimiento_frijol_invierno)
        #Calculos de los kcalorias
        tiempo_kcalorias[anio[1]] = [envio_calorias_pais(request, anio[0], 1), envio_calorias_pais(request, anio[0], 2)]


    return render(request,template,locals())

def detalle_finca(request, template='detalle_finca.html', entrevistado_id=None):
    detalle = Encuesta.objects.filter(entrevistado_id=entrevistado_id).order_by('year')

    #años que tiene ese productor
    years = []
    for en in Encuesta.objects.filter(entrevistado_id=entrevistado_id).order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    #para el mapa
    latitud = 0
    longitud = 0
    for obj in detalle:
        if obj.entrevistado.latitud:
            latitud = obj.entrevistado.latitud
        else:
            latitud = obj.entrevistado.municipio.latitud
        if obj.entrevistado.longitud:
            longitud = obj.entrevistado.longitud
        else:
            longitud = obj.entrevistado.municipio.longitud
    #fin del mapa
    #los años del detalle del productor
    gran_dicc = {}
    for year in years:
        detalle1 = detalle.filter(year=year[0])
        #calculo ingreso vs gasto
        gasto_total = detalle.filter(year=year[0]).aggregate(t=Sum('totalingreso__total_gasto'))['t']
        gasto_total_fuera = detalle.filter(year=year[0]).aggregate(t=Sum('totalingreso__total_gasto_fuera_finca'))['t']

        ingreso_total = detalle.filter(year=year[0]).aggregate(t=Sum('totalingreso__total'))['t']
        total_gastos = gasto_total + gasto_total_fuera

        ingreso_cultivo_tradicional = {}
        for obj in Cultivos.objects.all():
            cultivo = CultivosTradicionales.objects.filter(encuesta__entrevistado__departamento=request.session['departamento'],
                                                            cultivo=obj, encuesta__entrevistado__id=entrevistado_id, encuesta__year=year[0])
            cosechada = cultivo.aggregate(t=Sum('cantidad_cosechada'))['t']
            venta = cultivo.aggregate(t=Sum('venta'))['t']
            precio = cultivo.aggregate(t=Avg('precio'))['t']
            try:
                ingreso = venta * precio
            except:
                ingreso = 0
            costo = cultivo.aggregate(t=Avg('costo'))['t']
            if venta > 0:
                ingreso_cultivo_tradicional[obj] = {'unidad':obj.get_unidad_medida_display(),
                                                'cantidad_cosechada':cosechada,
                                                'venta':venta,
                                                'precio':precio,
                                                'ingreso': ingreso,
                                                'costo':costo}

        ingreso_huertos = {}
        ingreso_patio = 0
        for obj in CultivosHuertos.objects.all():
            cultivo = CultivosHuertosFamiliares.objects.filter(cultivo=obj,
                                                            encuesta__entrevistado__id=entrevistado_id,
                                                            encuesta__year=year[0])
            cosechada = cultivo.aggregate(t=Sum('cantidad_cosechada'))['t']
            venta = cultivo.aggregate(t=Sum('venta'))['t']
            precio = cultivo.aggregate(t=Avg('precio'))['t']
            try:
                ingreso = venta * precio
            except:
                ingreso = 0
            costo_huerto = CostoHuerto.objects.filter(encuesta__entrevistado__id=entrevistado_id,
                                                                                 encuesta__year=year[0]).aggregate(t=Avg('costo'))['t']
            ingreso_patio += ingreso

            if venta > 0:
                ingreso_huertos[obj] = {'unidad':obj.get_unidad_medida_display(),
                                                'cantidad_cosechada':cosechada,
                                                'venta':venta,
                                                'precio':precio,
                                                'ingreso': ingreso,
                                                }

        gran_dicc[year[1]] = (ingreso_total, total_gastos,ingreso_cultivo_tradicional, ingreso_huertos, detalle1)

    return render(request, template, locals())


def indicadores(request, template='indicadores.html'):
    #a = _queryset_filtrado(request)
    #indicadores = Encuesta.objects.filter(entrevistado__departamento=request.session['departamento']).distinct('entrevistado__id')
    total_entrevistados = Encuesta.objects.filter(entrevistado__departamento=request.session['departamento']).distinct('entrevistado__id').count()
    total_hombres = Encuesta.objects.filter(entrevistado__departamento=request.session['departamento'], entrevistado__sexo=2).distinct('entrevistado__id').count()
    total_mujeres = Encuesta.objects.filter(entrevistado__departamento=request.session['departamento'], entrevistado__sexo=1).distinct('entrevistado__id').count()

    porcentaje_hombres = float(total_hombres) / float(total_entrevistados) * 100
    porcentaje_mujeres = float(total_mujeres) / float(total_entrevistados) * 100

    organizaciones = Encuesta.objects.filter(entrevistado__departamento=request.session['departamento']).distinct('entrevistado__departamento').count()
    familias = Entrevistados.objects.count()

    #años que tiene ese productor
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    #-------- Ingresos por años ----------
    model_dict = {
    'Procesamiento': Procesamiento,
    'Ganaderia': Ganaderia,
    'Cultivos huertos familiares': CultivosHuertosFamiliares,
    'Cultivos tradicionales': CultivosTradicionales,
    'Fuentes': Fuentes,
    'Cultivos frutas finca': CultivosFrutasFinca,

    }

    dicc1 = OrderedDict()
    for name,value in model_dict.items():
        dicc1[name] = OrderedDict()
        for year in years:
            valor = value.objects.filter(encuesta__year=year[0]).aggregate(t=Sum('total'))['t']
            dicc1[name][year[1]] = valor

    #------------ Gasto del hogar ------
    dicc2 = OrderedDict()
    for obj in CHOICE_TIPO_GASTOS:
        dicc2[obj[1]] = OrderedDict()
        for year in years:
            valor = GastoHogar.objects.filter(encuesta__year=year[0], tipo=obj[0]).aggregate(t=Sum('total'))['t']
            dicc2[obj[1]][year[1]] = valor

    #Ingresos vs gastos por años
    ingreso_dicc = OrderedDict()
    for year in years:
        ingreso_total = Encuesta.objects.filter(year=year[0]).aggregate(t=Sum('totalingreso__total'))['t']
        total_poll = Encuesta.objects.filter(year=year[0]).count()
        try:
            porcentaje = saca_porcentajes(ingreso_total,total_poll,False)
        except:
            porcentaje = 0
        ingreso_dicc[year[1]] = porcentaje

    return render(request, template, locals())


def indicadores1(request, template='indicadores1.html'):
    request.session['encuestados'] = 0
    if request.method == 'POST':
        mensaje = None
        form = ConsultarForm(request.POST)
        if form.is_valid():
            request.session['estacion'] = form.cleaned_data['estacion']
            request.session['pais'] = form.cleaned_data['pais']
            request.session['departamento'] = form.cleaned_data['departamento']
            request.session['organizacion'] = form.cleaned_data['organizacion']
            request.session['municipio'] = form.cleaned_data['municipio']
            request.session['comunidad'] = form.cleaned_data['comunidad']

            mensaje = "Todas las variables estan correctamente :)"
            request.session['activo'] = True
            centinela = 1
            request.session['encuestados'] = len(_queryset_filtrado(request))

            #return HttpResponseRedirect('/indicadores1/')

        else:
            centinela = 0
            print "fail no entro bien"

    else:
        form = ConsultarForm()
        mensaje = "Existen alguno errores"
        centinela = 0
        #filtro = _queryset_filtrado(request)
        if 'pais' in request.session:
            try:
                del request.session['estacion']
                del request.session['pais']
                del request.session['departamento']
                del request.session['organizacion']
                del request.session['municipio']
                del request.session['comunidad']
                #del request.session['encuestados']
            except:
                pass
            request.session['activo'] = False

    return render(request, template, locals())

#FUNCIONES PARA LAS DEMAS SALIDAS DEL SISTEMA

def sexo_duenos(request, template="indicadores/sexo_duenos.html"):
    filtro = _queryset_filtrado(request)
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    dicc_sexo_dueno = OrderedDict()
    for year in years:
        filtro1 = filtro.filter(year=year[0]).count()
        si_dueno = filtro.filter(year=year[0], dueno=1).count()
        no_dueno = filtro.filter(year=year[0], dueno=2).count()

        a_nombre = {}
        for obj in CHOICE_DUENO_SI:
            conteos = filtro.filter(year=year[0], duenosi__si=obj[0]).count()
            a_nombre[obj[1]] = conteos

        situacion = {}
        for obj in CHOICE_DUENO_NO:
            conteos = filtro.filter(year=year[0], duenono__no=obj[0]).count()
            situacion[obj[1]] = conteos

        sexo_jefe_hogar = {}
        for obj in CHOICE_SEXO:
            conteos = filtro.filter(year=year[0], sexomiembros__sexo=obj[0]).count()
            sexo_jefe_hogar[obj[1]] = conteos

        personas_habitan = {}
        for obj in CHOICE_SEXO:
            conteos = filtro.filter(year=year[0], sexomiembros__sexo=obj[0]).aggregate(t=Sum('sexomiembros__cantidad'))['t']
            if conteos > 0:
                personas_habitan[obj[1]] = conteos

        total_personas = sum(list([ i for i in personas_habitan.values()]))

        detalle_edad = {}
        for obj in CHOICE_EDAD:
            conteos = filtro.filter(year=year[0], detallemiembros__edad=obj[0]).aggregate(t=Sum('detallemiembros__cantidad'))['t']
            if conteos > 0:
                detalle_edad[obj[1]] = conteos

        dicc_sexo_dueno[year[1]] = (si_dueno,no_dueno,a_nombre,situacion,sexo_jefe_hogar,personas_habitan,detalle_edad,total_personas,filtro1)

    return render(request, template, locals())

def escolaridad(request, template="indicadores/escolaridad.html"):
    filtro = _queryset_filtrado(request)

    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    dicc_escolaridad = OrderedDict()
    dicc_grafo_tipo_educacion = OrderedDict()
    for year in years:
        filtro1 = filtro.filter(year=year[0]).count()
        cantidad_miembros_hombres = filtro.filter(year=year[0],
                                    entrevistado__departamento=request.session['departamento'],
                                    entrevistado__sexo=2,
                                    entrevistado__jefe=1).aggregate(num_total = Sum('escolaridad__total'))['num_total']

        cantidad_miembros_mujeres = filtro.filter(year=year[0],
                                    entrevistado__departamento=request.session['departamento'],
                                    entrevistado__sexo=1,
                                    entrevistado__jefe=1).aggregate(num_total = Sum('escolaridad__total'))['num_total']

        grafo_educacion_hombre = filtro.filter(year=year[0],
                                    entrevistado__departamento=request.session['departamento'],
                                    entrevistado__sexo=2,
                                    entrevistado__jefe=1).aggregate(
                                    no_sabe_leer = Sum('escolaridad__no_leer'),
                                    primaria_incompleta = Sum('escolaridad__pri_incompleta'),
                                    primaria_completa = Sum('escolaridad__pri_completa'),
                                    secundaria_incompleta = Sum('escolaridad__secu_incompleta'),
                                    bachiller = Sum('escolaridad__bachiller'),
                                    universitario = Sum('escolaridad__uni_tecnico'),
                                )

        grafo_educacion_mujer = filtro.filter(year=year[0],
                                    entrevistado__sexo=1,
                                    entrevistado__jefe=1).aggregate(
                                    no_sabe_leer = Sum('escolaridad__no_leer'),
                                    primaria_incompleta = Sum('escolaridad__pri_incompleta'),
                                    primaria_completa = Sum('escolaridad__pri_completa'),
                                    secundaria_incompleta = Sum('escolaridad__secu_incompleta'),
                                    bachiller = Sum('escolaridad__bachiller'),
                                    universitario = Sum('escolaridad__uni_tecnico'),
                                )

        tabla_educacion_hombre = []
        for e in CHOICE_ESCOLARIDAD:
            objeto = filtro.filter(year=year[0], escolaridad__sexo = e[0],
                    entrevistado__sexo=2,
                    entrevistado__jefe=1).aggregate(num_total = Sum('escolaridad__total'),
                    no_leer = Sum('escolaridad__no_leer'),
                    p_incompleta = Sum('escolaridad__pri_incompleta'),
                    p_completa = Sum('escolaridad__pri_completa'),
                    s_incompleta = Sum('escolaridad__secu_incompleta'),
                    bachiller = Sum('escolaridad__bachiller'),
                    universitario = Sum('escolaridad__uni_tecnico'),

                    )

            fila = [e[1], objeto['num_total'],
                    saca_porcentajes(objeto['no_leer'], objeto['num_total'], False),
                    saca_porcentajes(objeto['p_incompleta'], objeto['num_total'], False),
                    saca_porcentajes(objeto['p_completa'], objeto['num_total'], False),
                    saca_porcentajes(objeto['s_incompleta'], objeto['num_total'], False),
                    saca_porcentajes(objeto['bachiller'], objeto['num_total'], False),
                    saca_porcentajes(objeto['universitario'], objeto['num_total'], False),
                    ]
            tabla_educacion_hombre.append(fila)

            #tabla para cuando la mujer es jefe

        tabla_educacion_mujer = []
        for e in CHOICE_ESCOLARIDAD:
            objeto = filtro.filter(year=year[0],
                    escolaridad__sexo = e[0],
                    entrevistado__sexo=1,
                    entrevistado__jefe=1).aggregate(num_total = Sum('escolaridad__total'),
                    no_leer = Sum('escolaridad__no_leer'),
                    p_incompleta = Sum('escolaridad__pri_incompleta'),
                    p_completa = Sum('escolaridad__pri_completa'),
                    s_incompleta = Sum('escolaridad__secu_incompleta'),
                    bachiller = Sum('escolaridad__bachiller'),
                    universitario = Sum('escolaridad__uni_tecnico'),

                    )
            fila = [e[1], objeto['num_total'],
                    saca_porcentajes(objeto['no_leer'], objeto['num_total'], False),
                    saca_porcentajes(objeto['p_incompleta'], objeto['num_total'], False),
                    saca_porcentajes(objeto['p_completa'], objeto['num_total'], False),
                    saca_porcentajes(objeto['s_incompleta'], objeto['num_total'], False),
                    saca_porcentajes(objeto['bachiller'], objeto['num_total'], False),
                    saca_porcentajes(objeto['universitario'], objeto['num_total'], False),
                    ]
            tabla_educacion_mujer.append(fila)
        dicc_escolaridad[year[1]] = (tabla_educacion_hombre,tabla_educacion_mujer,filtro1)
        dicc_grafo_tipo_educacion[year[1]] = (grafo_educacion_hombre, grafo_educacion_mujer, cantidad_miembros_hombres, cantidad_miembros_mujeres)

    return render(request, template, locals())

def energia(request, template="indicadores/energia.html"):
    filtro = _queryset_filtrado(request)
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    dicc_energia = OrderedDict()
    for year in years:
        filtro1 = filtro.filter(year=year[0]).count()
        grafo_tipo_energia = {}
        for obj in Energia.objects.all():
            valor = filtro.filter(year=year[0], tipoenergia__tipo=obj).count()
            grafo_tipo_energia[obj] =  valor

        grafo_panel_solar = {}
        for obj in CHOICE_PANEL_SOLAR:
            valor = filtro.filter(year=year[0], panelsolar__panel=obj[0]).count()
            grafo_panel_solar[obj[1]] =  valor

        grafo_fuente_energia = {}
        for obj in FuenteEnergia.objects.all():
            valor = filtro.filter(year=year[0], energiasolarcocinar__fuente=obj).count()
            grafo_fuente_energia[obj] =  valor

        grafo_tipo_cocina = {}
        for obj in Cocinas.objects.all():
            valor = filtro.filter(year=year[0], tipococinas__cocina=obj).count()
            grafo_tipo_cocina[obj] =  valor

        dicc_energia[year[1]] = (grafo_tipo_energia,grafo_panel_solar,grafo_fuente_energia,grafo_tipo_cocina,filtro1)

    return render(request, template, locals())

def agua(request, template="indicadores/agua.html"):
    filtro = _queryset_filtrado(request)
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    dicc_agua = OrderedDict()
    for year in years:
        filtro1 = filtro.filter(year=year[0]).count()
        grafo_agua_consumo = {}
        for obj in AguaConsumo.objects.all():
            valor = filtro.filter(year=year[0], accesoagua__agua=obj).count()
            grafo_agua_consumo[obj] =  valor

        grafo_agua_disponibilidad = {}
        for obj in CHOICE_DISPONIBILIDAD:
            valor = filtro.filter(year=year[0], disponibilidadagua__disponibilidad=obj[0]).count()
            grafo_agua_disponibilidad[obj[1]] =  valor

        grafo_agua_calidad = {}
        for obj in CHOICE_CALIDAD_AGUA:
            valor = filtro.filter(year=year[0], calidadagua__calidad=obj[0]).count()
            grafo_agua_calidad[obj[1]] =  valor

        grafo_agua_contaminada = {}
        for obj in TipoContamindaAgua.objects.all():
            valor = filtro.filter(year=year[0], contaminada__contaminada=obj).count()
            grafo_agua_contaminada[obj] =  valor

        grafo_agua_tratamiento = {}
        for obj in CHOICE_TRATAMIENTO:
            valor = filtro.filter(year=year[0], tratamientoagua__tratamiento=obj[0]).count()
            grafo_agua_tratamiento[obj[1]] =  valor

        grafo_agua_usos = {}
        for obj in CHOICE_OTRO_USO:
            valor = filtro.filter(year=year[0], usosagua__uso=obj[0]).count()
            grafo_agua_usos[obj[1]] =  valor

        dicc_agua[year[1]] = (grafo_agua_consumo,grafo_agua_disponibilidad,grafo_agua_calidad,grafo_agua_contaminada,grafo_agua_tratamiento,grafo_agua_usos,filtro1)

    return render(request, template, locals())

def organizaciones(request, template="indicadores/organizaciones.html"):
    filtro = _queryset_filtrado(request)
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    dicc_organizacion = OrderedDict()
    for year in years:
        filtro1 = filtro.filter(year=year[0]).count()
        grafo_pertenece = {}
        for obj in CHOICE_JEFE:
            valor = filtro.filter(year=year[0], organizacioncomunitaria__pertenece=obj[0]).count()
            grafo_pertenece[obj[1]] =  valor

        grafo_org_comunitarias = {}
        for obj in OrgComunitarias.objects.all():
            valor = filtro.filter(year=year[0], organizacioncomunitaria__caso_si=obj).count()
            if valor > 0:
                grafo_org_comunitarias[obj] =  valor

        grafo_beneficios = {}
        for obj in BeneficiosOrganizados.objects.all():
            valor = filtro.filter(year=year[0], organizacioncomunitaria__cuales_beneficios=obj).count()
            if valor > 0:
                grafo_beneficios[obj] =  valor

        dicc_organizacion[year[1]] = (grafo_pertenece,grafo_org_comunitarias, grafo_beneficios,filtro1)

    return render(request, template, locals())

def tierra(request, template="indicadores/tierra.html"):
    filtro = _queryset_filtrado(request)
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    dicc_tierra = OrderedDict()
    for year in years:
        #tabla distribucion de frecuencia
        filtro1 = filtro.filter(year=year[0]).count()
        uno_num = filtro.filter(year=year[0], organizacionfinca__area_finca__range=(0.1,5.99)).count()
        seis_num = filtro.filter(year=year[0], organizacionfinca__area_finca__range=(6,10.99)).count()
        diez_mas = filtro.filter(year=year[0], organizacionfinca__area_finca__gt=11).count()

        #promedio de manzanas por todas las personas
        promedio_mz = filtro.filter(year=year[0]).aggregate(p=Avg('organizacionfinca__area_finca'))['p']

        grafo_distribucion_tierra = {}
        for obj in CHOICE_TIERRA:
            valor = filtro.filter(year=year[0],entrevistado__departamento=request.session['departamento'], distribuciontierra__tierra=obj[0]).count()
            grafo_distribucion_tierra[obj[1]] =  valor

        dicc_tierra[year[1]] = (uno_num,seis_num,diez_mas,promedio_mz,grafo_distribucion_tierra,filtro1)


    return render(request, template, locals())

def prestamos(request, template="indicadores/prestamo.html"):
    filtro = _queryset_filtrado(request)
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    dicc_prestamos = OrderedDict()
    for year in years:
        filtro1 = filtro.filter(year=year[0]).count()
        grafo_prestamo_sino = {}
        for obj in CHOICE_JEFE:
            valor = filtro.filter(year=year[0], prestamo__algun_prestamo=obj[0]).count()
            grafo_prestamo_sino[obj[1]] =  valor

        grafo_recibe_prestamo = {}
        for obj in RecibePrestamo.objects.all():
            valor = filtro.filter(year=year[0], prestamo__recibe=obj).count()
            if valor > 0:
                grafo_recibe_prestamo[obj] =  valor

        grafo_uso_prestamo = {}
        for obj in UsoPrestamo.objects.all():
            valor = filtro.filter(year=year[0], prestamo__uso=obj).count()
            if valor > 0:
                grafo_uso_prestamo[obj] =  valor

        dicc_prestamos[year[1]] = (grafo_prestamo_sino,grafo_recibe_prestamo,grafo_uso_prestamo,filtro1)

    return render(request, template, locals())

def practicas(request, template="indicadores/practicas.html"):
    filtro = _queryset_filtrado(request)
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    dicc_practicas = OrderedDict()
    for year in years:
        filtro1 = filtro.filter(year=year[0]).count()
        grafo_practicas_sino = {}
        for obj in CHOICE_JEFE:
            valor = filtro.filter(year=year[0], practicasagroecologicas__si_no=obj[0]).count()
            grafo_practicas_sino[obj[1]] =  valor

        grafo_manejo = {}
        for obj in CHOICE_MANEJO:
            valor = filtro.filter(year=year[0], practicasagroecologicas__manejo=obj[0]).count()
            grafo_manejo[obj[1]] =  valor

        grafo_traccion = {}
        for obj in CHOICE_TRACCION:
            valor = filtro.filter(year=year[0], practicasagroecologicas__traccion=obj[0]).count()
            grafo_traccion[obj[1]] =  valor

        grafo_fertilidad = {}
        for obj in CHOICE_JEFE:
            valor = filtro.filter(year=year[0], practicasagroecologicas__fertilidad=obj[0]).count()
            grafo_fertilidad[obj[1]] =  valor

        grafo_control = {}
        for obj in CHOICE_JEFE:
            valor = filtro.filter(year=year[0], practicasagroecologicas__control=obj[0]).count()
            grafo_control[obj[1]] =  valor

        dicc_practicas[year[1]] = (grafo_practicas_sino,grafo_manejo,grafo_traccion,grafo_fertilidad,grafo_control,filtro1)

    return render(request, template, locals())

def seguridad(request, template="indicadores/seguridad.html"):
    filtro = _queryset_filtrado(request)
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    dicc_seguridad = OrderedDict()
    for year in years:
        filtro1 = filtro.filter(year=year[0]).count()
        grafo_economico = {}
        for obj in CHOICE_JEFE:
            valor = filtro.filter(year=year[0], seguridadalimentaria__economico=obj[0]).count()
            grafo_economico[obj[1]] =  valor

        grafo_secado = {}
        for obj in CHOICE_JEFE:
            valor = filtro.filter(year=year[0], seguridadalimentaria__secado=obj[0]).count()
            grafo_secado[obj[1]] =  valor

        grafo_tipo_secado = {}
        for obj in TipoSecado.objects.all():
            valor = filtro.filter(year=year[0], seguridadalimentaria__tipo_secado=obj).count()
            grafo_tipo_secado[obj] =  valor

        grafo_plan_cosecha = {}
        for obj in CHOICE_JEFE:
            valor = filtro.filter(year=year[0], seguridadalimentaria__plan_cosecha=obj[0]).count()
            grafo_plan_cosecha[obj[1]] =  valor

        grafo_ayuda = {}
        for obj in CHOICE_JEFE:
            valor = filtro.filter(year=year[0], seguridadalimentaria__ayuda=obj[0]).count()
            grafo_ayuda[obj[1]] =  valor

        grafo_suficiente_alimento = {}
        for obj in CHOICE_JEFE:
            valor = filtro.filter(year=year[0], seguridadalimentaria__suficiente_alimento=obj[0]).count()
            grafo_suficiente_alimento[obj[1]] =  valor

        grafo_consumo_diario = {}
        for obj in CHOICE_JEFE:
            valor = filtro.filter(year=year[0], seguridadalimentaria__consumo_diario=obj[0]).count()
            grafo_consumo_diario[obj[1]] =  valor


        conteo_fenomeno = {}
        for obj in CHOICE_FENOMENOS:
            valor = filtro.filter(year=year[0], respuestano41__fenomeno=obj[0]).count()
            conteo_fenomeno[obj[1]] =  valor

        conteo_agricola = {}
        for obj in CHOICE_AGRICOLA:
            valor = filtro.filter(year=year[0], respuestano41__agricola=obj[0]).count()
            conteo_agricola[obj[1]] =  valor

        conteo_mercado = {}
        for obj in CHOICE_MERCADO:
            valor = filtro.filter(year=year[0], respuestano41__mercado=obj[0]).count()
            conteo_mercado[obj[1]] =  valor

        conteo_inversion = {}
        for obj in CHOICE_INVERSION:
            valor = filtro.filter(year=year[0], respuestano41__inversion=obj[0]).count()
            conteo_inversion[obj[1]] =  valor

        grafo_adquiere_agua = {}
        for obj in AdquiereAgua.objects.all():
            valor = filtro.filter(year=year[0], otrasseguridad__adquiere_agua=obj).count()
            grafo_adquiere_agua[obj] =  valor

        grafo_tratamiento_agua = {}
        for obj in CHOICE_JEFE:
            valor = filtro.filter(year=year[0], otrasseguridad__tratamiento=obj[0]).count()
            grafo_tratamiento_agua[obj[1]] =  valor

        grafo_tipo_tratamientos = {}
        for obj in TrataAgua.objects.all():
            valor = filtro.filter(year=year[0], otrasseguridad__tipo_tratamiento=obj).count()
            grafo_tipo_tratamientos[obj] =  valor

        dicc_seguridad[year[1]] = (grafo_economico,
                                    grafo_secado,
                                    grafo_tipo_secado,
                                    grafo_plan_cosecha,
                                    grafo_ayuda,
                                    grafo_suficiente_alimento,
                                    grafo_consumo_diario,
                                    conteo_fenomeno,
                                    conteo_agricola,
                                    conteo_mercado,
                                    conteo_inversion,
                                    grafo_adquiere_agua,
                                    grafo_tratamiento_agua,
                                    grafo_tipo_tratamientos,
                                    filtro1)

    return render(request, template, locals())

def genero(request, template="indicadores/genero.html"):
    filtro = _queryset_filtrado(request)
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    dicc_genero = OrderedDict()
    for year in years:
        filtro1 = filtro.filter(year=year[0]).count()
        porcentaje_aporta_mujer = OrderedDict()
        for obj in CHOICER_INGRESO:
            porcentaje_aporta_mujer[obj[1]] = OrderedDict()
            for obj2 in CHOICE_PORCENTAJE:
                valor = filtro.filter(year=year[0], genero__tipo=obj[0], genero__porcentaje=obj2[0]).count()
                if valor > 0:
                    porcentaje_aporta_mujer[obj[1]][obj2[1]] =  valor


        grafo_credito_mujer = {}
        for obj in CHOICE_JEFE:
            valor = filtro.filter(year=year[0], genero1__tipo=obj[0]).count()
            grafo_credito_mujer[obj[1]] =  valor

        grafo_bienes_mujer = {}
        for obj in CHOICER_COSAS_MUJER:
            valor_si = filtro.filter(year=year[0], genero2__pregunta=obj[0], genero2__respuesta=1).count()
            valor_no = filtro.filter(year=year[0], genero2__pregunta=obj[0], genero2__respuesta=2).count()
            grafo_bienes_mujer[obj[1]] =  (valor_si, valor_no)

        grafo_organizacion_mujer = {}
        for obj in CHOICE_JEFE:
            valor = filtro.filter(year=year[0], genero3__respuesta=obj[0]).count()
            grafo_organizacion_mujer[obj[1]] =  valor

        mujer_organizacion = {}
        for obj in OrgComunitarias.objects.all():
            dato = filtro.filter(year=year[0],organizacioncomunitaria__caso_si=obj,entrevistado__jefe=1).count()
            if dato > 0:
                mujer_organizacion[obj] = dato


        nivel_educacion_mujer = OrderedDict()
        for obj in CHOICER_NIVEL_MUJER:
            valor = filtro.filter(year=year[0],genero4__opcion=obj[0]).count()
            nivel_educacion_mujer[obj[1]] =  valor

        dicc_genero[year[1]] = (porcentaje_aporta_mujer,
                                  grafo_credito_mujer,
                                  grafo_bienes_mujer,
                                  grafo_organizacion_mujer,
                                  mujer_organizacion,
                                  nivel_educacion_mujer,
                                  filtro1,
                                  )

    return render(request, template, locals())

from django.views.decorators.cache import cache_page

@cache_page(60 * 15)
def ingreso_optimizado(request, template="indicadores/ingresos_opt.html"):
    #años de encuestas
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    dicc_ingresos = OrderedDict()
    for year in years:

        #ingreso de cultivos tracionales

        ingreso_cultivo_tradicional = {}
        for obj in Cultivos.objects.all():
            cultivo = CultivosTradicionales.objects.filter(encuesta__year=year[0],encuesta__entrevistado__departamento=request.session['departamento'],
                                                            cultivo=obj)
            cosechada = cultivo.aggregate(t=Sum('cantidad_cosechada'))['t']
            venta = cultivo.aggregate(t=Sum('venta'))['t']
            precio = cultivo.aggregate(t=Avg('precio'))['t']
            try:
                ingreso = venta * precio
            except:
                ingreso = 0
            costo = cultivo.aggregate(t=Avg('costo'))['t']
            if venta > 0:
                try:
                    utilidad = ingreso - costo
                except:
                    pass
                ingreso_cultivo_tradicional[obj] = {'unidad':obj.get_unidad_medida_display(),
                                                'cantidad_cosechada':cosechada,
                                                'venta':venta,
                                                'precio':precio,
                                                'ingreso': ingreso,
                                                'costo':costo,
                                                'utilidad': utilidad}

        total_utilidad_tradicional = sum(list([ i['utilidad'] for i in ingreso_cultivo_tradicional.values()]))
        total_ingreso_tradicional = sum(list([ i['ingreso'] for i in ingreso_cultivo_tradicional.values()]))
        total_costo_tradicional = sum(list([ i['costo'] for i in ingreso_cultivo_tradicional.values()]))
        #cultivos huertos familiares

        dicc_ingresos[year[1]] = (
                            ingreso_cultivo_tradicional,
                            total_utilidad_tradicional,
                            total_ingreso_tradicional,
                            total_costo_tradicional,

                            )

    return render(request, template, locals())

def ingresos(request, template="indicadores/ingresos.html"):
    filtro = _queryset_filtrado(request)
    request.session["encuestados"] = filtro.count()
    #años de encuestas
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    dicc_ingresos = OrderedDict()
    for year in years:
        filtro1 = filtro.filter(year=year[0]).count()
        percibe_ingreso = {}
        for obj in CHOICE_JEFE:
            valor = filtro.filter(year=year[0], percibeingreso__si_no=obj[0]).count()
            percibe_ingreso[obj[1]] =  valor

        fuente_ingresos = {}
        for obj in TipoFuenteIngreso.objects.all():
            valor = filtro.filter(year=year[0], fuentes__fuente_ingreso=obj).count()
            fuente_ingresos[obj] =  valor

        #ingreso de cultivos tracionales

        ingreso_cultivo_tradicional = {}
        for obj in Cultivos.objects.all():
            cultivo = filtro.filter(year=year[0],
                                    cultivostradicionales__cultivo=obj)
            cosechada = cultivo.aggregate(t=Sum('cultivostradicionales__cantidad_cosechada'))['t']
            venta = cultivo.aggregate(t=Sum('cultivostradicionales__venta'))['t']
            precio = cultivo.aggregate(t=Avg('cultivostradicionales__precio'))['t']
            try:
                ingreso = venta * precio
            except:
                ingreso = 0
            costo = cultivo.aggregate(t=Avg('cultivostradicionales__costo'))['t']
            if venta > 0:
                try:
                    utilidad = ingreso - costo
                except:
                    pass
                ingreso_cultivo_tradicional[obj] = {'unidad':obj.get_unidad_medida_display(),
                                                'cantidad_cosechada':cosechada,
                                                'venta':venta,
                                                'precio':precio,
                                                'ingreso': ingreso,
                                                'costo':costo,
                                                'utilidad': utilidad}

        total_utilidad_tradicional = sum(list([ i['utilidad'] for i in ingreso_cultivo_tradicional.values()]))
        total_ingreso_tradicional = sum(list([ i['ingreso'] for i in ingreso_cultivo_tradicional.values()]))
        total_costo_tradicional = sum(list([ i['costo'] for i in ingreso_cultivo_tradicional.values()]))
        #cultivos huertos familiares

        ingreso_huertos = {}
        ingreso_patio = 0
        for obj in CultivosHuertos.objects.all():
            cultivo = filtro.filter(year=year[0],
                                    cultivoshuertosfamiliares__cultivo=obj)
            cosechada = cultivo.aggregate(t=Sum('cultivoshuertosfamiliares__cantidad_cosechada'))['t']
            venta = cultivo.aggregate(t=Sum('cultivoshuertosfamiliares__venta'))['t']
            precio = cultivo.aggregate(t=Avg('cultivoshuertosfamiliares__precio'))['t']
            try:
                ingreso = venta * precio
            except:
                ingreso = 0
            costo_huerto = filtro.filter(year=year[0]).aggregate(t=Avg('costohuerto__costo'))['t']
            ingreso_patio += ingreso

            if venta > 0:
                ingreso_huertos[obj] = {'unidad':obj.get_unidad_medida_display(),
                                                'cantidad_cosechada':cosechada,
                                                'venta':venta,
                                                'precio':precio,
                                                'ingreso': ingreso,
                                                }
        try:
            utilidad_huerto_patio = ingreso_patio - costo_huerto
        except:
            utilidad_huerto_patio = 0
        # cultivos frutales

        ingreso_frutales = {}
        ingreso_fruta = 0
        for obj in CultivosFrutas.objects.all():
            cultivo = filtro.filter(year=year[0],
                                    cultivosfrutasfinca__cultivo=obj)
            cosechada = cultivo.aggregate(t=Sum('cultivosfrutasfinca__cantidad_cosechada'))['t']
            venta = cultivo.aggregate(t=Sum('cultivosfrutasfinca__venta'))['t']
            precio = cultivo.aggregate(t=Avg('cultivosfrutasfinca__precio'))['t']
            try:
                ingreso = venta * precio
            except:
                ingreso = 0
            costo_fruta = filtro.filter(year=year[0]).aggregate(t=Avg('costofrutas__costo'))['t']

            ingreso_fruta += ingreso
            if venta > 0:
                ingreso_frutales[obj] = {'unidad':obj.get_unidad_medida_display(),
                                                'cantidad_cosechada':cosechada,
                                                'venta':venta,
                                                'precio':precio,
                                                'ingreso': ingreso,
                                                }
        try:
            utilidad_frutas = ingreso_fruta - costo_fruta
        except:
            utilidad_frutas = 0
        # animales en la finca

        ingreso_ganaderia = {}
        for obj in Animales.objects.all():
            cultivo = filtro.filter(year=year[0],
                                    ganaderia__animal=obj)
            cantidad = cultivo.aggregate(t=Avg('ganaderia__cantidad'))['t']
            venta = cultivo.aggregate(t=Sum('ganaderia__cantidad_vendida'))['t']
            precio = cultivo.aggregate(t=Avg('ganaderia__precio'))['t']
            try:
                ingreso = venta * precio
            except:
                ingreso = 0

            if venta > 0:
                ingreso_ganaderia[obj] = {'cantidad':cantidad,
                                        'venta':venta,
                                        'precio':precio,
                                        'ingreso': ingreso,
                                        }

        total_ingreso_ganado = sum(list([ i['ingreso'] for i in ingreso_ganaderia.values()]))

        # comercializacion de productos procesados

        ingreso_procesado = {}
        for obj in ProductoProcesado.objects.all():
            cultivo = filtro.filter(year=year[0],
                                    procesamiento__producto=obj)
            cantidad = cultivo.aggregate(t=Avg('procesamiento__cantidad_total'))['t']
            venta = cultivo.aggregate(t=Sum('procesamiento__cantidad_vendida'))['t']
            precio = cultivo.aggregate(t=Avg('procesamiento__precio'))['t']
            try:
                ingreso = venta * precio
            except:
                ingreso = 0

            if venta > 0:
                ingreso_procesado[obj] = {'unidad':obj.get_unidad_medida_display(),
                                        'cantidad':cantidad,
                                        'venta':venta,
                                        'precio':precio,
                                        'ingreso': ingreso,
                                        }
        total_ingreso_procesado = sum(list([ i['ingreso'] for i in ingreso_procesado.values()]))
        gran_total_ingresos = 0
        try:
            gran_total_ingresos = float(total_utilidad_tradicional + utilidad_huerto_patio + utilidad_frutas + total_ingreso_ganado + total_ingreso_procesado) / filtro1
        except:
            pass
        dicc_ingresos[year[1]] = (percibe_ingreso,
                                fuente_ingresos,
                                ingreso_cultivo_tradicional,
                                total_utilidad_tradicional,
                                total_ingreso_tradicional,
                                total_costo_tradicional,
                                ingreso_huertos,
                                utilidad_huerto_patio,
                                ingreso_frutales,
                                utilidad_frutas,
                                ingreso_ganaderia,
                                total_ingreso_ganado,
                                ingreso_procesado,
                                total_ingreso_procesado,
                                ingreso_patio,
                                costo_huerto,
                                costo_fruta,
                                ingreso_fruta,
                                gran_total_ingresos,
                                filtro1,
                                )

    return render(request, template, locals())

def gastos(request, template="indicadores/gastos.html"):
    filtro = _queryset_filtrado(request)
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    dicc_gastos = OrderedDict()
    for year in years:
        filtro1 = filtro.filter(year=year[0]).count()
        introducido_tradicional = {}
        for obj in Cultivos.objects.all():
            valor = filtro.filter(year=year[0],
                                introducidostradicionales__cultivo=obj,
                                introducidostradicionales__si_no=1).count()
            if valor > 0:
                introducido_tradicional[obj] =  valor

        introducido_huerto = {}
        for obj in CultivosHuertos.objects.all():
            valor = filtro.filter(year=year[0],
                                introducidoshuertos__cultivo=obj,
                                introducidoshuertos__si_no=1).count()
            if valor > 0:
                introducido_huerto[obj] =  valor

        gasto_hogar = {}
        for obj in CHOICE_TIPO_GASTOS:
            valor = filtro.filter(year=year[0],
                                gastohogar__tipo=obj[0]).aggregate(t=Avg('gastohogar__cantidad'))['t']
            gasto_hogar[obj[1]] =  valor

        gasto_produccion = {}
        for obj in TipoGasto.objects.all():
            valor = filtro.filter(year=year[0],
                                gastoproduccion__tipo=obj).aggregate(t=Avg('gastoproduccion__cantidad'))['t']
            gasto_produccion[obj] =  valor

        dicc_gastos[year[1]] = (introducido_tradicional,
                                introducido_huerto,
                                gasto_hogar,
                                gasto_produccion,
                                filtro1,
                                )

    return render(request, template, locals())


def envio_calorias(request, anio, tiempo):
    filtro = Encuesta.objects.filter(year=anio,estacion=tiempo,entrevistado__departamento=request.session["departamento"])#.distinct('entrevistado__id')
    numero_total_habitante = filtro.aggregate(t=Sum('sexomiembros__cantidad'))['t']

    calorias_tradicional = {}
    for obj in Cultivos.objects.all():
        calculo = filtro.filter(cultivostradicionales__cultivo=obj).aggregate(t=Coalesce(Sum('cultivostradicionales__consumo_familia'), V(0)))['t']
        consumida = calculo / 12
        try:
            consumida_gramos = consumida * obj.calorias
            calorias_mes = float(consumida_gramos) / numero_total_habitante
            calorias_dia = calorias_mes / 30
            proteina = float(obj.proteinas*consumida)
            if calorias_dia > 0:
                calorias_tradicional[obj] = (consumida, obj.get_unidad_medida_display(),consumida_gramos,obj.calorias, obj.proteinas,calorias_dia,proteina)
        except:
            pass
    total_calorias_tradicional = sum(list([ i[5] for i in calorias_tradicional.values()]))
    total_proteina_tradicional = sum(list([ i[6] for i in calorias_tradicional.values()]))

    calorias_huerto = {}
    for obj in CultivosHuertos.objects.all():
        calculo = filtro.filter(cultivoshuertosfamiliares__cultivo=obj).aggregate(t=Coalesce(Sum('cultivoshuertosfamiliares__consumo_familia'), V(0)))['t']
        consumida = calculo / 12
        try:
            consumida_gramos = consumida * obj.calorias
            calorias_mes = float(consumida_gramos) / numero_total_habitante
            calorias_dia = calorias_mes / 30
            gramo_dia = float(obj.proteinas*consumida)
            if calorias_dia > 0:
                calorias_huerto[obj] = (consumida, obj.get_unidad_medida_display(),consumida_gramos,obj.calorias, obj.proteinas,calorias_dia,gramo_dia)
        except:
            pass

    total_calorias_huerto = sum(list([ i[5] for i in calorias_huerto.values()]))
    total_proteina_huerto = sum(list([ i[6] for i in calorias_huerto.values()]))

    calorias_fruta = {}
    for obj in CultivosFrutas.objects.all():
        calculo = filtro.filter(cultivosfrutasfinca__cultivo=obj).aggregate(t=Coalesce(Sum('cultivosfrutasfinca__consumo_familia'), V(0)))['t']
        consumida = calculo / 12
        try:
            consumida_gramos = consumida * obj.calorias
            calorias_mes = float(consumida_gramos) / numero_total_habitante
            calorias_dia = float(calorias_mes) / 30
            gramo_dia = float(obj.proteinas*consumida)
            if calorias_dia > 0:
                calorias_fruta[obj] = (consumida, obj.get_unidad_medida_display(),consumida_gramos,obj.calorias, obj.proteinas,calorias_dia,gramo_dia)
        except:
            pass
    total_calorias_fruta = sum(list([ i[5] for i in calorias_fruta.values()]))
    total_proteina_fruta = sum(list([ i[6] for i in calorias_fruta.values()]))

    calorias_procesado = {}
    for obj in ProductoProcesado.objects.all():
        calculo = filtro.filter(procesamiento__producto=obj).aggregate(t=Coalesce(Sum('procesamiento__cantidad'), V(0)))['t']
        consumida = calculo / 12
        try:
            consumida_gramos = consumida * obj.calorias
            calorias_mes = float(consumida_gramos) / numero_total_habitante
            calorias_dia = float(calorias_mes) / 30
            gramo_dia = float(obj.proteinas)
            if calorias_dia > 0:
                calorias_procesado[obj] = (consumida, obj.get_unidad_medida_display(),consumida_gramos,obj.calorias, obj.proteinas,calorias_dia,gramo_dia)
        except:
            pass
    total_calorias_procesado = sum(list([ i[5] for i in calorias_procesado.values()]))
    total_proteina_procesado = sum(list([ i[6] for i in calorias_procesado.values()]))

    calorias_fuera_finca = {}
    for obj in ProductosFueraFinca.objects.all():
        calculo = filtro.filter(alimentosfuerafinca__producto=obj).aggregate(t=Coalesce(Sum('alimentosfuerafinca__cantidad'), V(0)))['t']
        consumida = calculo / 12
        try:
            consumida_gramos = consumida * obj.calorias
            calorias_mes = float(consumida_gramos) / numero_total_habitante
            calorias_dia = float(calorias_mes) / 30
            gramo_dia = float(obj.proteinas)
            if calorias_dia > 0:
                calorias_fuera_finca[obj] = (consumida, obj.unidad_medida,consumida_gramos,obj.calorias, obj.proteinas,calorias_dia,gramo_dia)
        except:
            pass
    total_calorias_fuera_finca = sum(list([ i[5] for i in calorias_fuera_finca.values()]))
    total_proteina_fuera_finca = sum(list([ i[6] for i in calorias_fuera_finca.values()]))

    # datos = {'Kcal Cultivos Tradicional':total_calorias_tradicional,
    #         'Kcal Huertos de patio':total_calorias_huerto,
    #         'Kcal Frutas':total_calorias_fruta,
    #         'Kcal Productos procesados':total_calorias_procesado,
    #         'Kcal Productos comprados': total_calorias_fuera_finca}
    datos = [total_calorias_tradicional,
             total_calorias_huerto,
             total_calorias_fruta,
             total_calorias_procesado,
             total_calorias_fuera_finca]
    return datos

def envio_calorias_pais(request, anio, tiempo):
    filtro = Encuesta.objects.filter(year=anio,estacion=tiempo,entrevistado__pais=request.session['pais'])
    numero_total_habitante = filtro.aggregate(t=Sum('sexomiembros__cantidad'))['t']

    calorias_tradicional = {}
    for obj in Cultivos.objects.all():
        calculo = filtro.filter(cultivostradicionales__cultivo=obj).aggregate(t=Coalesce(Sum('cultivostradicionales__consumo_familia'), V(0)))['t']
        consumida = calculo / 12
        try:
            consumida_gramos = consumida * obj.calorias
            calorias_mes = float(consumida_gramos) / numero_total_habitante
            calorias_dia = calorias_mes / 30
            proteina = float(obj.proteinas*consumida)
            if calorias_dia > 0:
                calorias_tradicional[obj] = (consumida, obj.get_unidad_medida_display(),consumida_gramos,obj.calorias, obj.proteinas,calorias_dia,proteina)
        except:
            pass
    total_calorias_tradicional = sum(list([ i[5] for i in calorias_tradicional.values()]))
    total_proteina_tradicional = sum(list([ i[6] for i in calorias_tradicional.values()]))

    calorias_huerto = {}
    for obj in CultivosHuertos.objects.all():
        calculo = filtro.filter(cultivoshuertosfamiliares__cultivo=obj).aggregate(t=Coalesce(Sum('cultivoshuertosfamiliares__consumo_familia'), V(0)))['t']
        consumida = calculo / 12
        try:
            consumida_gramos = consumida * obj.calorias
            calorias_mes = float(consumida_gramos) / numero_total_habitante
            calorias_dia = calorias_mes / 30
            gramo_dia = float(obj.proteinas*consumida)
            if calorias_dia > 0:
                calorias_huerto[obj] = (consumida, obj.get_unidad_medida_display(),consumida_gramos,obj.calorias, obj.proteinas,calorias_dia,gramo_dia)
        except:
            pass
    total_calorias_huerto = sum(list([ i[5] for i in calorias_huerto.values()]))
    total_proteina_huerto = sum(list([ i[6] for i in calorias_huerto.values()]))

    calorias_fruta = {}
    for obj in CultivosFrutas.objects.all():
        calculo = filtro.filter(cultivosfrutasfinca__cultivo=obj).aggregate(t=Coalesce(Sum('cultivosfrutasfinca__consumo_familia'), V(0)))['t']
        consumida = calculo / 12
        consumida_gramos = consumida * obj.calorias
        try:
            calorias_mes = float(consumida_gramos) / numero_total_habitante
            calorias_dia = float(calorias_mes) / 30
            gramo_dia = float(obj.proteinas*consumida)
            if calorias_dia > 0:
                calorias_fruta[obj] = (consumida, obj.get_unidad_medida_display(),consumida_gramos,obj.calorias, obj.proteinas,calorias_dia,gramo_dia)
        except:
            pass
    total_calorias_fruta = sum(list([ i[5] for i in calorias_fruta.values()]))
    total_proteina_fruta = sum(list([ i[6] for i in calorias_fruta.values()]))

    calorias_procesado = {}
    for obj in ProductoProcesado.objects.all():
        calculo = filtro.filter(procesamiento__producto=obj).aggregate(t=Coalesce(Sum('procesamiento__cantidad'), V(0)))['t']
        consumida = calculo / 12
        try:
            consumida_gramos = consumida * obj.calorias
            calorias_mes = float(consumida_gramos) / numero_total_habitante
            calorias_dia = float(calorias_mes) / 30
            gramo_dia = float(obj.proteinas)
            if calorias_dia > 0:
                calorias_procesado[obj] = (consumida, obj.get_unidad_medida_display(),consumida_gramos,obj.calorias, obj.proteinas,calorias_dia,gramo_dia)
        except:
            pass
    total_calorias_procesado = sum(list([ i[5] for i in calorias_procesado.values()]))
    total_proteina_procesado = sum(list([ i[6] for i in calorias_procesado.values()]))

    calorias_fuera_finca = {}
    for obj in ProductosFueraFinca.objects.all():
        calculo = filtro.filter(alimentosfuerafinca__producto=obj).aggregate(t=Coalesce(Sum('alimentosfuerafinca__cantidad'), V(0)))['t']
        consumida = calculo / 12
        try:
            consumida_gramos = consumida * obj.calorias
            calorias_mes = float(consumida_gramos) / numero_total_habitante
            calorias_dia = float(calorias_mes) / 30
            gramo_dia = float(obj.proteinas)
            if calorias_dia > 0:
                calorias_fuera_finca[obj] = (consumida, obj.unidad_medida,consumida_gramos,obj.calorias, obj.proteinas,calorias_dia,gramo_dia)
        except:
            pass
    total_calorias_fuera_finca = sum(list([ i[5] for i in calorias_fuera_finca.values()]))
    total_proteina_fuera_finca = sum(list([ i[6] for i in calorias_fuera_finca.values()]))

    # datos = {'Kcal Cultivos Tradicional':total_calorias_tradicional,
    #         'Kcal Huertos de patio':total_calorias_huerto,
    #         'Kcal Frutas':total_calorias_fruta,
    #         'Kcal Productos procesados':total_calorias_procesado,
    #         'Kcal Productos comprados': total_calorias_fuera_finca}
    datos = [total_calorias_tradicional,
             total_calorias_huerto,
             total_calorias_fruta,
             total_calorias_procesado,
             total_calorias_fuera_finca]
    return datos

def calorias(request, template="indicadores/calorias.html"):
    filtro = _queryset_filtrado(request)
     #años de encuestas
    numero_total_habitante = filtro.aggregate(t=Sum('sexomiembros__cantidad'))['t']
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    dicc_calorias = OrderedDict()
    for year in years:
        filtro1 = filtro.filter(year=year[0]).count()
        calorias_tradicional = {}
        for obj in Cultivos.objects.all():
            calculo = filtro.filter(year=year[0],
                                    cultivostradicionales__cultivo=obj).aggregate(t=Coalesce(Avg('cultivostradicionales__consumo_familia'), V(0)))['t']
            consumida = calculo / 12
            consumida_gramos = consumida * obj.calorias
            calorias_mes = float(consumida_gramos) / numero_total_habitante
            calorias_dia = float(calorias_mes) / 30
            gramo_dia = float(obj.proteinas)
            if calorias_dia > 0:
                calorias_tradicional[obj] = (consumida, obj.get_unidad_medida_display(),consumida_gramos,obj.calorias, obj.proteinas,calorias_dia,gramo_dia)
        total_calorias_tradicional = sum(list([ i[5] for i in calorias_tradicional.values()]))
        total_proteina_tradicional = sum(list([ i[6] for i in calorias_tradicional.values()]))

        calorias_huerto = {}
        for obj in CultivosHuertos.objects.all():
            calculo = filtro.filter(year=year[0],
                                    cultivoshuertosfamiliares__cultivo=obj).aggregate(t=Coalesce(Avg('cultivoshuertosfamiliares__consumo_familia'), V(0)))['t']
            consumida = calculo / 12
            try:
                consumida_gramos = consumida * obj.calorias
            except:
                consumida_gramos = 0
            calorias_mes = float(consumida_gramos) / numero_total_habitante
            calorias_dia = float(consumida_gramos) / 30
            try:
                gramo_dia = float(obj.proteinas)
            except:
                pass
            if calorias_dia > 0:
                calorias_huerto[obj] = (consumida, obj.get_unidad_medida_display(),consumida_gramos,obj.calorias, obj.proteinas,calorias_dia,gramo_dia)

        total_calorias_huerto = sum(list([ i[5] for i in calorias_huerto.values()]))
        total_proteina_huerto = sum(list([ i[6] for i in calorias_huerto.values()]))

        calorias_fruta = {}
        for obj in CultivosFrutas.objects.all():
            calculo = filtro.filter(year=year[0],
                                    cultivosfrutasfinca__cultivo=obj).aggregate(t=Coalesce(Avg('cultivosfrutasfinca__consumo_familia'), V(0)))['t']
            consumida = calculo / 12
            consumida_gramos = consumida * obj.calorias
            calorias_mes = float(consumida_gramos) / numero_total_habitante
            calorias_dia = float(consumida_gramos) / 30
            gramo_dia = float(obj.proteinas)
            if calorias_dia > 0:
                calorias_fruta[obj] = (consumida, obj.get_unidad_medida_display(),consumida_gramos,obj.calorias, obj.proteinas,calorias_dia,gramo_dia)
        total_calorias_fruta = sum(list([ i[5] for i in calorias_fruta.values()]))
        total_proteina_fruta = sum(list([ i[6] for i in calorias_fruta.values()]))

        calorias_procesado = {}
        for obj in ProductoProcesado.objects.all():
            calculo = filtro.filter(year=year[0],
                                    procesamiento__producto=obj).aggregate(t=Coalesce(Avg('procesamiento__cantidad'), V(0)))['t']
            consumida = calculo / 12
            consumida_gramos = consumida * obj.calorias
            calorias_mes = float(consumida_gramos) / numero_total_habitante
            calorias_dia = float(consumida_gramos) / 30
            gramo_dia = float(obj.proteinas)
            if calorias_dia > 0:
                calorias_procesado[obj] = (consumida, obj.get_unidad_medida_display(),consumida_gramos,obj.calorias, obj.proteinas,calorias_dia,gramo_dia)

        total_calorias_procesado = sum(list([ i[5] for i in calorias_procesado.values()]))
        total_proteina_procesado = sum(list([ i[6] for i in calorias_procesado.values()]))

        calorias_fuera_finca = {}
        for obj in ProductosFueraFinca.objects.all():
            calculo = filtro.filter(year=year[0],
                                    alimentosfuerafinca__producto=obj).aggregate(t=Coalesce(Avg('alimentosfuerafinca__cantidad'), V(0)))['t']
            consumida = calculo / 12
            consumida_gramos = consumida * obj.calorias
            calorias_mes = float(consumida_gramos) / numero_total_habitante
            calorias_dia = float(consumida_gramos) / 30
            gramo_dia = float(obj.proteinas)
            if calorias_dia > 0:
                calorias_fuera_finca[obj] = (consumida, obj.unidad_medida,consumida_gramos,obj.calorias, obj.proteinas,calorias_dia,gramo_dia)

        total_calorias_fuera_finca = sum(list([ i[5] for i in calorias_fuera_finca.values()]))
        total_proteina_fuera_finca = sum(list([ i[6] for i in calorias_fuera_finca.values()]))

        dicc_calorias[year[1]] = (calorias_tradicional,
                                    total_calorias_tradicional,
                                    total_proteina_tradicional,
                                    calorias_huerto,
                                    total_calorias_huerto,
                                    total_proteina_huerto,
                                    calorias_fruta,
                                    total_calorias_fruta,
                                    total_proteina_fruta,
                                    calorias_procesado,
                                    total_calorias_procesado,
                                    total_proteina_procesado,
                                    calorias_fuera_finca,
                                    total_calorias_fuera_finca,
                                    total_proteina_fuera_finca,
                                    filtro1)

    return render(request, template, locals())

def productividad(request, template="indicadores/productividad.html"):
    filtro = _queryset_filtrado(request)
     #años de encuestas
    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    list(set(years))

    dicc_productividad = OrderedDict()
    for year in years:

        productividad_cultivo_tradicional_primera = {}
        for obj in Cultivos.objects.all():
            cultivo = filtro.filter(year=year[0],cultivostradicionales__cultivo=obj,cultivostradicionales__periodo=1)
            total_area_sembrada = cultivo.aggregate(t=Sum('cultivostradicionales__area_sembrada'))['t']
            total_area_cosechada = cultivo.aggregate(t=Sum('cultivostradicionales__area_cosechada'))['t']
            total_cosechada = cultivo.aggregate(t=Sum('cultivostradicionales__cantidad_cosechada'))['t']
            numero_gente_produce = cultivo.count()
            try:
                perdida = total_area_sembrada - total_area_cosechada
                productividad = total_cosechada / total_area_cosechada
            except:
                perdida = 0
                productividad = 0
            if numero_gente_produce > 0:
                productividad_cultivo_tradicional_primera[obj] = {'unidad':obj.get_unidad_medida_display(),
                                                'total_gente':numero_gente_produce,
                                                'total_area_cosechada':total_area_cosechada,
                                                'perdida':perdida,
                                                'total_produccion': total_cosechada,
                                                'productividad':productividad,
                                                }

        productividad_cultivo_tradicional_postrera = {}
        for obj in Cultivos.objects.all():
            cultivo = filtro.filter(year=year[0],cultivostradicionales__cultivo=obj,cultivostradicionales__periodo=2)
            total_area_sembrada = cultivo.aggregate(t=Sum('cultivostradicionales__area_sembrada'))['t']
            total_area_cosechada = cultivo.aggregate(t=Sum('cultivostradicionales__area_cosechada'))['t']
            total_cosechada = cultivo.aggregate(t=Sum('cultivostradicionales__cantidad_cosechada'))['t']
            numero_gente_produce = cultivo.count()
            try:
                perdida = total_area_sembrada - total_area_cosechada
                productividad = total_cosechada / total_area_cosechada
            except:
                perdida = 0
                productividad = 0
            if numero_gente_produce > 0:
                productividad_cultivo_tradicional_postrera[obj] = {'unidad':obj.get_unidad_medida_display(),
                                                'total_gente':numero_gente_produce,
                                                'total_area_cosechada':total_area_cosechada,
                                                'perdida':perdida,
                                                'total_produccion': total_cosechada,
                                                'productividad':productividad,
                                                }


        dicc_productividad[year[1]] = (productividad_cultivo_tradicional_primera,productividad_cultivo_tradicional_postrera)

    return render(request, template, {"dicc_productividad": dicc_productividad})

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

def save_as_xls(request):
    tabla = request.POST['tabla']
    response = render_to_response('xls.html', {'tabla': tabla, })
    response['Content-Disposition'] = 'attachment; filename=tabla.xls'
    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Charset'] ='UTF-8'
    return response


def traer_departamento(request):
    ids = request.GET.get('ids', '')
    if ids:
        lista = ids.split(',')
    results = []
    departamento = Departamento.objects.filter(pais__pk__in=lista, entrevistados__gt=1).distinct().values('id', 'nombre')
    return HttpResponse(simplejson.dumps(list(departamento)), content_type='application/json')

def traer_municipio(request):
    ids = request.GET.get('ids', '')
    dicc = {}
    resultado = []
    if ids:
        lista = ids.split(',')
        for id in lista:
			try:
				encuesta = Encuesta.objects.filter(entrevistado__municipio__departamento__id=id).distinct().values_list('entrevistado__municipio__id', flat=True)
				departamento = Departamento.objects.get(pk=id)
				municipios = Municipio.objects.filter(departamento__id=departamento.pk,id__in=encuesta).order_by('nombre')
				lista1 = []
				for municipio in municipios:
					muni = {}
					muni['id'] = municipio.pk
					muni['nombre'] = municipio.nombre
					lista1.append(muni)
					dicc[departamento.nombre] = lista1
			except:
				pass

	#filtrar segun la organizacion seleccionada
    org_ids = request.GET.get('org_ids', '')
    if org_ids:
		lista = org_ids.split(',')
		municipios = [encuesta.municipio for encuesta in Encuesta.objects.filter(organizacion__id__in=lista)]
		#crear los keys en el dicc para evitar KeyError
		for municipio in municipios:
			dicc[municipio.departamento.nombre] = []

		#agrupar municipios por departamento padre
		for municipio in municipios:
			muni = {'id': municipio.id, 'nombre': municipio.nombre}
			if not muni in dicc[municipio.departamento.nombre]:
				dicc[municipio.departamento.nombre].append(muni)

    resultado.append(dicc)

    return HttpResponse(simplejson.dumps(resultado), content_type='application/json')

def traer_organizacion(request):
    ids = request.GET.get('ids', '')
    if ids:
        lista = ids.split(',')
        organizaciones = OrganizacionResp.objects.filter(departamento__id__in = lista).order_by('nombre').values('id', 'nombre')
    return HttpResponse(simplejson.dumps(list(organizaciones)), content_type='application/json')

def traer_comunidad(request):
    ids = request.GET.get('ids', '')
    if ids:
        lista = ids.split(',')
        results = []
        comunies = Comunidad.objects.filter(municipio__pk__in=lista).order_by('nombre').values('id', 'nombre')
    return HttpResponse(simplejson.dumps(list(comunies)), content_type='application/json')
