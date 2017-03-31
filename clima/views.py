from django.shortcuts import render, get_object_or_404
from encuestas.models import *
from django.template.defaultfilters import slugify
from lugar.models import Pais
from django.db.models import Count, Sum, Avg, Value as V
from django.db.models.functions import Coalesce
from collections import OrderedDict

# Create your views here.
#programacion sobre las infografias


def info_consumo_kcal_pais(request, template='infografias/consumo_kcal_pais.html'):
    
    pais = get_object_or_404(Pais, slug=slugify(request.session['pais']))
    filtro_general = Encuesta.objects.filter(entrevistado__pais_id=pais.id)
    total_distinct = filtro_general.distinct('entrevistado__id')

    titulo = 'CONSUMO KCAL'
    pais = request.session['pais']
    total = total_distinct.count()
    hombres = float(total_distinct.filter(entrevistado__sexo=2,entrevistado__jefe=1).count()) / float(total) * 100
    mujeres = float(total_distinct.filter(entrevistado__sexo=1,entrevistado__jefe=1).count()) / float(total) * 100

    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    muchos_tiempo = list(sorted(set(years)))

    tiempo_kcalorias = OrderedDict()
    for anio in muchos_tiempo:
        tiempo_kcalorias[anio[1]] = [envio_calorias_pais(request, anio[0], 1), envio_calorias_pais(request, anio[0], 2)]


    return render(request, template, locals())


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

def infografia_ingreso_pais(request, template='infografias/info_ingresos_pais.html'):

    pais = get_object_or_404(Pais, slug=slugify(request.session['pais']))
    filtro_general = Encuesta.objects.filter(entrevistado__pais_id=pais.id)
    total_distinct = filtro_general.distinct('entrevistado__id')

    titulo = 'INGRESOS'
    pais = request.session['pais']
    total = total_distinct.count()
    hombres = float(total_distinct.filter(entrevistado__sexo=2,entrevistado__jefe=1).count()) / float(total) * 100
    mujeres = float(total_distinct.filter(entrevistado__sexo=1,entrevistado__jefe=1).count()) / float(total) * 100

    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    muchos_tiempo = list(sorted(set(years)))

    tiempo_ingresos = OrderedDict()
    for anio in muchos_tiempo:
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
            tradicional_verano = float(filtro_general.filter(year=anio[0],estacion=1).aggregate(t=Sum('cultivostradicionales__total'))['t'] / float(12)) / float(total)
            tradicional_invierno = float(filtro_general.filter(year=anio[0],estacion=2).aggregate(t=Sum('cultivostradicionales__total'))['t'] / float(12)) / float(total)
        except:
            pass

        try:
            huertos_verano = float(filtro_general.filter(year=anio[0],estacion=1).aggregate(t=Sum('cultivoshuertosfamiliares__total'))['t'] / float(12)) / float(total)
            huertos_invierno = float(filtro_general.filter(year=anio[0],estacion=2).aggregate(t=Sum('cultivoshuertosfamiliares__total'))['t'] / float(12)) / float(total)
        except:
            pass

        try:
            frutas_verano = float(filtro_general.filter(year=anio[0],estacion=1).aggregate(t=Sum('cultivosfrutasfinca__total'))['t'] / float(12) ) / float(total)
            frutas_invierno = float(filtro_general.filter(year=anio[0],estacion=2).aggregate(t=Sum('cultivosfrutasfinca__total'))['t'] / float(12) ) / float(total)
        except:
            pass

        try:
            fuente_verano = float(filtro_general.filter(year=anio[0],estacion=1).aggregate(t=Sum('fuentes__total'))['t'] / float(12)) / float(total)
            fuente_invierno = float(filtro_general.filter(year=anio[0],estacion=2).aggregate(t=Sum('fuentes__total'))['t'] / float(12)) / float(total)
        except:
            pass

        try:
            ganado_verano = float(filtro_general.filter(year=anio[0],estacion=1).aggregate(t=Sum('ganaderia__total'))['t'] / float(12)) / float(total)
            ganado_invierno = float(filtro_general.filter(year=anio[0],estacion=2).aggregate(t=Sum('ganaderia__total'))['t'] / float(12)) / float(total)
        except:
            pass

        try:
            procesamiento_verano = float(filtro_general.filter(year=anio[0],estacion=1).aggregate(t=Sum('procesamiento__total'))['t'] / float(12)) / float(total)
            procesamiento_invierno = float(filtro_general.filter(year=anio[0],estacion=2).aggregate(t=Sum('procesamiento__total'))['t'] / float(12)) / float(total)
        except:
            pass
        tiempo_ingresos[anio[1]] = [tradicional_verano,tradicional_invierno,huertos_verano,huertos_invierno,
                                    frutas_verano,frutas_invierno,fuente_verano,fuente_invierno,ganado_verano,
                                    ganado_invierno,procesamiento_verano,procesamiento_invierno]
    
 
    return render(request, template, locals())


def info_patron_gasto_pais(request, template='infografias/patron_gasto_pais.html'):
    
    pais = get_object_or_404(Pais, slug=slugify(request.session['pais']))
    filtro_general = Encuesta.objects.filter(entrevistado__pais_id=pais.id)
    total_distinct = filtro_general.distinct('entrevistado__id')

    titulo = 'PATRON DE GASTO'
    pais = request.session['pais']
    total = total_distinct.count()
    hombres = float(total_distinct.filter(entrevistado__sexo=2,entrevistado__jefe=1).count()) / float(total) * 100
    mujeres = float(total_distinct.filter(entrevistado__sexo=1,entrevistado__jefe=1).count()) / float(total) * 100

    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    muchos_tiempo = list(sorted(set(years)))

    tiempo_patron_gasto = OrderedDict()
    for anio in muchos_tiempo:
        gasto_finca_verano=0
        gasto_finca_invierno=0
        gasto_fuera_finca_verano=0
        gasto_fuera_finca_invierno=0
        try:
            gasto_finca_verano = float(filtro_general.filter(year=anio[0],estacion=1,gastohogar__tipo=5).aggregate(t=Sum('gastohogar__total'))['t'] / 12) / float(total)
            gasto_finca_invierno = float(filtro_general.filter(year=anio[0],estacion=2,gastohogar__tipo=5).aggregate(t=Sum('gastohogar__total'))['t'] / 12) / float(total)
        except:
            pass
        try:
            gasto_fuera_finca_verano = float(filtro_general.filter(year=anio[0],estacion=1).aggregate(t=Sum('gastoproduccion__total'))['t'] / 12) / float(total)
            gasto_fuera_finca_invierno = float(filtro_general.filter(year=anio[0],estacion=2).aggregate(t=Sum('gastoproduccion__total'))['t'] / 12) / float(total)
        except:
            pass
        tiempo_patron_gasto[anio[0]] = [gasto_finca_verano,gasto_finca_invierno,gasto_fuera_finca_verano,gasto_fuera_finca_invierno]


    return render(request, template, locals())

def info_rendimientos_pais(request, template='infografias/rendimientos_pais.html'):
    
    pais = get_object_or_404(Pais, slug=slugify(request.session['pais']))
    filtro_general = Encuesta.objects.filter(entrevistado__pais_id=pais.id)
    total_distinct = filtro_general.distinct('entrevistado__id')

    titulo = 'RENDIMIENTOS'
    pais = request.session['pais']
    total = total_distinct.count()
    hombres = float(total_distinct.filter(entrevistado__sexo=2,entrevistado__jefe=1).count()) / float(total) * 100
    mujeres = float(total_distinct.filter(entrevistado__sexo=1,entrevistado__jefe=1).count()) / float(total) * 100

    years = []
    for en in Encuesta.objects.order_by('year').values_list('year', flat=True):
        years.append((en,en))
    muchos_tiempo = list(sorted(set(years)))

    tiempo_rendimiento = OrderedDict()
    for anio in muchos_tiempo:
        #Calculo de los rendimientos o productividad del maiz y frijol primera
        total_area_cosechada_maiz_verano = filtro_general.filter(cultivostradicionales__cultivo=3,
                                    year=anio[0],estacion=1).aggregate(t=Sum('cultivostradicionales__area_cosechada'))['t']
        total_cosecha_maiz_verano = filtro_general.filter(cultivostradicionales__cultivo=3,
                                    year=anio[0],estacion=1).aggregate(t=Sum('cultivostradicionales__cantidad_cosechada'))['t']
        try:
            rendimiento_maiz_verano = total_cosecha_maiz_verano / total_area_cosechada_maiz_verano
        except:
            rendimiento_maiz_verano = 0

        total_area_cosechada_frijol_verano = filtro_general.filter(cultivostradicionales__cultivo=2,
                                            year=anio[0],estacion=1).aggregate(t=Sum('cultivostradicionales__area_cosechada'))['t']
        total_cosecha_frijol_verano = filtro_general.filter(cultivostradicionales__cultivo=2,
                                            year=anio[0],estacion=1).aggregate(t=Sum('cultivostradicionales__cantidad_cosechada'))['t']
        try:
            rendimiento_frijol_verano = total_cosecha_frijol_verano / total_area_cosechada_frijol_verano
        except:
            rendimiento_frijol_verano = 0

        #calculo de los rendimiento invierno
        total_area_cosechada_maiz_invierno = filtro_general.filter(cultivostradicionales__cultivo=3,
                                    year=anio[0],estacion=2).aggregate(t=Sum('cultivostradicionales__area_cosechada'))['t'] or 0
        total_cosecha_maiz_invierno = filtro_general.filter(cultivostradicionales__cultivo=3,
                                    year=anio[0],estacion=2).aggregate(t=Sum('cultivostradicionales__cantidad_cosechada'))['t'] or 0
        try:
            rendimiento_maiz_invierno = total_cosecha_maiz_invierno / total_area_cosechada_maiz_invierno
        except:
            rendimiento_maiz_invierno = 0

        total_area_cosechada_frijol_invierno = filtro_general.filter(cultivostradicionales__cultivo=2,
                                            year=anio[0],estacion=2).aggregate(t=Sum('cultivostradicionales__area_cosechada'))['t'] or 0
        total_cosecha_frijol_invierno = filtro_general.filter(cultivostradicionales__cultivo=2,
                                            year=anio[0],estacion=2).aggregate(t=Sum('cultivostradicionales__cantidad_cosechada'))['t'] or 0
        try:
            rendimiento_frijol_invierno = total_cosecha_frijol_invierno / total_area_cosechada_frijol_invierno
        except:
            rendimiento_frijol_invierno = 0
        tiempo_rendimiento[anio[1]] = (rendimiento_maiz_verano,
                                       rendimiento_maiz_invierno,
                                       rendimiento_frijol_verano,
                                       rendimiento_frijol_invierno)
        
    return render(request, template, locals())