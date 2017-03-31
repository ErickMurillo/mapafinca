from django import template
import locale
register = template.Library()

@register.filter(name='calculaperct')
def calculaperct(value1, value2):
    try:
        resultado = (float(value1) / float(value2) * 100)
        return resultado
    except:
        return 0

@register.filter(name='calculaUtilidad')
def calculaUtilidad(value1, value2):
    try:
        resultado = float(value1) - float(value2)
        return resultado
    except:
        return 0

@register.filter(name='calculaSumatoriaIngreso')
def calculaSumatoriaIngreso(value1):
    try:
        resultado += float(value1)
        return resultado
    except:
        return 0

@register.filter(name='calcularIngresoXfamilia')
def calcularIngresoXfamilia(value1, value2):
    try:
        resultado = float(value1) / float(value2)
        return resultado
    except:
        return 0


@register.filter(name='limpiarSlug')
def limpiarSlug(value):
    return value.replace('_', ' ')

@register.filter
def running_total(your_list):
    print "la suma"
    
    print your_list
    return sum(d for d in your_list)

@register.filter(name='calculaperct2')
def calculaperct2(value1, listas):
    value2 = sum(d for d in listas)
    try:
        resultado = (float(value1) / float(value2) * 100)
        return resultado
    except:
        return 0

@register.simple_tag
def calculaperct3(value1, value2, *args, **kwargs):
    suma = float(value1) + float(value2)
    try:
        resultado = (float(value1) / float(suma) * 100)
        return round(resultado,2)
    except:
        return 0

@register.simple_tag
def calculaperct4(value1, value2, *args, **kwargs):
    suma = float(value1) + float(value2) + float(kwargs['v4']) + float(kwargs['v6']) \
            + float(kwargs['v8']) + float(kwargs['v10'])
    try:
        resultado = (float(value1) / float(suma) * 100)
        return round(resultado,2)
    except:
        return 0