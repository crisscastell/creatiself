from django.contrib import admin
from .models import (
    Rol, Usuario, Pais, Estado, Ciudad, Representante, Parentesco, Paciente,
    PacienteRepresentante, AntecedentesPersonales, Condicion, Cita, DetalleCita,
    PacienteCita, Empleado
)

# Registro de modelos

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre_rol',)
    search_fields = ('nombre_rol',)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined')
    list_filter = ('is_active',)


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ('nombre_pais',)
    search_fields = ('nombre_pais',)


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('nombre_estado', 'pais')
    list_filter = ('pais',)
    search_fields = ('nombre_estado',)


@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ('nombre_ciudad', 'estado')
    list_filter = ('estado',)
    search_fields = ('nombre_ciudad',)


@admin.register(Representante)
class RepresentanteAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'apellido', 'telefono', 'edad', 'sexo', 'parentesco')
    list_filter = ('sexo', 'parentesco')
    search_fields = ('cedula', 'nombre', 'apellido')


@admin.register(Parentesco)
class ParentescoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'apellido', 'telefono', 'edad', 'sexo', 'nivel_academico', 'pais', 'estado', 'ciudad')
    list_filter = ('sexo', 'nivel_academico', 'pais', 'estado', 'ciudad')
    search_fields = ('cedula', 'nombre', 'apellido')


@admin.register(PacienteRepresentante)
class PacienteRepresentanteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'representante')
    list_filter = ('paciente', 'representante')
    search_fields = ('paciente__nombre', 'representante__nombre')


@admin.register(AntecedentesPersonales)
class AntecedentesPersonalesAdmin(admin.ModelAdmin):
    list_display = ('descripcion',)
    search_fields = ('descripcion',)


@admin.register(Condicion)
class CondicionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre', 'descripcion')


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora', 'modalidad', 'motivo_consulta', 'paciente')
    list_filter = ('modalidad', 'paciente')
    search_fields = ('paciente__nombre', 'motivo_consulta')


@admin.register(DetalleCita)
class DetalleCitaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'cita')
    list_filter = ('cita',)
    search_fields = ('titulo', 'anotacion', 'conclusion')


@admin.register(PacienteCita)
class PacienteCitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'cita')
    list_filter = ('paciente', 'cita')
    search_fields = ('paciente__nombre', 'cita__motivo_consulta')


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'apellido', 'cargo', 'status')
    list_filter = ('cargo', 'status', 'nivel_academico', 'sexo')
    search_fields = ('cedula', 'nombre', 'apellido')