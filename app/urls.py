from django.urls import path
from app.views import *
from app.viewscitas import *
from app.viewspacientes import *
from app.viewsempleados import *


urlpatterns = [
    path("", login, name='Login'),

    path('index/', index, name='Index'),
    path('pacientes/crear', crear_pacientes, name='Crear_pacientes'),
    path('pacientes/listar/', listar_pacientes, name='Listar_pacientes'),
    path('editar_paciente/<int:id>/', editar_paciente, name='Editar_paciente'),
    path('api/paises/', get_countries, name='obtener_paises'),
    path('api/estados/', obtener_estados, name='obtener_estados'),
    path('api/ciudades/', obtener_ciudades, name='obtener_ciudades'),
    
    path('crear/citas', crear_cita, name='Crear_citas'),
    path('listar/citas', listar_citas, name='Listar_citas'),
    path('editar_cita/<int:id>/', editar_cita, name='Editar_cita'),

     path('crear_empleado/', crear_empleado, name='Crear_empleado'),
    path('listar_empleados/', listar_empleados, name='Listar_empleados'),
    path('crear_usuario/', crear_usuario, name='Crear_usuario'),
    path('listar_usuarios/', listar_usuarios, name='Listar_usuarios'),

    path('cita/<int:cita_id>/detalle/crear/', crear_detalle_cita, name='Crear_detalle_cita'),
    path('cita/<int:cita_id>/detalle/listar/', listar_detalles_cita, name='Listar_detalles_cita'),
    path('detalle/editar/<int:detalle_cita_id>/', editar_detalle_cita, name='Editar_detalle_cita'),
    path('detalle/eliminar/<int:detalle_cita_id>/', eliminar_detalle_cita, name='Eliminar_detalle_cita'),

    path('tablas/', tablas, name='Tablas'),

    path('antecedentes_personales/crear', crear_antecedente, name='Crear_antecedentes'),
    path('antecedentes_personales/listar', listar_antecedentes, name='Listar_antecedentes'),
    path('editar_antecedente/<int:id>/', editar_antecedente, name='Editar_antecedente'),
    path('eliminar_antecedente/<int:id>/', eliminar_antecedente, name='Eliminar_antecedente'),

    path('condicion/crear/', crear_condicion, name='Crear_condicion'),
    path('condicion/listar', listar_condiciones, name='Listar_condiciones'),
    path('editar_condicion/<int:id>/', editar_condicion, name='Editar_condicion'),
    path('eliminar_condicion/<int:id>/', eliminar_condicion, name='Eliminar_condicion'),
]

