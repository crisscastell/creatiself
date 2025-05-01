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
            messages.success(request, "empleado actualizado correctamente")
            return redirect('Listar_empleados')
        else:
            messages.error(request, "Error al actualizar el empleado")
    
    return redirect('Listar_empleados')

@login_required
def listar_empleados(request):
    usuario = request.user
    
    # Verificar rol de Administrador
    if not hasattr(usuario, 'rol') or usuario.rol.nombre_rol != 'Administrador':
        return redirect('acceso_denegado')
    
    # Base query
    empleados = Empleado.objects.select_related(
        'usuario', 
        'pais', 
        'estado', 
        'ciudad'
    ).all()
    
    # Búsqueda (ampliada con más campos)
    query = request.GET.get('q', '')
    if query:
        empleados = empleados.filter(
            Q(cedula__icontains=query) |
            Q(nombre__icontains=query) |
            Q(nombre2__icontains=query) |
            Q(apellido__icontains=query) |
            Q(apellido2__icontains=query) |
            Q(cargo__icontains=query) |
            Q(telefono__icontains=query) |
            Q(usuario__email__icontains=query)  # Búsqueda en FK Usuario
        )
    
    # Filtro por estado (activo/inactivo)
    status = request.GET.get('status')
    if status == '1':
        empleados = empleados.filter(status=True)  # Asumo que el campo se llama 'activo'
    elif status == '0':
        empleados = empleados.filter(status=False)
    
    # Paginación
    paginator = Paginator(empleados, 15)
    page_number = request.GET.get('page')
    empleados_paginados = paginator.get_page(page_number)
    
    # Contexto con datos para filtros/forms
    context = {
        'empleados': empleados_paginados,
        'query': query,
        'paises': Pais.objects.all(),
        'estados': Estado.objects.all(),
        'ciudades': Ciudad.objects.all(),
        'usuarios': Usuario.objects.all(),
        'niveles_academicos': Empleado._meta.get_field('nivel_academico').choices,
        'sexos': Empleado._meta.get_field('sexo').choices,
        'request': request,  # Asegúrate de pasar el request al contexto
    }
    
    return render(request, 'admin/listar_empleados.html', context)

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


@login_required
@login_required
def listar_usuarios(request):
    usuario = request.user
    
    # Verificar rol de Administrador
    if not hasattr(usuario, 'rol') or usuario.rol.nombre_rol != 'Administrador':
        return redirect('acceso_denegado')
    
    # Obtener todos los usuarios inicialmente
    usuarios = Usuario.objects.all()
    
    # Búsqueda
    query = request.GET.get('q', '')
    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(cedula__icontains=query)  # Asumiendo que tienes campo cedula
        )
    
    # Filtro por rol
    rol_id = request.GET.get('rol')
    if rol_id:
        usuarios = usuarios.filter(rol__id=rol_id)
    
    # Filtro por estado (activo/inactivo)
    status = request.GET.get('status')
    if status == '1':
        usuarios = usuarios.filter(is_active=True)
    elif status == '0':
        usuarios = usuarios.filter(is_active=False)
    
    # Obtener todos los roles para el select
    roles = Rol.objects.all()
    
    # Paginación (opcional)
    # paginator = Paginator(usuarios, 15)
    # page_number = request.GET.get('page')
    # usuarios = paginator.get_page(page_number)
    
    context = {
        'usuarios': usuarios,
        'roles': roles,
        'request': request,  # Importante para mantener los filtros
    }
    return render(request, 'admin/listar_usuarios.html', context)

def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente")
            return redirect('Listar_usuarios')  # Ajusta este nombre a tu URL
        else:
            messages.error(request, "Error al actualizar el usuario")
    
    else:
        form = UsuarioForm(instance=usuario)
    
    return redirect('Listar_usuarios')



