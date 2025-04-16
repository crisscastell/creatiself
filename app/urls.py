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
    path('pacientes/caracteristicas', caracteristicas, name='Caracteristicas'),

    path('relaciones/crear/', crear_relacion, name='Crear_relacion'),
    path('relaciones/', lista_relaciones, name='Listar_relaciones'),
    
    path('crear/citas', crear_cita, name='Crear_citas'),
    path('listar/citas', listar_citas, name='Listar_citas'),
    path('editar_cita/<int:id>/', editar_cita, name='Editar_cita'),

     path('crear_empleado/', crear_empleado, name='Crear_empleado'),
    path('listar_empleados/', listar_empleados, name='Listar_empleados'),
    path('editar_empleado/<int:id>/', editar_empleado, name='Editar_empleado'),

    path('crear_usuario/', crear_usuario, name='Crear_usuario'),
    path('listar_usuarios/', listar_usuarios, name='Listar_usuarios'),
    path('editar_usuario/<int:id>/', editar_usuario, name='Editar_usuario'),
    

    path('cita/<int:cita_id>/detalle/crear/', crear_detalle_cita, name='Crear_detalle_cita'),
    path('cita/<int:cita_id>/detalle/listar/', listar_detalles_cita, name='Listar_detalles_cita'),
    path('detalle/editar/<int:detalle_cita_id>/', editar_detalle_cita, name='Editar_detalle_cita'),

    path('tablas/', tablas, name='Tablas'),

    path('caracteristicas/listar', caracteristicas, name='Caracteristicas'),

    path('antecedentes_personales/crear', crear_antecedente, name='Crear_antecedentes'),
    path('editar_antecedente/<int:id>/', editar_antecedente, name='Editar_antecedente'),

    path('condicion/crear/', crear_condicion, name='Crear_condicion'),
    path('editar_condicion/<int:id>/', editar_condicion, name='Editar_condicion'),
    
]

