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
    pacientes = Paciente.objects.all()

    query = request.GET.get('q', '')  # Captura el valor de búsqueda desde la URL
    pacientes_list = Paciente.objects.all()

    # Filtrar por nombre o cédula
    if query:
        pacientes_list = pacientes_list.filter(
            Q(cedula__icontains=query) | 
            Q(nombre__icontains=query) | 
            Q(apellido__icontains=query)
        )

    # Paginación (15 pacientes por página)
    paginator = Paginator(pacientes_list, 15)
    page_number = request.GET.get('page')
    pacientes = paginator.get_page(page_number)

    return render(request, 'paciente/listar_pacientes.html', {'pacientes': pacientes, 'query': query})

def editar_paciente(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('Listar_pacientes') 
    else:
        form = PacienteForm(instance=paciente)

    condiciones = Condicion.objects.all()
    antecedentes = AntecedentesPersonales.objects.all()
    paises = Pais.objects.all()
    estados = Estado.objects.all()
    ciudades = Ciudad.objects.all()
    
    return render(request, 'paciente/listar_pacientes.html', {
        'form': form,
        'paciente': paciente,
        'condiciones': condiciones,
        'antecedentes': antecedentes,
        'paises': paises,
        'estados': estados,
        'ciudades': ciudades
    })

def crear_relacion(request):
    if request.method == "POST":
        form = RelacionPacienteForm(request.POST)
        if form.is_valid():
            paciente1 = form.cleaned_data["paciente1"]
            paciente2 = form.cleaned_data["paciente2"]

            if paciente1 == paciente2:
                messages.error(request, "No puedes relacionar un paciente consigo mismo.")
                return redirect("Crear_relacion")

            # Verificar si la relación ya existe en cualquier orden
            if RelacionPaciente.objects.filter(
                paciente1=paciente1, paciente2=paciente2
            ).exists() or RelacionPaciente.objects.filter(
                paciente1=paciente2, paciente2=paciente1
            ).exists():
                messages.warning(request, "Estos pacientes ya tienen una relación registrada.")
                return redirect("Crear_relacion")

            form.save()
            messages.success(request, "Relación creada correctamente.")
            return redirect("Listar_relaciones")
    else:
        form = RelacionPacienteForm()

    return render(request, "paciente/crear_relacion.html", {"form": form})

def lista_relaciones(request):
    relaciones = RelacionPaciente.objects.select_related("paciente1", "paciente2").all()
    return render(request, "paciente/listar_relaciones.html", {"relaciones": relaciones})