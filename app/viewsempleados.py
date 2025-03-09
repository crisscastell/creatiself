from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q
from .forms import EmpleadoForm
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

@login_required
# Función para verificar si el usuario es administrador
def es_administrador(user, request):
    print(f"Usuario autenticado: {request.user.username}, Rol: {request.user.rol.nombre_rol}")
    return user.is_authenticated and user.rol.nombre_rol.lower() == "administrador"


# Vista para crear empleados (solo administradores pueden acceder)
@user_passes_test(es_administrador, login_url='/sin-permiso/')
def crear_empleado(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Listar_empleados')  # Redirige a la vista de listar empleados
    else:
        form = EmpleadoForm()

    # Obtener los datos relacionados como los países, estados y ciudades
    paises = Pais.objects.all()
    estados = Estado.objects.all()
    ciudades = Ciudad.objects.all()

    return render(request, 'admin/crear_empleado.html', {
        'form': form,
        'paises': paises,
        'estados': estados,
        'ciudades': ciudades
    })

# Vista para listar empleados (solo administradores pueden acceder)
@user_passes_test(es_administrador, login_url='/sin-permiso/')
def listar_empleados(request):
    query = request.GET.get('q', '')  # Captura el valor de búsqueda desde la URL
    empleados_list = Empleado.objects.all()

    # Filtrar por nombre, apellido, o cédula
    if query:
        empleados_list = empleados_list.filter(
            Q(cedula__icontains=query) | 
            Q(nombre__icontains=query) | 
            Q(apellido__icontains=query)
        )

    # Paginación (15 empleados por página)
    paginator = Paginator(empleados_list, 15)
    page_number = request.GET.get('page')
    empleados = paginator.get_page(page_number)

    return render(request, 'admin/listar_empleados.html', {
        'empleados': empleados, 
        'query': query
    })

@login_required
def editar_empleado(request, id):
    empleado = get_object_or_404(Empleado, id=id)  # Asegura que el empleado existe
    form = EmpleadoForm(instance=empleado)

    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            return redirect('Listar_empleados')  # Redirige a la lista de empleados después de editar

    return render(request, 'admin/editar_empleado.html', {'form': form, 'empleado': empleado})