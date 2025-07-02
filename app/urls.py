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

    path('relaciones/', listar_relaciones, name='Listar_relaciones'),
    path('relaciones/editar/<int:id>/', editar_relacion, name='Editar_relacion'),

    path('representante/crear/', crear_representante, name='Crear_representante'),
    path('representantes/listar', listar_representantes, name='Listar_representantes'),
    
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
    path('api/citas/', api_citas, name='api_citas'),

    path('tablas/', tablas, name='Tablas'),

    path('caracteristicas/listar', caracteristicas, name='Caracteristicas'),

    path('historial/listar', historial, name='Historial'),

    path('appointment-counts/', GetAppointmentCounts.as_view(), name='get_appointment_counts'),

    path('antecedentes_personales/crear', crear_antecedente, name='Crear_antecedentes'),
    path('editar_antecedente/<int:id>/', editar_antecedente, name='Editar_antecedente'),
    path('antecedente/<int:pk>/ocultar/', ocultar_antecedente, name='Ocultar_antecedente'),

    path('condicion/crear/', crear_condicion, name='Crear_condicion'),
    path('editar_condicion/<int:id>/', editar_condicion, name='Editar_condicion'),
    path('condicion/<int:pk>/ocultar/', ocultar_condicion, name='Ocultar_condicion'),

    path('crear_pais/', crear_pais, name='Crear_pais'),
    path('editar_pais/<int:id>/', editar_pais, name='Editar_pais'),
    path('crear_estado/', crear_estado, name='Crear_estado'),
    path('editar_estado/<int:id>/', editar_estado, name='Editar_estado'),
    path('crear_ciudad/', crear_ciudad, name='Crear_ciudad'),
    path('editar_ciudad/<int:id>/', editar_ciudad, name='Editar_ciudad'),   
]

