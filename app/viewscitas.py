from django.shortcuts import render, redirect, get_object_or_404,  redirect
from django.http import HttpResponse
from app.models import Cita, DetalleCita, Paciente, RelacionPaciente
from app.forms import CitaForm, DetalleCitaForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from datetime import date 
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime
from django.db.models import Count
from datetime import time

def crear_cita(request):
    hoy = timezone.now().date()
    capacidad_maxima = 20

    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            
            # Asignación correcta según selección
            if form.cleaned_data.get('relacion'):  # Si se seleccionó una relación
                cita.relacion = form.cleaned_data['relacion']
                cita.paciente = None
            else:  # Si se seleccionó un paciente individual
                cita.paciente = form.cleaned_data['paciente']
                cita.relacion = None
            
            cita.save()
            messages.success(request, "Cita creada exitosamente")
            return redirect('Listar_citas')
    else:
        form = CitaForm(initial={
            'fecha': hoy,
            'estatus': 'pendiente'
        })

    # Preparación de datos para el template
    citas_hoy = Cita.objects.filter(fecha=hoy).count()
    disponibilidad = max(0, 100 - int((citas_hoy / capacidad_maxima) * 100))
    
    proximas_citas = []
    for cita in Cita.objects.filter(fecha__gte=hoy).order_by('fecha', 'hora')[:5]:
        if cita.paciente:
            paciente_nombre = f"{cita.paciente.nombre} {cita.paciente.apellido}"
            tipo_cita = "Individual"
        elif cita.relacion:
            paciente_nombre = f"{cita.relacion.paciente1.nombre} & {cita.relacion.paciente2.nombre}"
            tipo_cita = cita.relacion.get_tipo_relacion_display()
        else:
            paciente_nombre = 'Sin paciente'
            tipo_cita = ""
        
        if cita.estatus == 'pendiente':
            estatus_color = 'green'
        elif cita.estatus == 'completada':
            estatus_color = 'blue'
        else:
            estatus_color = 'red'
        
        proximas_citas.append({
            'paciente_nombre': paciente_nombre,
            'tipo_cita': tipo_cita,
            'fecha': cita.fecha.strftime('%d/%m/%Y'),
            'hora': cita.hora.strftime('%H:%M'),
            'estatus': cita.get_estatus_display(),
            'estatus_color': estatus_color
        })
    
    context = {
        'form': form,
        'pacientes': Paciente.objects.all(),
        'relaciones': RelacionPaciente.objects.all().select_related('paciente1', 'paciente2'),
        'proximas_citas': proximas_citas,
        'citas_hoy': citas_hoy,
        'disponibilidad': disponibilidad,
    }
    
    return render(request, 'citas/crear_cita.html', context)

def listar_citas(request):
    # Obtener el parámetro de búsqueda si existe
    query = request.GET.get('q')
    
    # Obtener todas las citas ordenadas
    citas_list = Cita.objects.all().order_by('-fecha', '-hora')
    
    # Filtrar si hay una búsqueda
    if query:
        citas_list = citas_list.filter(
            Q(paciente__nombre__icontains=query) |
            Q(paciente__apellido__icontains=query) |
            Q(fecha__icontains=query) |
            Q(hora__icontains=query) |
            Q(modalidad__icontains=query) |
            Q(motivo_consulta__icontains=query)
        )
    
    # Configurar la paginación (10 items por página)
    paginator = Paginator(citas_list, 10)
    page = request.GET.get('page')
    
    try:
        citas = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, mostrar la primera página
        citas = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página
        citas = paginator.page(paginator.num_pages)
    
    # Manejar la alerta de creación exitosa
    mostrar_alerta = request.session.pop('mostrar_alerta', False) if 'mostrar_alerta' in request.session else False
    
    return render(request, 'citas/listar_citas.html', {
        'citas': citas,
        'mostrar_alerta': mostrar_alerta,
        'query': query  # Pasar el término de búsqueda al template
    })


def editar_cita(request, id):
    cita = get_object_or_404(Cita, id=id)
    
    if request.method == 'POST':
        # Creamos una copia mutable del POST
        post_data = request.POST.copy()
        # Forzamos el paciente original para evitar modificaciones
        post_data['paciente'] = cita.paciente.id
        form = CitaForm(post_data, instance=cita)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Cita actualizada correctamente")
            return redirect('Listar_citas')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    return redirect('Listar_citas') 


def crear_detalle_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)  # Obtén la cita relacionada

    if request.method == "POST":
        form = DetalleCitaForm(request.POST)
        if form.is_valid():
            detalle_cita = form.save(commit=False)
            detalle_cita.cita = cita  # Asigna la cita al detalle de cita
            detalle_cita.save()
            return redirect('Listar_detalles_cita', cita_id=cita_id)  # Redirige a la lista de detalles de la cita
    else:
        form = DetalleCitaForm()

    return redirect('Listar_citas')

def listar_detalles_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)  # Obtén la cita relacionada
    detalles_cita = DetalleCita.objects.filter(cita=cita)  # Filtra los detalles de la cita

    return redirect('Listar_citas')

def editar_detalle_cita(request, detalle_cita_id):
    detalle_cita = get_object_or_404(DetalleCita, id=detalle_cita_id)
    pacientes = Paciente.objects.all()   # Obtén el detalle de cita

    if request.method == "POST":
        form = DetalleCitaForm(request.POST, instance=detalle_cita)
        if form.is_valid():
            form.save()
            return redirect('listar_detalles_cita', cita_id=detalle_cita.cita.id)  # Redirige a la lista de detalles de la cita
    else:
        form = DetalleCitaForm(instance=detalle_cita)

    return redirect('Listar_citas')

def historial(request):
    detalles_citas = DetalleCita.objects.select_related('cita').all().order_by('-cita__fecha', '-cita__hora')
    
    # Conteos para estadísticas
    completadas_count = detalles_citas.filter(cita__estatus='completada').count()
    este_mes_count = detalles_citas.filter(cita__fecha__month=timezone.now().month).count()
    
    # Paginación
    paginator = Paginator(detalles_citas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'citas/historial.html', {
        'detalles_citas': page_obj,
        'completadas_count': completadas_count,
        'este_mes_count': este_mes_count,
    })