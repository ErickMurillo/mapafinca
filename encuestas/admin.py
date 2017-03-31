from django.contrib import admin
from .models import *
from .forms import *

class InlineDuenoSi(admin.TabularInline):
    model = DuenoSi
    extra = 1
    max_num = 1

class InlineDuenoNo(admin.TabularInline):
    model = DuenoNo
    extra = 1
    max_num = 1

class InlineSexoMiembros(admin.TabularInline):
    model = SexoMiembros
    extra = 1
    max_num = 1

class InlineDetalleMiembros(admin.TabularInline):
    model = DetalleMiembros
    extra = 1

class InlineEscolaridad(admin.TabularInline):
    model = Escolaridad
    extra = 1
    max_num = 8

class InlineTipoEnergia(admin.TabularInline):
    form = TipoEnergiaForm
    model = TipoEnergia
    extra = 1
    max_num = 1

class InlinePanelSolar(admin.TabularInline):
    #form = TipoEnergiaForm
    model = PanelSolar
    extra = 1
    max_num = 3

class InlineEnergiaSolarCocinar(admin.TabularInline):
    form = EnergiaSolarCocinarForm
    model = EnergiaSolarCocinar
    extra = 1
    max_num = 1

class InlineTipoCocinas(admin.TabularInline):
    form = TipoCocinasForm
    model = TipoCocinas
    extra = 1
    max_num = 1

class InlineAccesoAgua(admin.TabularInline):
    form = AccesoAguaForm
    model = AccesoAgua
    extra = 1
    max_num = 1

class InlineDisponibilidadAgua(admin.TabularInline):
    model = DisponibilidadAgua
    extra = 1
    max_num = 1

class InlineCalidadAgua(admin.TabularInline):
    model = CalidadAgua
    extra = 1
    max_num = 1

class InlineContaminada(admin.TabularInline):
    model = Contaminada
    extra = 1
    max_num = 5

class InlineEvidencia(admin.TabularInline):
    model = Evidencia
    extra = 1

class InlineTratamientoAgua(admin.TabularInline):
    model = TratamientoAgua
    extra = 1

class InlineUsosAgua(admin.TabularInline):
    model = UsosAgua
    extra = 1
    max_num = 5

class InlineOrganizacionComunitaria(admin.TabularInline):
    model = OrganizacionComunitaria
    extra = 1
    max_num = 1

class InlineOrganizacionFinca(admin.TabularInline):
    model = OrganizacionFinca
    extra = 1
    max_num = 1

class InlineDistribucionTierra(admin.TabularInline):
    model = DistribucionTierra
    extra = 1

class InlinePercibeIngreso(admin.TabularInline):
    model = PercibeIngreso
    extra = 1
    max_num = 1

class InlineFuentes(admin.TabularInline):
    model = Fuentes
    extra = 1

class InlineCultivosTradicionales(admin.TabularInline):
    model = CultivosTradicionales
    extra = 1

class InlineCultivosHuertosFamiliares(admin.TabularInline):
    model = CultivosHuertosFamiliares
    extra = 1

class InlineCostoHuerto(admin.TabularInline):
    model = CostoHuerto
    extra = 1
    max_num = 1

class InlineCultivosFrutasFinca(admin.TabularInline):
    model = CultivosFrutasFinca
    extra = 1

class InlineCostoFrutas(admin.TabularInline):
    model = CostoFrutas
    extra = 1
    max_num = 1

class InlineGanaderia(admin.TabularInline):
    model = Ganaderia
    extra = 1

class InlineProcesamiento(admin.TabularInline):
    model = Procesamiento
    extra = 1

class InlineIntroducidosTradicionales(admin.TabularInline):
    model = IntroducidosTradicionales
    extra = 1

class InlineIntroducidosHuertos(admin.TabularInline):
    model = IntroducidosHuertos
    extra = 1

class InlineGastoHogar(admin.TabularInline):
    model = GastoHogar
    extra = 1

class InlineGastoProduccion(admin.TabularInline):
    model = GastoProduccion
    extra = 1

class InlinePrestamo(admin.TabularInline):
    model = Prestamo
    extra = 1
    max_num = 1

class InlinePracticasAgroecologicas(admin.TabularInline):
    model = PracticasAgroecologicas
    extra = 1
    max_num = 1

class InlineSeguridadAlimentaria(admin.TabularInline):
    model = SeguridadAlimentaria
    extra = 1
    max_num = 1

class InlineRespuestaNo41(admin.TabularInline):
    model = RespuestaNo41
    extra = 1
    max_num = 1

class InlineOtrasSeguridad(admin.TabularInline):
    model = OtrasSeguridad
    extra = 1
    max_num = 1

class InlineAlimentosFueraFinca(admin.TabularInline):
    model = AlimentosFueraFinca
    extra = 1

class InlineGenero(admin.TabularInline):
    model = Genero
    extra = 1
    max_num = 6

class InlineGenero1(admin.TabularInline):
    model = Genero1
    extra = 1
    max_num = 1

class InlineGenero2(admin.TabularInline):
    model = Genero2
    extra = 1
    max_num = 3

class InlineGenero3(admin.TabularInline):
    model = Genero3
    extra = 1
    max_num = 1

class InlineGenero4(admin.TabularInline):
    model = Genero4
    extra = 1
    max_num = 1

class AdminEncuesta(admin.ModelAdmin):
    form = ProductorAdminForm
    fields = (('entrevistado','fecha','estacion'),('encuestador','mapa_finca'), 'org_responsable','dueno',)
    def queryset(self, request):
        if request.user.is_superuser:
            return Encuesta.objects.all()
        return Encuesta.objects.filter(user=request.user)

    def save_model(self, request, obj, form, change):
      obj.user = request.user
      obj.save()

    exclude = ('user',)
    inlines = [InlineDuenoSi,InlineDuenoNo,InlineSexoMiembros,
                InlineDetalleMiembros,InlineEscolaridad,InlineTipoEnergia,InlinePanelSolar,
                InlineEnergiaSolarCocinar,InlineTipoCocinas,InlineAccesoAgua,
                InlineDisponibilidadAgua,InlineCalidadAgua,InlineContaminada,
                InlineEvidencia,InlineTratamientoAgua,InlineUsosAgua,
                InlineOrganizacionComunitaria,InlineOrganizacionFinca,
                InlineDistribucionTierra,InlinePercibeIngreso,InlineFuentes,
                InlineCultivosTradicionales,InlineCultivosHuertosFamiliares,
                InlineCostoHuerto,InlineCultivosFrutasFinca,InlineCostoFrutas,
                InlineGanaderia,InlineProcesamiento,InlineIntroducidosTradicionales,
                InlineIntroducidosHuertos,InlineGastoHogar,InlineGastoProduccion,
                InlinePrestamo,InlinePracticasAgroecologicas,InlineSeguridadAlimentaria,
                InlineRespuestaNo41,InlineOtrasSeguridad,InlineAlimentosFueraFinca,
                InlineGenero,InlineGenero1,InlineGenero2,InlineGenero3,InlineGenero4,]

    list_display = ('entrevistado','dueno','org_responsable','get_municipio','get_comunidad' ,'year')
    list_filter = ('org_responsable','year','entrevistado__pais','entrevistado__pais__departamento')
    search_fields = ('entrevistado__nombre',)

    def get_departamento(self, obj):
        return obj.entrevistado.departamento
    get_departamento.short_description = 'Departamento'
    #get_departamento.admin_order_field = 'entrevistado__departamento'

    def get_municipio(self, obj):
        return obj.entrevistado.municipio
    get_municipio.short_description = 'Municipio'
    get_municipio.admin_order_field = 'entrevistado__departamento__municipio'

    def get_comunidad(self, obj):
        return obj.entrevistado.comunidad
    get_comunidad.short_description = 'Comunidad'
    get_comunidad.admin_order_field = 'entrevistado__departamento__municipio__comunidad'

    class Media:
        css = {
            "all": ("css/my_styles_admin.css",)
        }
        js = ("js/code_admin.js",)

class EntrevistadoAdmin(admin.ModelAdmin):
    def queryset(self, request):
        if request.user.is_superuser:
            return Noticias.objects.all()
        return Noticias.objects.filter(user=request.user)

    def save_model(self, request, obj, form, change):
      obj.user = request.user
      obj.save()

    exclude = ('user',)
    list_display = ('nombre', 'sexo', 'jefe', 'pais', 'departamento')
    list_filter = ('sexo','pais','departamento')
    search_fields = ('nombre',)

#registro de los cultivos con sus propios calorias
from import_export.admin import ImportExportModelAdmin

class CultivosAdmin(ImportExportModelAdmin):
    list_display = ('codigo', 'nombre', 'unidad_medida', 'calorias', 'proteinas')
    list_display_links = ('codigo', 'nombre', )

class CultivosHuertosAdmin(ImportExportModelAdmin):
    list_display = ('codigo', 'nombre', 'unidad_medida', 'calorias', 'proteinas')
    list_display_links = ('codigo', 'nombre', )

class CultivosFrutasAdmin(ImportExportModelAdmin):
    list_display = ('codigo', 'nombre', 'unidad_medida', 'calorias', 'proteinas')
    list_display_links = ('codigo', 'nombre', )

class ProductoProcesadoAdmin(ImportExportModelAdmin):
    list_display = ('codigo', 'nombre', 'unidad_medida', 'calorias', 'proteinas')
    list_display_links = ('codigo', 'nombre', )

class ProductosFueraFincaAdmin(ImportExportModelAdmin):
    list_display = ('nombre', 'unidad_medida', 'calorias', 'proteinas')

class OrganizacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais', 'departamento', 'municipio')
# Register your models here.
admin.site.register(Encuestadores)
admin.site.register(OrganizacionResp, OrganizacionAdmin)
admin.site.register(Entrevistados, EntrevistadoAdmin)
admin.site.register(Encuesta, AdminEncuesta)
admin.site.register(Energia)
admin.site.register(FuenteEnergia)
admin.site.register(Cocinas)
admin.site.register(AguaConsumo)
admin.site.register(TipoContamindaAgua)
admin.site.register(OrgComunitarias)
admin.site.register(BeneficiosOrganizados)
admin.site.register(TipoFuenteIngreso)
admin.site.register(Cultivos, CultivosAdmin)
admin.site.register(TipoMercado)
admin.site.register(CultivosHuertos, CultivosHuertosAdmin)
admin.site.register(Animales)
admin.site.register(ProductoProcesado, ProductoProcesadoAdmin)
admin.site.register(TipoGasto)
admin.site.register(RecibePrestamo)
admin.site.register(UsoPrestamo)
admin.site.register(Practicas)
admin.site.register(TipoSecado)
admin.site.register(AdquiereAgua)
admin.site.register(TrataAgua)
admin.site.register(ProductosFueraFinca, ProductosFueraFincaAdmin)
admin.site.register(CultivosFrutas, CultivosFrutasAdmin)
