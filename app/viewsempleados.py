from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Q
from .forms import EmpleadoForm, UsuarioForm
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

def crear_empleado(request):
    usuario = request.user
    # Comprobamos si el usuario tiene el rol de 'Administrador'
    if usuario.rol.nombre_rol == 'Administrador':
        if request.method == 'POST':
            form = EmpleadoForm(request.POST)
            if form.is_valid():
                empleado = form.save(commit=False)
                empleado.usuario = request.user
                empleado.save()
                return redirect('Listar_empleados')
            else:
                print(form.errors) # Cambia a la URL que muestra la lista de empleados

        # Si el método es GET, mostramos el formulario vacío
        form = EmpleadoForm()

        # Obtenemos los países, estados y ciudades desde la base de datos
        usuarios = Usuario.objects.all()
        paises = Pais.objects.all()
        estados = Estado.objects.all()
        ciudades = Ciudad.objects.all()

        # Pasamos estos datos al contexto
        context = {
            'form': form,
            'paises': paises,
            'estados': estados,
            'ciudades': ciudades,
            'usuarios':usuarios
        }

        return render(request, 'admin/crear_empleado.html', context)
    else:
        return redirect('acceso_denegado')
    
def editar_empleado(request, id):
    empleado = get_object_or_404(Empleado, id=id)
    
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            return redirect('Listar_empleados') 
    else:
        form = EmpleadoForm(instance=empleado)

    paises = Pais.objects.all()
    estados = Estado.objects.all()
    ciudades = Ciudad.objects.all()
    
    return render(request, 'admin/listar_empleados.html', {
        'form': form,
        'empleado': empleado,
        'paises': paises,
        'estados': estados,
        'ciudades': ciudades
    })
    
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
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Listar_usuarios')  # Redirige a donde quieras después de guardar
        else:
            print(form.errors)
    else:
        form = UsuarioForm()

    roles = Rol.objects.all()

    return render(request, 'admin/crear_usuario.html', {'form': form, 'roles': roles})

def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('Listar_usuarios') 
    else:
        form = UsuarioForm(instance=usuario)

    roles = Rol.objects.all()

    return render(request, 'usuario/listar_usuarios.html', {
        'form': form,
        'usuario': usuario,
        'roles': roles
    })

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