from django.shortcuts import render
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import *
from .forms import PacienteForm
from django.shortcuts import render, get_object_or_404
from .models import Pais, Estado, Ciudad


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
