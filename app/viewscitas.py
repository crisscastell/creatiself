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
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

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
            Q(paciente__identificacion__icontains=query) |
            Q(fecha__icontains=query) |
            Q(hora__icontains=query) |
            Q(modalidad__icontains=query) |
            Q(motivo_consulta__icontains=query) |
            Q(relacion__paciente1__nombre__icontains=query) |
            Q(relacion__paciente1__apellido__icontains=query) |
            Q(relacion__paciente2__nombre__icontains=query) |
            Q(relacion__paciente2__apellido__icontains=query)
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
    
    # Calcular estadísticas
    hoy = timezone.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    
    # Total de citas
    total_citas = Cita.objects.count()
    
    # Citas por estado
    citas_pendientes = Cita.objects.filter(estatus='pendiente').count()
    citas_completadas = Cita.objects.filter(estatus='completada').count()
    citas_canceladas = Cita.objects.filter(estatus='cancelada').count()
    
    # Citas por modalidad
    citas_virtuales = Cita.objects.filter(modalidad='virtual').count()
    citas_presenciales = Cita.objects.filter(modalidad='presencial').count()
    
    # Citas por tipo (individual vs relación)
    citas_individuales = Cita.objects.filter(paciente__isnull=False).count()
    citas_relaciones = Cita.objects.filter(relacion__isnull=False).count()
    
    # Citas para hoy y esta semana
    citas_hoy = Cita.objects.filter(fecha=hoy).count()
    citas_semana = Cita.objects.filter(fecha__range=[inicio_semana, fin_semana]).count()
    
    # Manejar la alerta de creación exitosa
    mostrar_alerta = request.session.pop('mostrar_alerta', False) if 'mostrar_alerta' in request.session else False
    
    return render(request, 'citas/listar_citas.html', {
        'citas': citas,
        'mostrar_alerta': mostrar_alerta,
        'query': query,  # Pasar el término de búsqueda al template
        
        # Estadísticas
        'citas_pendientes': citas_pendientes,
        'citas_completadas': citas_completadas,
        'citas_canceladas': citas_canceladas,
        'citas_virtuales': citas_virtuales,
        'citas_presenciales': citas_presenciales,
        'citas_relaciones': citas_relaciones,
        'citas_hoy': citas_hoy,
        'citas_semana': citas_semana,
        'citas_individuales': citas_individuales,
        'total_citas': total_citas,
        
        # Rangos de fecha para el resumen
        'hoy': hoy,
        'inicio_semana': inicio_semana,
        'fin_semana': fin_semana,
    })


def editar_cita(request, id):
    cita = get_object_or_404(Cita, id=id)
    
    if request.method == 'POST':
        # Añadir editing=True para desactivar validación de fechas pasadas
        form = CitaForm(request.POST, instance=cita, editing=True)
        
        if form.is_valid():
            cita_editada = form.save(commit=False)
            
            # Corrección: 'tipo_cita' (no 'tipo_cita')
            if cita.paciente:
                cita_editada.tipo_cita = 'paciente'  # Corregido el typo
                cita_editada.paciente = cita.paciente
                cita_editada.relacion = None
            elif cita.relacion:
                cita_editada.tipo_cita = 'relacion'
                cita_editada.relacion = cita.relacion
                cita_editada.paciente = None
            
            cita_editada.save()
            messages.success(request, "Cita actualizada correctamente")
            return redirect('Listar_citas')
        else:
            for campo, errores in form.errors.items():
                for error in errores:
                    messages.error(request, f"{campo}: {error}")
            
            request.session['editar_cita_form_errors'] = form.errors
            request.session['editar_cita_form_data'] = request.POST
            return redirect('Listar_citas')
    
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
    pendientes_count = detalles_citas.filter(cita__estatus='pendiente').count()
    este_mes_count = detalles_citas.filter(cita__fecha__month=timezone.now().month).count()
    
    # Paginación
    paginator = Paginator(detalles_citas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'citas/historial.html', {
        'detalles_citas': page_obj,
        'completadas_count': completadas_count,
        'este_mes_count': este_mes_count,
        'pendientes_count':pendientes_count
    })

def api_citas(request):
    year = int(request.GET.get('year'))
    month = int(request.GET.get('month'))
    
    citas = Cita.objects.filter(
        fecha__year=year,
        fecha__month=month
    ).select_related('paciente')
    
    citas_data = []
    for cita in citas:
        citas_data.append({
            'fecha': cita.fecha.isoformat(),
            'hora': cita.hora.strftime('%H%M') if hasattr(cita.hora, 'strftime') else cita.hora,
            'paciente_nombre': f"{cita.paciente.nombre} {cita.paciente.apellido}" if cita.paciente else "Pareja",
            'motivo_consulta': cita.motivo_consulta,
            'modalidad': cita.modalidad
        })
    
    return JsonResponse(citas_data, safe=False)