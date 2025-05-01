from django.shortcuts import render
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import *
from .forms import PacienteForm, RelacionPacienteForm
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Pais, Estado, Ciudad
from django.contrib import messages


def crear_pacientes(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Listar_pacientes')  # Cambia según el nombre de tu vista de lista
    else:
        form = PacienteForm()

    # Obtener los datos de las ForeignKey manualmente
    condiciones = Condicion.objects.all()
    antecedentes = AntecedentesPersonales.objects.all()
    paises = Pais.objects.all()
    estados = Estado.objects.all()
    ciudades = Ciudad.objects.all()
    
    return render(request, 'paciente/crear_pacientes.html', {
        'form': form,
        'condiciones': condiciones,
        'antecedentes': antecedentes,
        'paises': paises,
        'estados': estados,
        'ciudades': ciudades
        
    })

def listar_pacientes(request):
    # Obtener todos los pacientes inicialmente
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
    
    # Filtro por tipo de paciente
    tipo_paciente = request.GET.get('tipo_paciente')
    if tipo_paciente:
        pacientes = pacientes.filter(tipo_paciente=tipo_paciente)
    
    # Filtro por sexo
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
        'request': request,  # Importante para mantener los filtros
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
        )
    else:
        relaciones = RelacionPaciente.objects.all()

    paginator = Paginator(relaciones, 10)
    page = request.GET.get('page')
    relaciones_pag = paginator.get_page(page)

    pacientes = Paciente.objects.all()

    return render(request, "paciente/listar_relaciones.html", {
        'relaciones': relaciones_pag,
        'query': query,
        'pacientes': pacientes,
        'form': form  # Por si quieres reutilizarlo en el modal
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