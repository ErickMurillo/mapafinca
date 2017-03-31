# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.

class Pais(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, null=True, help_text="Usado como url unica(autorellenado)")
    codigo = models.CharField(max_length=2,
                help_text='Código de 2 letras del país, ejemplo : Nicaragua (ni)')
    latitud = models.DecimalField('Latitud', max_digits=8, decimal_places=5, blank=True, null=True)
    longitud = models.DecimalField('Longitud', max_digits=8, decimal_places=5, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Países"

    def __unicode__(self):
        return self.nombre

class Departamento(models.Model):
    id = models.IntegerField("Código", primary_key=True)
    pais = models.ForeignKey(Pais)
    nombre = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(unique=True, null=True, help_text="Usado como url unica(autorellenado)")
    extension = models.DecimalField("Extension Territorials", max_digits=10, decimal_places=2, null=True, blank=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Departamentos"
        ordering = ['nombre']

class Municipio(models.Model):
    id = models.IntegerField("Código", primary_key=True)
    departamento = models.ForeignKey(Departamento)
    nombre = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(unique=True, null=True, help_text="Usado como url unica(autorellenado)")
    extension = models.DecimalField("Extension Territorial", max_digits=10, decimal_places=2, blank=True, null=True)
    latitud = models.DecimalField('Latitud', max_digits=8, decimal_places=5, blank=True, null=True)
    longitud = models.DecimalField('Longitud', max_digits=8, decimal_places=5, blank=True, null=True)

    def __unicode__(self):
        return '%s - %s' % (self.departamento.nombre, self.nombre)

    class Meta:
        verbose_name_plural = "Municipios"
        ordering = ['departamento__nombre', 'nombre']

class Comunidad(models.Model):
    municipio = models.ForeignKey(Municipio)
    nombre = models.CharField(max_length=40)

    class Meta:
        verbose_name_plural="Comunidades"
        ordering = ['nombre']

    def __unicode__(self):
        return u'%s' % self.nombre

class Microcuenca(models.Model):
    comunidad = models.ForeignKey(Comunidad)
    nombre = models.CharField(max_length=40)

    class Meta:
        verbose_name_plural="Microcuencas"
        ordering = ['nombre']

    def __unicode__(self):
        return u'%s' % self.nombre
