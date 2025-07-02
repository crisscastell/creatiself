from django.shortcuts import render
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Q
from .models import *
from .forms import PacienteForm, RelacionPacienteForm, RepresentanteForm
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Pais, Estado, Ciudad
from django.contrib import messages
from django.views.decorators.http import require_POST
import json
from django.core.serializers.json import DjangoJSONEncoder



def crear_pacientes(request, representante_id=None):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)
            
            # Validar que pacientes infantiles tengan un representante
            if paciente.tipo_paciente == 'infantil' and not request.POST.get('representante_id'):
                form.add_error(None, "Los pacientes infantiles deben tener un representante")
            else:
                paciente.save()
                
                # Si hay un representante_id, crear la relación
                representante_id = request.POST.get('representante_id')
                if representante_id:
                    PacienteRepresentante.objects.create(
                        paciente=paciente,
                        representante_id=representante_id
                    )
            
            # Obtener los datos actuales para los selects y volver a renderizar la página
            condiciones = Condicion.objects.all()
            antecedentes = AntecedentesPersonales.objects.all()
            paises = Pais.objects.all()
            estados = Estado.objects.all()
            ciudades = Ciudad.objects.all()
            return redirect('Listar_pacientes')
    else:
        form = PacienteForm()

    # Obtener los datos para los selects
    condiciones = Condicion.objects.all()
    antecedentes = AntecedentesPersonales.objects.all()
    paises = Pais.objects.all()
    estados = Estado.objects.all()
    ciudades = Ciudad.objects.all()

    total_pacientes = Paciente.objects.count()
    pacientes_hombres = Paciente.objects.filter(sexo='masculino').count()
    pacientes_mujeres = Paciente.objects.filter(sexo='femenino').count()
    pacientes_infantiles = Paciente.objects.filter(tipo_paciente='infantil').count()
    pacientes_adultos = Paciente.objects.filter(tipo_paciente='individual').count()
    
    # Estadísticas por condición (top 5)
    condiciones_stats = Paciente.objects.values('condicion__nombre').annotate(
        total=Count('condicion')
    ).order_by('-total')[:5]

    return render(request, 'paciente/crear_pacientes.html', {
        'form': form,
        'condiciones': condiciones,
        'antecedentes': antecedentes,
        'paises': paises,
        'estados': estados,
        'ciudades': ciudades,
        'representante_id': representante_id,
        'stats_data': json.dumps({
            'total': total_pacientes,
            'hombres': pacientes_hombres,
            'mujeres': pacientes_mujeres,
            'infantiles': pacientes_infantiles,
            'adultos': pacientes_adultos,
            'condiciones': list(condiciones_stats),
        }, cls=DjangoJSONEncoder)
    })

def listar_pacientes(request):
    pacientes = Paciente.objects.all()
    
    # Búsqueda
    query = request.GET.get('q', '')
    if query:
        pacientes = pacientes.filter(
            Q(cedula__icontains=query) |
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(telefono__icontains=query)
        )
    
    # Filtros
    tipo_paciente = request.GET.get('tipo_paciente')
    if tipo_paciente:
        pacientes = pacientes.filter(tipo_paciente=tipo_paciente)
    
    sexo = request.GET.get('sexo')
    if sexo:
        pacientes = pacientes.filter(sexo=sexo)
    
    # Paginación
    paginator = Paginator(pacientes, 15)
    page_number = request.GET.get('page')
    pacientes_paginados = paginator.get_page(page_number)
    
    context = {
        'pacientes': pacientes_paginados,
        'query': query,
        'condiciones': Condicion.objects.all(),
        'antecedentes': AntecedentesPersonales.objects.all(),
        'paises': Pais.objects.all(),
        'estados': Estado.objects.all(),
        'ciudades': Ciudad.objects.all(),
    }
    return render(request, 'paciente/listar_pacientes.html', context)

def editar_paciente(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, "Paciente actualizado correctamente")
            return redirect('Listar_pacientes')
        else:
            messages.error(request, "Error al actualizar el paciente")
    
    return redirect('Listar_pacientes')

def listar_relaciones(request):
    # Procesar creación de relación si el método es POST
    if request.method == "POST":
        form = RelacionPacienteForm(request.POST)
        if form.is_valid():
            paciente1 = form.cleaned_data["paciente1"]
            paciente2 = form.cleaned_data["paciente2"]

            if paciente1 == paciente2:
                messages.error(request, "No puedes relacionar un paciente consigo mismo.")
            elif RelacionPaciente.objects.filter(
                Q(paciente1=paciente1, paciente2=paciente2) |
                Q(paciente1=paciente2, paciente2=paciente1)
            ).exists():
                messages.warning(request, "Estos pacientes ya tienen una relación registrada.")
            else:
                form.save()
                messages.success(request, "Relación creada correctamente.")
                return redirect("Listar_relaciones")  # Redirigir para evitar reenvío del formulario
        else:
            messages.error(request, "Formulario inválido. Verifica los campos.")
    else:
        form = RelacionPacienteForm()

    # Listado y búsqueda de relaciones
    query = request.GET.get('q')
    if query:
        relaciones = RelacionPaciente.objects.filter(
            Q(paciente1__nombre__icontains=query) |
            Q(paciente2__nombre__icontains=query)
        ).distinct()
    else:
        relaciones = RelacionPaciente.objects.all()

    # Estadísticas de relaciones
    total_relaciones = relaciones.count()
    relaciones_pareja = relaciones.filter(tipo_relacion='pareja')
    relaciones_familiares = relaciones.filter(tipo_relacion='familiar')
    relaciones_otros = relaciones.filter(tipo_relacion='otro')


    # Paginación
    paginator = Paginator(relaciones, 10)
    page = request.GET.get('page')
    relaciones_pag = paginator.get_page(page)

    pacientes = Paciente.objects.all()

    return render(request, "paciente/listar_relaciones.html", {
        'relaciones': relaciones_pag,
        'query': query,
        'pacientes': pacientes,
        'form': form,
        # Estadísticas
        'total_relaciones': total_relaciones,
        'relaciones_pareja': relaciones_pareja,
        'relaciones_familiares': relaciones_familiares,
        'relaciones_otros': relaciones_otros,
        
    })


def editar_relacion(request, id):
    relacion = get_object_or_404(RelacionPaciente, id=id)
    
    if request.method == 'POST':
        form = RelacionPacienteForm(request.POST, instance=relacion)
        if form.is_valid():
            form.save()
            messages.success(request, "relacion actualizado correctamente")
            return redirect('Listar_relaciones')
        else:
            messages.error(request, "Error al actualizar el relacion")
    
    return redirect('Listar_relaciones')

@require_POST
def crear_representante(request):
    form = RepresentanteForm(request.POST)
    if form.is_valid():
        representante = form.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Respuesta para AJAX
            return JsonResponse({
                'success': True,
                'representante': {
                    'id': representante.id,
                    'nombre': representante.nombre,
                    'apellido': representante.apellido,
                    'cedula': representante.cedula,
                    'parentesco': representante.get_parentesco_display()
                }
            })
        else:
            # Redirección normal para POST tradicional
            return redirect('Crear_pacientes')
    
    # Si el formulario no es válido
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'errors': form.errors.as_json()
        }, status=400)
    else:
        return redirect('Crear_pacientes')


def listar_representantes(request):
    query = request.GET.get('q', '')
    representantes = Representante.objects.all()
    
    if query:
        representantes = representantes.filter(
            Q(nombre__icontains=query) | 
            Q(apellido__icontains=query) |
            Q(cedula__icontains=query) |
            Q(telefono__icontains=query)
        )
    
    page = request.GET.get('page', 1)
    paginator = Paginator(representantes, 6)  # 6 representantes por página
    
    try:
        representantes_page = paginator.page(page)
    except PageNotAnInteger:
        representantes_page = paginator.page(1)
    except EmptyPage:
        representantes_page = paginator.page(paginator.num_pages)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Solo devolver el contenido necesario para AJAX
        context = {
            'representantes': representantes_page,
            'page_obj': representantes_page,
        }
        return render(request, 'paciente/listar_representantes.html', context)
    
    # Vista normal para GET inicial
    return render(request, 'listar_representantes.html', {'representantes': representantes_page})
    