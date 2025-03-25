from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Q
from .forms import EmpleadoForm
from .models import *
from django.contrib.auth.decorators import login_required


@login_required
def crear_empleado(request):
    usuario = request.user
    if usuario.rol.nombre_rol == 'Administrador':
        return render(request, 'admin/crear_empleado.html')
    else:
        return redirect('acceso_denegado')

@login_required
def listar_empleados(request):
    usuario = request.user
    if usuario.rol.nombre_rol == 'Administrador':
        empleados = Empleado.objects.all()
        return render(request, 'admin/listar_empleados.html', {'empleados': empleados})
    else:
        return redirect('acceso_denegado')

@login_required
def crear_usuario(request):
    usuario = request.user
    if usuario.rol.nombre_rol == 'Administrador':
        return render(request, 'admin/crear_usuario.html')
    else:
        return redirect('acceso_denegado')

@login_required
def listar_usuarios(request):
    usuario = request.user
    if usuario.rol.nombre_rol == 'Administrador':
        usuarios = Usuario.objects.all()
        return render(request, 'admin/listar_usuarios.html', {'usuarios': usuarios})
    else:
        return redirect('acceso_denegado')

def acceso_denegado(request):
    messages.error(request, 'Acceso denegado: No tienes permisos para acceder a esta página.')
    return redirect('pagina_principal')  # Redirige a la página principal o a donde desees