# -*- coding: utf-8 -*-
from django.db import models
from lugar.models import Pais, Departamento, Municipio, Comunidad, Microcuenca
from multiselectfield import MultiSelectField
from sorl.thumbnail import ImageField
from smart_selects.db_fields import ChainedForeignKey
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
#CHOICES ESTATICOS
CHOICE_SEXO = (
                (1, 'Mujer'),
                (2, 'Hombre'),
                (3, 'Ambos'),
              )
CHOICE_SEXO1 = (
                (1, 'Mujer'),
                (2, 'Hombre'),
                (3, 'Ambos'),
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
                (4, 'Tierra Indígena/Comunal'),
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
    pais = models.ForeignKey(Pais, null=True)
    departamento = ChainedForeignKey(
        Departamento,
        chained_field="pais",
        chained_model_field="pais",
        show_all=False,
        auto_choose=True,
        null=True
    )
    municipio = ChainedForeignKey(
        Municipio,
        chained_field="departamento",
        chained_model_field="departamento",
        show_all=False,
        auto_choose=True,
        null=True
    )

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Organización responsable'
        verbose_name_plural = 'Organizaciones responsables'


class Entrevistados(models.Model):
    nombre = models.CharField('Nombre Completo', max_length=250)
    cedula = models.CharField('No. Cédula/DPI', max_length=50, null=True, blank=True)
    ocupacion = models.CharField('Ocupación', max_length=150)
    sexo = models.IntegerField(choices=CHOICE_SEXO)
    jefe = models.IntegerField(choices=CHOICE_JEFE, verbose_name='Jefe del hogar')
    edad = models.IntegerField()
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null= True, blank=True)
    pais = models.ForeignKey(Pais)
    departamento = ChainedForeignKey(
        Departamento,
        chained_field="pais",
        chained_model_field="pais",
        show_all=False,
        auto_choose=True
    )
    municipio = ChainedForeignKey(
        Municipio,
        chained_field="departamento",
        chained_model_field="departamento",
        show_all=False,
        auto_choose=True
    )
    comunidad = ChainedForeignKey(
        Comunidad,
        chained_field="municipio",
        chained_model_field="municipio",
        show_all=False,
        auto_choose=True,
        null=True,
        blank=True,
    )
    microcuenca = ChainedForeignKey(
        Microcuenca,
        chained_field="comunidad",
        chained_model_field="comunidad",
        show_all=False,
        auto_choose=True,
        null=True,
        blank=True,
    )
    finca = models.CharField('Nombre de la finca', max_length=250)

    user = models.ForeignKey(User)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Base de datos Productor'
        verbose_name_plural = 'Base de datos Productores'

CHOICES_ESTACIONES = ((1, 'Verano'),(2, 'Invierno'),)

class Encuesta(models.Model):
    entrevistado = models.ForeignKey(Entrevistados)
    fecha = models.DateField()
    estacion = models.IntegerField(choices=CHOICES_ESTACIONES, default='1')
    encuestador = models.ForeignKey(Encuestadores)
    mapa_finca = ImageField(upload_to='mapas_fincas', null=True, blank=True)
    dueno = models.IntegerField(choices=CHOICE_JEFE,
                    verbose_name='¿Son dueños de la propiedad/finca?')
    org_responsable = models.ForeignKey(OrganizacionResp, verbose_name='Nombre de la organización responsable')

    year = models.IntegerField(editable=False, verbose_name='Año')

    user = models.ForeignKey(User)

    def save(self):
        self.year = self.fecha.year
        super(Encuesta, self).save()

    def __unicode__(self):
        return u'%s' % (self.entrevistado.nombre)

    class Meta:
        verbose_name_plural = 'ENCUESTAS'


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
        return u'%s' % (self.get_no_display())

    class Meta:
        verbose_name_plural = '6.2_En el caso que diga NO, especifique la situación'


class SexoMiembros(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    sexo = models.IntegerField(choices=CHOICE_SEXO,
                verbose_name='7_Quien es el jefe (a) del hogar')
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
        return u'%s' % (self.get_edad_display())

    class Meta:
        verbose_name_plural = '9_Detalle la cantidad de miembros del hogar según edad y sexo'


class Escolaridad(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    sexo = models.IntegerField(choices=CHOICE_ESCOLARIDAD)
    no_leer = models.IntegerField('No lee,ni escribe')
    pri_incompleta = models.IntegerField('Primaria incompleta')
    pri_completa = models.IntegerField('Primaria completa')
    secu_incompleta = models.IntegerField('Secundaria incompleta')
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
    si_no = models.IntegerField(choices=CHOICE_JEFE, null=True, blank=True)

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
                (5, 'Sodificación'),
                (6, 'Ninguno')
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
    caso_si = models.ManyToManyField(OrgComunitarias, verbose_name='19_1 qué organización comunitaria pertenece?',
                                    blank=True)
    cuales_beneficios = models.ManyToManyField(BeneficiosOrganizados,
                                        verbose_name='19_2 ¿Cuales son los beneficios de estar organizado?',
                                        blank=True)

class OrganizacionFinca(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    area_finca = models.FloatField('20_¿Cuál es el área total en manzana de la finca?')

CHOICE_TIERRA = (
        (1,'Bosque'),
        (2,'Tacotal/Guamil/Machorra/Llano'),
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
    si_no = models.IntegerField(choices=CHOICE_JEFE, verbose_name='Opciones')

    class Meta:
        verbose_name_plural = '21_¿La familia percibe otros ingresos diferentes a la actividad agropecuaria?'


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
        return u'%s - %s ' % (self.get_tipo_display(), self.nombre)


class Fuentes(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    fuente_ingreso = models.ForeignKey(TipoFuenteIngreso)
    cantidad = models.FloatField('Cantidad mensual C$')
    cantidad_veces = models.FloatField('Cantidad de veces en el año')
    hombres = models.IntegerField('Cantidad de miembros hombres')
    mujeres = models.IntegerField('Cantidad de miembros mujeres')

    total = models.FloatField(editable=False)

    def save(self, *args, **kwargs):
        '''Save sobrecargado para calcular totales'''

        self.total = self.cantidad * self.cantidad_veces
        super(Fuentes, self).save(*args, **kwargs)

        models.signals.post_save.send(sender=Encuesta, instance=self.encuesta)

    class Meta:
        verbose_name_plural = '21.1_ingresos diferentes a la actividad agropecuaria'


CHOICE_MEDIDA = (
                (1, 'Quintal'),
                (2, 'Libras'),
                (3, 'Docena'),
                (4, 'Cien'),
                (5, 'Cabeza'),
                (6, 'Litro'),
                (7, 'Unidad'),
                )

CHOICE_PERIODO = (
                (1, 'Primera'),
                (2, 'Postrera'),
                )

CHOICE_INICIATIVAS = (
                (1, 'Si'),
                (2, 'No'),
                )


class Cultivos(models.Model):
    codigo = models.CharField(max_length=4)
    nombre = models.CharField(max_length=250)
    unidad_medida = models.IntegerField(choices=CHOICE_MEDIDA)
    calorias = models.FloatField(null=True, blank=True)
    proteinas = models.FloatField(null=True, blank=True)


    def __unicode__(self):
        return u'%s - %s - %s' % (self.codigo, self.nombre, self.get_unidad_medida_display())

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
    iniciativas = models.IntegerField(choices=CHOICE_INICIATIVAS, null=True, blank=True)

    total = models.FloatField(editable=False)

    def save(self, *args, **kwargs):
        '''Save sobrecargado para calcular totales'''

        self.total = self.venta * self.precio
        super(CultivosTradicionales, self).save(*args, **kwargs)

        models.signals.post_save.send(sender=Encuesta, instance=self.encuesta)

    class Meta:
        verbose_name_plural = '22_Cultivos tradicionales  producidos en la finca'

#cultivos de huertos familiares

class CultivosHuertos(models.Model):
    codigo = models.CharField(max_length=4)
    nombre = models.CharField(max_length=250)
    unidad_medida = models.IntegerField(choices=CHOICE_MEDIDA)
    calorias = models.FloatField(null=True, blank=True)
    proteinas = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return u'%s - %s - %s' % (self.codigo, self.nombre, self.get_unidad_medida_display())


class CultivosHuertosFamiliares(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    cultivo = models.ForeignKey(CultivosHuertos)
    cantidad_cosechada = models.FloatField()
    consumo_familia = models.FloatField('Consumo de la familia')
    consumo_animal = models.FloatField()
    procesamiento = models.FloatField()
    venta = models.FloatField()
    precio = models.FloatField('Precio de venta en C$')
    #costo = models.FloatField('Costo por Mz en C$')
    mercado = models.ForeignKey(TipoMercado)
    iniciativas = models.IntegerField(choices=CHOICE_INICIATIVAS, null=True, blank=True)

    total = models.FloatField(editable=False)

    def save(self, *args, **kwargs):
        '''Save sobrecargado para calcular totales'''

        self.total = self.venta * self.precio
        super(CultivosHuertosFamiliares, self).save(*args, **kwargs)

        models.signals.post_save.send(sender=Encuesta, instance=self.encuesta)

    class Meta:
        verbose_name_plural = '23_1 Cultivos de huertos familiares en la finca'

class CostoHuerto(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    total_mz = models.FloatField('Área Total en Mz')
    costo = models.FloatField('Costo total en C$')

    class Meta:
        verbose_name_plural = 'Total Mz y costo para huerto familiar'


#cultivos de frutas familiares

class CultivosFrutas(models.Model):
    codigo = models.CharField(max_length=4)
    nombre = models.CharField(max_length=250)
    unidad_medida = models.IntegerField(choices=CHOICE_MEDIDA)
    calorias = models.FloatField(null=True, blank=True)
    proteinas = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return u'%s - %s - %s' % (self.codigo, self.nombre, self.get_unidad_medida_display())


class CultivosFrutasFinca(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    cultivo = models.ForeignKey(CultivosFrutas)
    cantidad_cosechada = models.FloatField()
    consumo_familia = models.FloatField('Consumo de la familia')
    consumo_animal = models.FloatField()
    procesamiento = models.FloatField()
    venta = models.FloatField()
    precio = models.FloatField('Precio de venta en C$')
    #costo = models.FloatField('Costo por Mz en C$')
    mercado = models.ForeignKey(TipoMercado)
    iniciativas = models.IntegerField(choices=CHOICE_INICIATIVAS, null=True, blank=True)

    total = models.FloatField(editable=False)

    def save(self, *args, **kwargs):
        '''Save sobrecargado para calcular totales'''

        self.total = self.venta * self.precio
        super(CultivosFrutasFinca, self).save(*args, **kwargs)

        models.signals.post_save.send(sender=Encuesta, instance=self.encuesta)

    class Meta:
        verbose_name_plural = '23_2 Frutas en la finca'

class CostoFrutas(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    total_mz = models.FloatField('Área Total en Mz')
    costo = models.FloatField('Costo total en C$')

    class Meta:
        verbose_name_plural = 'Total Mz y costo para huerto familiar'
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
    si_no = models.IntegerField(choices=CHOICE_JEFE, verbose_name='Comercializa SI/NO')
    cantidad_vendida = models.IntegerField('Cantidad vendida este año', null=True, blank=True)
    precio = models.FloatField('Precio de venta en C$', null=True, blank=True)
    mercado = models.ForeignKey(TipoMercado, null=True, blank=True)
    iniciativas = models.IntegerField(choices=CHOICE_INICIATIVAS, null=True, blank=True)

    total = models.FloatField(editable=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        '''Save sobrecargado para calcular totales'''

        self.total = self.cantidad_vendida * self.precio
        super(Ganaderia, self).save(*args, **kwargs)

        models.signals.post_save.send(sender=Encuesta, instance=self.encuesta)

    class Meta:
        verbose_name_plural = '24_1 Inventario de ganaderia mayor y menor'

#procesamiento

class ProductoProcesado(models.Model):
    codigo = models.CharField(max_length=4, null=True, blank=True)
    nombre = models.CharField(max_length=250)
    unidad_medida = models.IntegerField(choices=CHOICE_MEDIDA)
    calorias = models.FloatField(null=True, blank=True)
    proteinas = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return u'%s - %s - %s' % (self.codigo, self.nombre, self.get_unidad_medida_display())


class Procesamiento(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    producto = models.ForeignKey(ProductoProcesado)
    cantidad_total = models.FloatField('Cantidad', null=True, blank=True)
    cantidad = models.IntegerField('Cantidad consumida en el hogar')
    cantidad_vendida = models.IntegerField('Cantidad vendida este año')
    precio = models.FloatField('Precio de venta en C$')
    mercado = models.ForeignKey(TipoMercado)
    iniciativas = models.IntegerField(choices=CHOICE_INICIATIVAS, null=True, blank=True)

    total = models.FloatField(editable=False)

    def save(self, *args, **kwargs):
        '''Save sobrecargado para calcular totales'''

        self.total = self.cantidad_vendida * self.precio
        super(Procesamiento, self).save(*args, **kwargs)

        models.signals.post_save.send(sender=Encuesta, instance=self.encuesta)

    class Meta:
        verbose_name_plural = '24_2 Procesamiento de la producción'

#25  de la lista de los  productos  indicar cuales fueron introducidos/providos por
#el programa medios de vida sostenible

class IntroducidosTradicionales(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    cultivo = models.ForeignKey(Cultivos, verbose_name='Cultivos tradicionales')
    si_no = models.IntegerField(choices=CHOICE_JEFE,
        verbose_name='El dedicarse a cultivar ese cultivo es porque el progama lo ha promovido')
    anio = models.IntegerField('Año', null=True, blank=True)

    class Meta:
        verbose_name_plural = '25_1 Productos introducidos/promovidos tradicionales'


class IntroducidosHuertos(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    cultivo = models.ForeignKey(CultivosHuertos,
        verbose_name='Cultivos en huertos familiares')
    si_no = models.IntegerField(choices=CHOICE_JEFE,
        verbose_name='El dedicarse a cultivar ese cultivo es porque el progama lo ha promovido')
    anio = models.IntegerField('Año', null=True, blank=True)

    class Meta:
        verbose_name_plural = '25_2 Productos introducidos/promovidos huertos familiares'

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

    total = models.FloatField(editable=False)

    def save(self, *args, **kwargs):
        '''Save sobrecargado para calcular totales'''

        self.total = self.cantidad * self.cantidad_veces
        super(GastoHogar, self).save(*args, **kwargs)

        models.signals.post_save.send(sender=Encuesta, instance=self.encuesta)

    class Meta:
        verbose_name_plural = '26_Gastos generales del hogar'

class TipoGasto(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

class GastoProduccion(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    tipo = models.ForeignKey(TipoGasto)
    cantidad = models.FloatField('Cantidad mensual en C$')
    cantidad_veces = models.FloatField('Cantidad de veces en el año')

    total = models.FloatField(editable=False)

    def save(self, *args, **kwargs):
        '''Save sobrecargado para calcular totales'''

        self.total = self.cantidad * self.cantidad_veces
        super(GastoProduccion, self).save(*args, **kwargs)

        models.signals.post_save.send(sender=Encuesta, instance=self.encuesta)

    class Meta:
        verbose_name_plural = '27_Gastos generales para la producción'


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
    algun_prestamo = models.IntegerField(choices=CHOICE_JEFE,
                     verbose_name='En el último año ha recibido algún tipo de prestamo/crédito')
    monto = models.FloatField('28.1_¿Cuál fue el monto en C$?', null=True, blank=True)
    pago = models.FloatField('28.2_¿Pago mensual en C$?', null=True, blank=True)
    recibe = models.ManyToManyField(RecibePrestamo,
                                    verbose_name='28.3_¿De quien recibe el prestamo/crédito', blank=True)
    uso = models.ManyToManyField(UsoPrestamo,
                                verbose_name='28.4_¿Cuál fue el uso del prestamo/crédito', blank=True)


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
                                            verbose_name='29.1_Mencione cinco principales',blank=True)
    manejo = models.IntegerField(choices=CHOICE_MANEJO,
                    verbose_name='30_Sobre el manejo del suelo ¿Cómo preparan el suelo?', null=True, blank=True)
    traccion = models.IntegerField(choices=CHOICE_TRACCION,
                    verbose_name='31_¿Qué tipo de tracción utilizan para la preparación del suelo?', null=True, blank=True)
    fertilidad = models.IntegerField(choices=CHOICE_JEFE,
                    verbose_name='32_¿Realizan análisis de fertilidad del suelo?', null=True, blank=True)
    control = models.IntegerField(choices=CHOICE_JEFE,
                    verbose_name='33_¿Realiza control y monitoreo de plagas y enfermedades?', null=True, blank=True)

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
    misma_finca = models.IntegerField(
        verbose_name='34_¿Qué porcentaje alimentos que consumen en su hogar provienen de la misma finca?', null=True, blank=True)
    economico = models.IntegerField(choices=CHOICE_JEFE,
        verbose_name='35_¿Disponen suficiente recursos económicos para manejo de finca?',
        null=True, blank=True)
    secado = models.IntegerField(choices=CHOICE_JEFE,
        verbose_name='36_¿Dispone de tecnología para el secado y almacenamiento de cosecha?', null=True, blank=True)
    tipo_secado = models.ForeignKey(TipoSecado, verbose_name='Si es si cuál?',
        null=True, blank=True)
    plan_cosecha = models.IntegerField(choices=CHOICE_JEFE,
        verbose_name='37_¿Cuentan con un plan de cosecha?',
        null=True, blank=True)
    ayuda = models.IntegerField(choices=CHOICE_JEFE,
        verbose_name='38_¿Cuentan con ayuda de alimentos en momentos de escasez?',
        null=True, blank=True)
    suficiente_alimento = models.IntegerField(choices=CHOICE_JEFE,
        verbose_name='39_¿Le ha preocupado que en su hogar no hubiera suficiente alimentos?', null=True, blank=True)
    consumo_diario = models.IntegerField(choices=CHOICE_JEFE,
        verbose_name='40_¿Considera que su familia cuenta con la cantidad necesaria de alimentos que necesitan para el consumo diario del hogar?',
        null=True, blank=True)

    class Meta:
        verbose_name_plural = 'VI. Seguridad alimentaria'

CHOICE_FENOMENOS = (
            ('A','Sequía'),
            ('B','Inundación'),
            ('C','Deslizamiento'),
            ('D','Viento'),
        )
CHOICE_AGRICOLA = (
            ('A','Falta de semilla'),
            ('B','Mala calidad de la semilla'),
            ('C','Falta de riego'),
            ('D','Poca Tierra'),
        )
CHOICE_MERCADO = (
            ('A','Bajo precio'),
            ('B','Falta de venta'),
            ('C','Mala calidad del producto'),
        )
CHOICE_INVERSION = (
            ('A','Falta de crédito'),
            ('B','Intereses altos'),
        )

class RespuestaNo41(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    fenomeno = MultiSelectField(choices=CHOICE_FENOMENOS, null=True, blank=True)
    agricola = MultiSelectField(choices=CHOICE_AGRICOLA, null=True, blank=True)
    mercado = MultiSelectField(choices=CHOICE_MERCADO, null=True, blank=True)
    inversion = MultiSelectField(choices=CHOICE_INVERSION, null=True, blank=True)

    class Meta:
        verbose_name_plural = '40.1_Si responde NO'

class AdquiereAgua(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

class TrataAgua(models.Model):
    nombre = models.CharField(max_length=250)

    def __unicode__(self):
        return self.nombre

class OtrasSeguridad(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    adquiere_agua = models.ForeignKey(AdquiereAgua,
                    verbose_name='41_En momentos de sequía como adquiere el agua de consumo')
    tratamiento = models.IntegerField(choices=CHOICE_JEFE,
                    verbose_name='41_1 Le da algún tipo de tratamiento:')
    tipo_tratamiento = models.ForeignKey(TrataAgua, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Pregunta 42'

#VII. Consumo de alimentos

class ProductosFueraFinca(models.Model):
    nombre = models.CharField(max_length=250)
    unidad_medida = models.CharField(max_length=150)
    calorias = models.FloatField(null=True, blank=True)
    proteinas = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return u'%s en %s' % (self.nombre, self.unidad_medida)

class AlimentosFueraFinca(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    producto = models.ForeignKey(ProductosFueraFinca)
    cantidad = models.FloatField('Cantidad mensual')
    precio = models.FloatField('Precio unitario en C$')

    total = models.FloatField(editable=False)

    def save(self, *args, **kwargs):
        '''Save sobrecargado para calcular totales'''

        self.total = self.cantidad * self.precio
        super(AlimentosFueraFinca, self).save(*args, **kwargs)

        # activar signal post_save de encuesta
        models.signals.post_save.send(sender=Encuesta, instance=self.encuesta)

    def __unicode__(self):
        return u'%s' % (self.producto)

    class Meta:
        verbose_name_plural = '42_Indique los alimentos que compra fuera de la finca'

CHOICER_INGRESO = (
            (1,'Cultivo tradicionales '),
            (2,'Cultivos en huertos familiares '),
            (3,'Frutales en finca'),
            (4,'Ganadería mayor y menor'),
            (5,'Productos procesados'),
            (6,'Otras fuentes'),
    )

#VII Genero

class Genero(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    tipo = models.IntegerField(choices=CHOICER_INGRESO)
    porcentaje = models.IntegerField(choices=CHOICE_PORCENTAJE)

    class Meta:
        verbose_name_plural = '43_¿Qué porcentaje de ingreso es aportado por la mujer (compañera del jefe del hogar)'

class Genero1(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    tipo = models.IntegerField(choices=CHOICE_JEFE,
        verbose_name='44 ¿Tiene crédito a nombre de la mujer (compañera del jefe del hogar)?')
    monto = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name_plural = '44_¿Tiene crédito a nombre de la mujer (compañera del jefe del hogar)?'


CHOICER_COSAS_MUJER = (
            (1,'Panel solar'),
            (2,'Animales (Ganado mayor o menor)'),
            (3,'Equipos de producción'),
    )

class Genero2(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    pregunta = models.IntegerField(choices=CHOICER_COSAS_MUJER)
    respuesta = models.IntegerField(choices=CHOICE_JEFE)

    class Meta:
        verbose_name_plural = '45_¿Tiene a nombre de la mujer (compañera del jefe del hogar) algunos de los siguientes bienes?'

class Genero3(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    respuesta = models.IntegerField(choices=CHOICE_JEFE,
        verbose_name='¿La mujer (compañera del jefe del hogar) pertenece a algún tipo de organización?')

    class Meta:
        verbose_name_plural = '46_¿La mujer (compañera del jefe del hogar) pertenece a algún tipo de organización ?'

CHOICER_NIVEL_MUJER = (
            (1,'No lee, ni escribe'),
            (2,'Primaria incompleta'),
            (3,'Primaria completa'),
            (4,'Secundaria incompleta'),
            (5,'Bachiller'),
            (6,'Universitario o técnico'),
    )

class Genero4(models.Model):
    encuesta = models.ForeignKey(Encuesta)
    opcion = models.IntegerField(choices=CHOICER_NIVEL_MUJER,
        verbose_name='¿nivel de educación de la mujer (compañera del jefe del hogar)?')

    class Meta:
        verbose_name_plural = '47_¿Cuál es el nivel de educación de la mujer (compañera del jefe del hogar)'


class TotalIngreso(models.Model):
    encuesta = models.OneToOneField(Encuesta)
    total = models.FloatField(editable=False)
    total_gasto = models.FloatField(editable=False)
    total_gasto_fuera_finca = models.FloatField(editable=False)

    class Meta:
        verbose_name_plural = 'Totales'

    #def __unicode__(self):
    #    return 'Total para la encuesta %s' % self.encuesta

    def save(self, *args, **kwargs):
        self.total = self._get_total()
        self.total_gasto = self._get_total_gasto()
        self.total_gasto_fuera_finca = self._get_total_gasto_fuera_finca()

        super(TotalIngreso, self).save(*args, **kwargs)

    def _get_total(self):
        params = dict(encuesta = self.encuesta)
        totales = [
                    Procesamiento.objects.filter(**params).aggregate(t=models.Sum('total'))['t'], \
                    Ganaderia.objects.filter(**params).aggregate(t=models.Sum('total'))['t'], \
                    CultivosHuertosFamiliares.objects.filter(**params).aggregate(t=models.Sum('total'))['t'], \
                    CultivosTradicionales.objects.filter(**params).aggregate(t=models.Sum('total'))['t'], \
                    Fuentes.objects.filter(**params).aggregate(t=models.Sum('total'))['t'], \
                    CultivosFrutasFinca.objects.filter(**params).aggregate(t=models.Sum('total'))['t'], \
                ]
        total = sum(filter(None, totales))
        return total

    def _get_total_gasto(self):
        params = dict(encuesta = self.encuesta)
        totales = [
                    GastoProduccion.objects.filter(**params).aggregate(t=models.Sum('total'))['t'], \
                    GastoHogar.objects.filter(**params).aggregate(t=models.Sum('total'))['t'], \
                ]
        total_gasto = sum(filter(None, totales))
        return total_gasto

    def _get_total_gasto_fuera_finca(self):
        params = dict(encuesta = self.encuesta)
        totales = [
                    AlimentosFueraFinca.objects.filter(**params).aggregate(t=models.Sum('total'))['t'],
                ]
        total_gasto_fuera = sum(filter(None, totales))
        return total_gasto_fuera

@receiver(post_save, sender=Encuesta)
def create_encuesta_callback(sender, **kwargs):
    encuesta = kwargs['instance']
    try:
        total_ingreso = TotalIngreso.objects.get(encuesta=encuesta)
        total_ingreso.save()
    except:
        total_ingreso = TotalIngreso(encuesta=encuesta)
        total_ingreso.save()
