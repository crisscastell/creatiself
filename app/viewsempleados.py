from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Q
from .forms import EmpleadoForm, UsuarioCreationForm, UsuarioChangeForm 
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Q
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .models import Paciente 
from .models import Cita
from django.db.models import Prefetch
from django.db.models import IntegerField
from django.db.models import Count, Q, Subquery, OuterRef
from datetime import datetime, timedelta

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
                print(form.errors)

        # Si el método es GET, mostramos el formulario vacío
        form = EmpleadoForm()

        # Obtenemos los datos necesarios desde la base de datos
        usuarios = Usuario.objects.filter(is_active=True).order_by('username')
        paises = Pais.objects.all().order_by('nombre_pais')
        estados = Estado.objects.all().order_by('nombre_estado')
        ciudades = Ciudad.objects.all().order_by('nombre_ciudad')
        
        # Estadísticas para el panel lateral
        total_empleados = Empleado.objects.count()
        empleados_activos = Empleado.objects.filter(status=True).count()
        empleados_inactivos = total_empleados - empleados_activos
        
        # Distribución por género
        distribucion_genero = Empleado.objects.values('sexo').annotate(total=Count('id'))
        
        # Distribución por nivel académico
        distribucion_nivel = Empleado.objects.values('nivel_academico').annotate(total=Count('id'))
        
        # Edad promedio
        empleados_con_edad = Empleado.objects.exclude(edad__isnull=True)
        edad_promedio = empleados_con_edad.aggregate(avg_edad=Avg('edad'))['avg_edad'] or 0
        
        # Cargos más comunes
        cargos_comunes = Empleado.objects.values('cargo').annotate(total=Count('id')).order_by('-total')[:5]

        # Contexto con todos los datos necesarios
        context = {
            'form': form,
            'paises': paises,
            'estados': estados,
            'ciudades': ciudades,
            'usuarios': usuarios,
            'total_empleados': total_empleados,
            'empleados_activos': empleados_activos,
            'empleados_inactivos': empleados_inactivos,
            'distribucion_genero': distribucion_genero,
            'distribucion_nivel': distribucion_nivel,
            'edad_promedio': round(edad_promedio, 1),
            'cargos_comunes': cargos_comunes,
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
    empleados = Empleado.objects.select_related('usuario', 'pais', 'estado', 'ciudad')
    
    # Búsqueda y filtros
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
            Q(usuario__email__icontains=query)
        )
    
    status = request.GET.get('status')
    if status == '1':
        empleados = empleados.filter(status=True)
    elif status == '0':
        empleados = empleados.filter(status=False)
    
    cargo_filter = request.GET.get('cargo')
    if cargo_filter and cargo_filter != 'all':
        empleados = empleados.filter(cargo__iexact=cargo_filter)
    
    cargos = Empleado.objects.values_list('cargo', flat=True).distinct().order_by('cargo')
    
    # Conteo de pacientes asignados
    empleados = empleados.annotate(
        pacientes_count=Count('paciente', distinct=True)
    )
    
    # Prefetch de pacientes asignados
    empleados = empleados.prefetch_related(
        Prefetch('paciente_set',
                queryset=Paciente.objects.only('id', 'nombre', 'apellido', 'cedula'),
                to_attr='pacientes_asignados')
    )
    
    # Estadísticas de citas - versión corregida
    hoy = datetime.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    
    # Primero obtenemos los IDs de empleados que necesitamos
    empleados_ids = empleados.values_list('id', flat=True)
    
    # Luego obtenemos las estadísticas de citas para estos empleados
    from django.db.models import F
    citas_stats = (
        Cita.objects
        .filter(paciente__empleado_asignado_id__in=empleados_ids)
        .values('paciente__empleado_asignado_id')
        .annotate(
            citas_count=Count('id'),
            citas_hoy=Count('id', filter=Q(fecha=hoy)),
            citas_semana=Count('id', filter=Q(fecha__range=[inicio_semana, fin_semana])),
            citas_pendientes=Count('id', filter=Q(estatus='pendiente')),
            citas_completadas=Count('id', filter=Q(estatus='completada')),
            citas_canceladas=Count('id', filter=Q(estatus='cancelada'))
        )
    )
    
    # Creamos un diccionario para mapear empleado_id a sus estadísticas
    stats_dict = {
        stat['paciente__empleado_asignado_id']: {
            'citas_count': stat['citas_count'],
            'citas_hoy': stat['citas_hoy'],
            'citas_semana': stat['citas_semana'],
            'citas_pendientes': stat['citas_pendientes'],
            'citas_completadas': stat['citas_completadas'],
            'citas_canceladas': stat['citas_canceladas']
        }
        for stat in citas_stats
    }
    
    # Prefetch para citas recientes (sin usar OuterRef)
    citas_recientes = (
        Cita.objects
        .filter(paciente__empleado_asignado_id__in=empleados_ids)
        .select_related('paciente')
        .order_by('-fecha', '-hora')
    )
    
    # Agrupamos citas por empleado
    from collections import defaultdict
    citas_por_empleado = defaultdict(list)
    for cita in citas_recientes:
        citas_por_empleado[cita.paciente.empleado_asignado_id].append(cita)
    
    # Ordenamos y limitamos a 5 citas por empleado
    for emp_id in citas_por_empleado:
        citas_por_empleado[emp_id] = sorted(
            citas_por_empleado[emp_id],
            key=lambda x: (x.fecha, x.hora),
            reverse=True
        )[:5]
    
    # Paginación
    empleados = empleados.order_by('-status', 'apellido', 'nombre')
    paginator = Paginator(empleados, 12)
    page_number = request.GET.get('page')
    empleados_paginados = paginator.get_page(page_number)
    
    # Añadimos las estadísticas a cada empleado
    for empleado in empleados_paginados:
        stats = stats_dict.get(empleado.id, {
            'citas_count': 0,
            'citas_hoy': 0,
            'citas_semana': 0,
            'citas_pendientes': 0,
            'citas_completadas': 0,
            'citas_canceladas': 0
        })
        empleado.citas_count = stats['citas_count']
        empleado.citas_hoy_count = stats['citas_hoy']
        empleado.citas_semana_count = stats['citas_semana']
        empleado.citas_pendientes_count = stats['citas_pendientes']
        empleado.citas_completadas_count = stats['citas_completadas']
        empleado.citas_canceladas_count = stats['citas_canceladas']
        empleado.citas_recientes = citas_por_empleado.get(empleado.id, [])
    
    context = {
        'empleados': empleados_paginados,
        'query': query,
        'status_filter': status,
        'cargo_filter': cargo_filter,
        'cargos': cargos,
        'paises': Pais.objects.all(),
        'estados': Estado.objects.all(),
        'ciudades': Ciudad.objects.all(),
        'usuarios': Usuario.objects.all(),
        'niveles_academicos': Empleado._meta.get_field('nivel_academico').choices,
        'sexos': Empleado._meta.get_field('sexo').choices,
        'request': request,
    }
    
    return render(request, 'admin/listar_empleados.html', context)

@login_required
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Si necesitas hacer algo adicional con el usuario antes de guardar
            user.save()
            return redirect('Listar_usuarios')
        else:
            print(form.errors)
    else:
        form = UsuarioCreationForm()

    roles = Rol.objects.all()
    return render(request, 'admin/crear_usuario.html', {'form': form, 'roles': roles})



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
            Q(email__icontains=query)
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

@login_required
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    
    if request.method == 'POST':
        form = UsuarioChangeForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente")
            return redirect('Listar_usuarios')
    else:
        form = UsuarioChangeForm(instance=usuario)

    return render(request, 'admin/crear_usuario.html', {
        'form': form,
        'editing': True  # Puedes usar este flag para mostrar diferente título en el template
    })


