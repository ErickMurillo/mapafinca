# -*- coding: utf-8 -*-
from django.db import models
from lugar.models import Pais, Departamento, Municipio, Comunidad
from multiselectfield import MultiSelectField
# Create your models here.
#CHOICES ESTATICOS
CHOICE_SEXO = (
                (1, 'Mujer'),
                (2, 'Hombre'),
              )
CHOICE_JEFE = (
                (1, 'Si'),
                (2, 'No'),
              )
CHOICE_DUENO_SI = (
                (1, 'A nombre del hombre'),
                (2, 'A nombre de la mujer'),
                (3, 'A nombre de los hijos'),
                (4, 'Mancomunado'),
              )
CHOICE_DUENO_NO = (
                (1, 'Arrendada'),
                (2, 'Promesa de venta'),
                (3, 'Prestada'),
                (4, 'Tierra Indígena'),
                (5, 'Sin escritura'),
                (6, 'Colectivo/Cooperativa'),
              )
CHOICE_EDAD = (
                (1, 'Hombres > 31 años'),
                (2, 'Mujeres > 31 años'),
                (3, 'Ancianos > 64 años'),
                (4, 'Ancianas > 64 años'),
                (5, 'Mujer joven de 19 a 30 años'),
                (6, 'Hombre joven de 19 a 30 años'),
                (7, 'Mujer adolescente 13 a 18 años'),
                (8, 'Hombre adolescente 13 a 18 años'),
                (9, 'Niñas 5 a 12 años'),
                (10, 'Niños 5 a 12 años '),
                (11, 'Niñas 0 a 4 años '),
                (12, 'Niños 0 a 4 años'),
              )
CHOICE_ESCOLARIDAD = (
                (1, 'Hombres mayores 31 años'),
                (2, 'Mujeres mayores 31 años'),
                (3, 'Hombre joven de 19 a 30 años'),
                (4, 'Mujer joven de 19 a 30 años'),
                (5, 'Hombre adolescente 13 a 18 años'),
                (6, 'Mujer adolescente 13 a 18 años'),
                (7, 'Niños 5 a 12 años'),
                (8, 'Niñas 5 a 12 años '),
              )
# FIN DE CHOICES ESTATICOS


class Encuestadores(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Encuestador'
        verbose_name_plural = 'Encuestadores'


class OrganizacionResp(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Organización responsable'
        verbose_name_plural = 'Organizaciones responsables'


class Entrevistados(models.Model):
    nombre = models.CharField('Nombre Completo', max_length=250)
    cedula = models.CharField('No. Cédula', max_length=50)
    ocupacion = models.CharField('Ocupación', max_length=150)
    sexo = models.IntegerField(choices=CHOICE_SEXO)
    jefe = models.IntegerField(choices=CHOICE_JEFE, verbose_name='Jefe del hogar')
    edad = models.IntegerField()
    latitud = models.FloatField(blank=True)
    longitud = models.FloatField(blank=True)
    pais = models.ForeignKey(Pais)
    departamento = models.ForeignKey(Departamento)
    municipio = models.ForeignKey(Municipio)
    comunidad = models.ForeignKey(Comunidad)
    finca = models.CharField('Nombre de la finca', max_length=250)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Entrevistado'
        verbose_name_plural = 'Entrevistados'


class Encuesta(models.Model):
    entrevistado = models.ForeignKey(Entrevistados)
    fecha = models.DateField()
    dueno = models.IntegerField(choices=CHOICE_JEFE,
                    verbose_name='¿Son dueños de la propiedad/finca?')

    year = models.IntegerField(editable=False)

    def save(self):
        self.year = self.fecha.year
        super(Encuesta, self).save()

    def __unicode__(self):
        return u'%s' % (self.entrevistado.nombre)


class DuenoSi(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    si = models.IntegerField(choices=CHOICE_DUENO_SI)

    def __unicode__(self):
        return u'%s' % (self.get_si_display())

    class Meta:
        verbose_name_plural = '6.1_En el caso SI, indique a nombre de quien está'


class DuenoNo(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    no = models.IntegerField(choices=CHOICE_DUENO_NO)

    def __unicode__(self):
        return u'%s' % (self.get_si_display())

    class Meta:
        verbose_name_plural = '6.2_En el caso que diga NO, especifique la situación'


class SexoMiembros(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    sexo = models.IntegerField(choices=CHOICE_SEXO,
                verbose_name='7_Sexo del jefe (a) del hogar')
    cantidad = models.IntegerField('8_Cantidad de personas que habitan en el hogar')

    def __unicode__(self):
        return u'%s' % (self.get_sexo_display())

    class Meta:
        verbose_name_plural = 'Sexo del jefe del hogar y cantidad de miembros'


class DetalleMiembros(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    edad = models.IntegerField(choices=CHOICE_EDAD)
    cantidad = models.IntegerField()

    def __unicode__(self):
        return u'%s' % (self.get_sexo_display())

    class Meta:
        verbose_name_plural = '9_Detalle la cantidad de miembros del hogar según edad y sexo'


class Escolaridad(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    sexo = models.IntegerField(choices=CHOICE_ESCOLARIDAD)
    no_leer = models.IntegerField('No lee,ni escribe')
    pri_incompleta = models.IntegerField('Primaria incompleta')
    pri_completa = models.IntegerField('Primaria completa')
    secu_incompleta = models.IntegerField('Secundaria incompleta')
    secu_completa = models.IntegerField('Secundaria completa')
    bachiller = models.IntegerField('Bachiller')
    uni_tecnico = models.IntegerField('Universitario o técnico')
    total = models.IntegerField('total')

    def __unicode__(self):
        return u'%s' % (self.get_sexo_display())

    class Meta:
        verbose_name_plural = '10_Nivel de escolaridad (número por categoría)'


class Energia(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Energia'
        verbose_name_plural = 'Energias'


class TipoEnergia(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    tipo = models.ManyToManyField(Energia)

    class Meta:
        verbose_name_plural = '11_¿Qué tipo de energía utiliza para alumbrar la vivienda?'

CHOICE_PANEL_SOLAR = (
                (1, 'Doméstico'),
                (2, 'Agrícola'),
                (3, 'Negocio'),
              )


class PanelSolar(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    panel = models.IntegerField(choices=CHOICE_PANEL_SOLAR)

    class Meta:
        verbose_name_plural = '11.1_En el caso que tenga panel solar, cuál es el fin'


class FuenteEnergia(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Fuente de Energia'
        verbose_name_plural = 'Fuentes de Energias'


class EnergiaSolarCocinar(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    fuente = models.ManyToManyField(FuenteEnergia)

    class Meta:
        verbose_name_plural = '12_Mencione el tipo de fuente de energía utiliza para cocinar'


class Cocinas(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo Cocina'
        verbose_name_plural = 'Tipos de cocinas'


class TipoCocinas(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    cocina = models.ManyToManyField(Cocinas)

    class Meta:
        verbose_name_plural = '13_Mencione el tipo de cocina que utiliza para cocinar'

class AguaConsumo(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Agua para consumo'
        verbose_name_plural = 'Agua para consumo'


class AccesoAgua(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    agua = models.ManyToManyField(AguaConsumo)

    class Meta:
        verbose_name_plural = '14_Indique la forma que accede al agua para consumo humano'


CHOICE_DISPONIBILIDAD = (
                (1, 'Todo los días y toda hora'),
                (2, 'Cada dos días y algunas horas'),
                (3, 'Algunos días y algunas horas'),
                (4, 'No confiable')
              )


class DisponibilidadAgua(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    disponibilidad = models.IntegerField(choices=CHOICE_DISPONIBILIDAD)

    class Meta:
        verbose_name_plural = '15_Mencione la disponibilidad del agua para consumo humano (en verano)'


CHOICE_CALIDAD_AGUA = (
                (1, 'De buena calidad'),
                (2, 'De regular calidad'),
                (3, 'Contaminada'),
                (4, 'No sabe')
              )


class CalidadAgua(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    calidad = models.IntegerField(choices=CHOICE_CALIDAD_AGUA)

    class Meta:
        verbose_name_plural = '16_Según Usted, cómo es la calidad del agua que consume'


class TipoContamindaAgua(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo agua contaminada'
        verbose_name_plural = 'Tipo agua contaminada'


class Contaminada(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    contaminada = models.ForeignKey(TipoContamindaAgua)

    class Meta:
        verbose_name_plural = '16.1_En caso de que esté contaminada, señala posibles causas'


class Evidencia(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    cual = models.CharField('¿Cuál?', max_length=250)

    class Meta:
        verbose_name_plural = '16.2_Existe alguna evidencia'


CHOICE_TRATAMIENTO = (
                (1, 'Se hierve'),
                (2, 'Se clora'),
                (3, 'Se usa filtro'),
                (4, 'Se deja reposar'),
                (5, 'Ninguno')
              )

CHOICE_OTRO_USO = (
                (1, 'Uso doméstico'),
                (2, 'Uso agrícola'),
                (3, 'Uso turístico'),
                (4, 'Crianza de peces'),
                (5, 'Para ganado')
              )


class TratamientoAgua(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    tratamiento = models.IntegerField(choices=CHOICE_TRATAMIENTO)

    class Meta:
        verbose_name_plural = '17_Realiza algún tratamiento al agua de consumo'


class UsosAgua(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    uso = models.IntegerField(choices=CHOICE_OTRO_USO)

    class Meta:
        verbose_name_plural = '18_Indique qué otros usos le dan al agua en la finca'


class OrgComunitarias(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre


class BeneficiosOrganizados(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

class OrganizacionComunitaria(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    pertenece = models.IntegerField(choices=CHOICE_JEFE, verbose_name='19_¿Pertenece a alguna organización?')
    caso_si = models.ManyToManyField(OrgComunitarias, verbose_name='19_1 qué organización comunitaria pertenece?')
    cuales_beneficios = models.ManyToManyField(BeneficiosOrganizados, verbose_name='19_2 ¿Cuales son los beneficios de estar organizado?')


class OrganizacionFinca(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    area_finca = models.FloatField('20_¿Cuál es el área total en manzana de la finca?')

CHOICE_TIERRA = (
        (1,'Bosque'),
        (2,'Tacotal'),
        (3,'Cultivo anual'),
        (4,'Plantación forestal'),
        (5,'Potrero'),
        (6,'Pasto en asocio con árboles'),
        (7,'Frutales'),
        (8,'Cultivos en asocio'),

    )
class DistribucionTierra(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    tierra = models.IntegerField(choices=CHOICE_TIERRA, verbose_name='20.1_Distribución de la tierra en la finca')
    manzanas = models.FloatField()


class PercibeIngreso(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    si_no = models.IntegerField(choices=CHOICE_JEFE)


CHOICE_TIPO_FUENTE = ((1,'Asalariado'),
                      (2,'Jornalero'),
                      (3,'Alquiler'),
                      (4,'Negocio propio'),
                      (5,'Remesas'),
                      (6,'Otros'),
                    )

class TipoFuenteIngreso(models.Model):
    tipo = models.IntegerField(choices=CHOICE_TIPO_FUENTE)
    nombre = models.CharField('especifique tipo', max_length=250)

    def __unicode__(self):
        return self.nombre


class Fuentes(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    fuente_ingreso = models.ForeignKey(TipoFuenteIngreso)
    cantidad = models.FloatField('Cantidad mensual C$')
    cantidad_veces = models.FloatField('Cantidad de veces en el año')
    hombres = models.IntegerField('Cantidad de miembros hombres')
    mujeres = models.IntegerField('Cantidad de miembros mujeres')

    class Meta:
        verbose_name_plural = '21_ingresos diferentes a la actividad agropecuaria'


CHOICE_MEDIDA = (
                (1, 'Quintal'),
                (2, 'Libras'),
                (3, 'Docena'),
                (4, 'Cien'),
                (5, 'Cabeza'),
                )

CHOICE_PERIODO = (
                (1, 'Primera'),
                (2, 'Postrera'),
                )


class Cultivos(models.Model):
    codigo = models.CharField(max_length=4)
    nombre = models.CharField(max_length=250)
    unidad_medida = models.IntegerField(choices=CHOICE_MEDIDA)

    def __unicode__(self):
        return u'%s-%s' % (self.codigo, self.nombre)

class TipoMercado(models.Model):
    codigo = models.CharField(max_length=4)
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return u'%s-%s' % (self.codigo, self.nombre)

class CultivosTradicionales(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    cultivo = models.ForeignKey(Cultivos)
    area_sembrada = models.FloatField('Area sembrada (Mz)')
    area_cosechada = models.FloatField('Area cosechada (Mz)')
    cantidad_cosechada = models.FloatField()
    consumo_familia = models.FloatField('Consumo de la familia')
    consumo_animal = models.FloatField()
    procesamiento = models.FloatField()
    venta = models.FloatField()
    precio = models.FloatField('Precio de venta en C$')
    costo = models.FloatField('Costo por Mz en C$')
    mercado = models.ForeignKey(TipoMercado)
    periodo = models.IntegerField(choices=CHOICE_PERIODO)

    class Meta:
        verbose_name_plural = '22_Cultivos tradicionales  producidos en la finca'

#cultivos de huertos familiares

class CultivosHuertos(models.Model):
    codigo = models.CharField(max_length=4)
    nombre = models.CharField(max_length=250)
    unidad_medida = models.IntegerField(choices=CHOICE_MEDIDA)

    def __unicode__(self):
        return u'%s-%s' % (self.codigo, self.nombre)


class CultivosHuertosFamiliares(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    cultivo = models.ForeignKey(CultivosHuertos)
    cantidad_cosechada = models.FloatField()
    consumo_familia = models.FloatField('Consumo de la familia')
    consumo_animal = models.FloatField()
    procesamiento = models.FloatField()
    venta = models.FloatField()
    precio = models.FloatField('Precio de venta en C$')
    costo = models.FloatField('Costo por Mz en C$')
    mercado = models.ForeignKey(TipoMercado)

    class Meta:
        verbose_name_plural = '23_Cultivos de huertos familiares en la finca'

#24 ganaderia mayor y menor otros en la finca

class Animales(models.Model):
    codigo = models.CharField(max_length=4)
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return u'%s-%s' % (self.codigo, self.nombre)

class Ganaderia(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    animal = models.ForeignKey(Animales)
    cantidad = models.IntegerField('Cantidad de animales')
    si_no = models.IntegerField(choices=CHOICE_JEFE)
    cantidad_vendida = models.IntegerField('Cantidad vendida este año')
    precio = models.FloatField('Precio de venta en C$')
    mercado = models.ForeignKey(TipoMercado)

    class Meta:
        verbose_name_plural = '24_1 Inventario de ganaderia mayor y menor'

#procesamiento

class ProductoProcesado(models.Model):
    nombre = models.CharField(max_length=250)
    unidad_medida = models.IntegerField(choices=CHOICE_MEDIDA)

    def __unicode__(self):
        return u'%s-%s' % (self.codigo, self.nombre)


class Procesamiento(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    producto = models.ForeignKey(ProductoProcesado)
    cantidad = models.IntegerField('Cantidad')
    cantidad_vendida = models.IntegerField('Cantidad vendida este año')
    precio = models.FloatField('Precio de venta en C$')
    mercado = models.ForeignKey(TipoMercado)

    class Meta:
        verbose_name_plural = '24_2 Procesamiento de la producción'

#25  de la lista de los  productos  indicar cuales fueron introducidos/providos por 
#el programa medios de vida sostenible

class IntroducidosTradicionales(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    cultivo = models.ForeignKey(Cultivos)
    si_no = models.IntegerField(choices=CHOICE_JEFE)
    anio = models.IntegerField('Año')

    class Meta:
        verbose_name_plural = 'Productos introducidos/promovidos tradicionales'


class IntroducidosHuertos(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    cultivo = models.ForeignKey(Cultivos)
    si_no = models.IntegerField(choices=CHOICE_JEFE)
    anio = models.IntegerField('Año')

    class Meta:
        verbose_name_plural = 'Productos introducidos/promovidos huertos familiares'

#Gastos en el hogar

CHOICE_TIPO_GASTOS = (
                        (1,'Salud'),
                        (2,'Educación'),
                        (3,'Alquiler de vivienda'),
                        (4,'Ropa'),
                        (5,'Alimentación'),
                        (6,'Recreación/Diversión'),
                    )

class GastoHogar(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    tipo = models.IntegerField(choices=CHOICE_TIPO_GASTOS)
    cantidad = models.FloatField('Cantidad mensual en C$')
    cantidad_veces = models.FloatField('Cantidad de veces en el año')

    class Meta:
        verbose_name_plural = 'Gastos generales del hogar'

class TipoGasto(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

class GastoProduccion(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    tipo = models.ForeignKey(TipoGasto)
    cantidad = models.FloatField('Cantidad mensual en C$')
    cantidad_veces = models.FloatField('Cantidad de veces en el año')

    class Meta:
        verbose_name_plural = 'Gastos generales para la producción'


class RecibePrestamo(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

class UsoPrestamo(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

class Prestamo(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    algun_prestamo = models.IntegerField(choices=CHOICE_JEFE)
    monto = models.FloatField('28.1_¿Cuál fue el monto en C$?')
    pago = models.FloatField('28.2_¿Pago mensual en C$?')
    recibe = models.ManyToManyField(RecibePrestamo, 
                                    verbose_name='28.3_¿De quien recibe el prestamo/crédito')
    uso = models.ManyToManyField(UsoPrestamo, 
                                verbose_name='28.4_¿Cuál fue el uso del prestamo/crédito')


    class Meta:
        verbose_name_plural = '28_En el ultimo año ha recibido algún tipo de prestamo/crédito'

# Prácticas agroecologicas

class Practicas(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

CHOICE_MANEJO = (
                    (1,'Tala y quema'),
                    (2,'Trabaja en crudo'),
                    (3,'Arado'),
                    (4,'Uso de cobertura'),
    )

CHOICE_TRACCION = (
                    (1,'Animal'),
                    (2,'Humana'),
                    (3,'Tractor'),
                    (4,'Ninguna'),
    )

class PracticasAgroecologicas(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    si_no = models.IntegerField(choices=CHOICE_JEFE, 
        verbose_name='29_¿En la finca aplican técnicas de manejo agro ecologico u orgánico')
    cinco_principales = models.ManyToManyField(Practicas, 
                                            verbose_name='29.1_Mencione cinco principales')
    manejo = models.IntegerField(choices=CHOICE_MANEJO)
    traccion = models.IntegerField(choices=CHOICE_TRACCION)
    fertilidad = models.IntegerField(choices=CHOICE_JEFE)
    control = models.IntegerField(choices=CHOICE_JEFE)

    class Meta:
        verbose_name_plural = 'Prácticas agroecológicas'

CHOICE_PORCENTAJE = (
                        (1,'10%'),
                        (2,'20%'),
                        (3,'30%'),
                        (4,'40%'),
                        (5,'50%'),
                        (6,'60%'),
                        (7,'70%'),
                        (8,'80%'),
                        (9,'90%'),
                        (10,'100%'),
                    )

#seguridad alimentaria

class TipoSecado(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre


class SeguridadAlimentaria(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    misma_finca = models.IntegerField(choices=CHOICE_PORCENTAJE, 
        verbose_name='35.1_¿Qué porcentaje alimentos que consumen en su hogar provienen de la misma finca?')
    fuera_finca = models.IntegerField(choices=CHOICE_PORCENTAJE, 
        verbose_name='35.2_¿Qué porcentaje alimentos que consumen en su hogar provienen fuera de la finca?')
    economico = models.IntegerField(choices=CHOICE_JEFE, 
        verbose_name='36_¿Disponen suficiente recursos económicos para manejo de finca?')
    secado = models.IntegerField(choices=CHOICE_JEFE, 
        verbose_name='37_¿Dispone de tecnología para el secado y almacenamiento de cosecha?')
    tipo_secado = models.ForeignKey(TipoSecado, verbose_name='Si es si cuál?')
    plan_cosecha = models.IntegerField(choices=CHOICE_JEFE, 
        verbose_name='38_¿Cuentan con un plan de cosecha?')
    ayuda = models.IntegerField(choices=CHOICE_JEFE, 
        verbose_name='39_¿Cuentan con ayuda de alimentos en momentos de escasez?')
    suficiente_alimento = models.IntegerField(choices=CHOICE_JEFE, 
        verbose_name='40_¿Le ha preocupado que en su hogar no hubiera suficiente alimentos?')
    consumo_diario = models.IntegerField(choices=CHOICE_JEFE, 
        verbose_name='41_¿Considera que su familia cuenta con la cantidad necesaria de alimentos que necesitan para el consumo diario del hogar?')

    class Meta:
        verbose_name_plural = 'VI. Seguridad alimentaria'

CHOICE_FENOMENOS = (
            (1,'Sequía'),
            (2,'Inundación'),
            (3,'Deslizamiento'),
            (4,'Viento'),
        )
CHOICE_AGRICOLA = (
            (1,'Falta de semilla'),
            (2,'Mala calidad de la semilla'),
        )
CHOICE_MERCADO = (
            (1,'Bajo precio'),
            (2,'Falta de venta'),
            (3,'Mala calidad del producto'),
        )
CHOICE_INVERSION = (
            (1,'Falta de crédito'),
            (2,'Alto interés'),
        )

class RespuestaNo41(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    fenomeno = MultiSelectField(CHOICE_FENOMENOS)
    fenomeno = MultiSelectField(CHOICE_AGRICOLA)
    fenomeno = MultiSelectField(CHOICE_MERCADO)
    fenomeno = MultiSelectField(CHOICE_INVERSION)

    class Meta:
        verbose_name_plural = '41.1_Si responde NO, marque con una X las principales razones'

class AdquiereAgua(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

class TratamientoAgua(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

class OtrasSeguridad(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    adquiere_agua = models.ForeignKey(AdquiereAgua, 
                    verbose_name='42_En momentos de sequía como adquiere el agua de consumo')
    tratamiento = models.IntegerField(choices=CHOICE_JEFE, 
                    verbose_name='42_1 Le da algún tipo de tratamiento:')
    tipo_tratamiento = models.ForeignKey(TratamientoAgua)

    class Meta:
        verbose_name_plural = 'Pregunta 42'

#VII. Consumo de alimentos

class ProductosFueraFinca(models.Model):
    nombre = models.CharField(max_length=250)
    unidad_medida = models.CharField(max_length=150)

    def __unicode__(self):
        return self.nombre

class AlimentosFueraFinca(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    producto = models.ForeignKey(ProductosFueraFinca)
    cantidad = models.FloatField('Cantidad mensual')
    precio = models.FloatField('Precio en C$')

    class Meta:
        verbose_name_plural = '43_Indique los alimentos que compra fuera de la finca'
