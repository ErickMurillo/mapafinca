from django.conf.urls import url
from encuestas import views

urlpatterns = [
    url(r'^$', views.IndexView, name='index'),
    url(r'^mapa/$', views.MapaView.as_view(), name='mapa'),
    url(r'^primer_mapa/$', views.FirstMapaView.as_view(), name='primer-mapa'),
    url(r'^dashboard-principal/(?P<departamento_id>[0-9]+)/$', views.principal_dashboard, name='dashboard'),
    url(r'^dashboard-principal-pais/(?P<pais>[-_\w]+)/$', views.principal_dashboard_pais, name='dashboard-pais'),
    url(r'^finca/(?P<entrevistado_id>[0-9]+)/$', views.detalle_finca, name='detalle-finca'),
    #url(r'^finca/(?P<entrevistado_id>[0-9]+)/$', views.detalle_finca, name='detalle-finca'),
    url(r'^indicadores/$', views.indicadores, name='indicadores'),
    url(r'^indicadores1/$', views.indicadores1, name='indicadores1'),
    url(r'^mapa_dash/$', views.obtener_mapa_dashboard, name='obtener-lista'),
     url(r'^mapa_dash_pais/$', views.obtener_mapa_dashboard_pais, name='obtener-lista-pais'),
    url(r'^galeria/$', views.galeria_mapas_fincas, name='galeria'),
    url(r'^detalle_indicador/$', views.DetailIndicadorView.as_view(), name='galeria'),
    #otros indicadores
    url(r'^jefe_sexo/$', views.sexo_duenos, name='jefe-sexo'),
    url(r'^escolaridad/$', views.escolaridad, name='escolaridad'),
    url(r'^energia/$', views.energia, name='energia'),
    url(r'^agua/$', views.agua, name='agua'),
    url(r'^organizaciones/$', views.organizaciones, name='organizaciones'),
    url(r'^tierra/$', views.tierra, name='tierra'),
    url(r'^prestamos/$', views.prestamos, name='prestamos'),
    url(r'^practicas/$', views.practicas, name='practicas'),
    url(r'^seguridad/$', views.seguridad, name='seguridad'),
    url(r'^genero/$', views.genero, name='genero'),
    url(r'^ingresos/$', views.ingresos, name='ingreso'),
    url(r'^gastos/$', views.gastos, name='gastos'),
    url(r'^calorias/$', views.calorias, name='calorias'),
    url(r'^ciclos-productivos/$', views.productividad, name='ciclos_productivos'),
    url(r'^xls/$', views.save_as_xls, name='salvar_xls'),
    #borrar
    url(r'^ingreso_optimizado/$', views.ingreso_optimizado, name='ingreso_optimizado'),
    #filtros por ajax
    url(r'^ajax/depart/$', views.traer_departamento, name='get-depart'),
    url(r'^ajax/organi/$', views.traer_organizacion, name='get-organi'),
    url(r'^ajax/munis/$', views.traer_municipio, name='get-munis'),
    url(r'^ajax/comunies/$', views.traer_comunidad, name='get-comunies'),
]
