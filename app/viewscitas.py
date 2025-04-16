from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from app.models import Cita, DetalleCita, Paciente
from app.forms import CitaForm, DetalleCitaForm
from django.contrib import messages

def crear_cita(request):
    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Listar_citas')  # Ajusta según el nombre de tu vista de lista
    else:
        form = CitaForm()

    # Obtener los datos de las ForeignKey manualmente
    pacientes = Paciente.objects.all()

    return render(request, 'citas/crear_cita.html', {
        'form': form,
        'pacientes': pacientes
    })

def listar_citas(request):
    citas = Cita.objects.all()
    
    return render(request, 'citas/listar_citas.html', {'citas': citas})

def editar_cita(request, id):
    cita = get_object_or_404(Cita, id=id)
    
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, "Cita actualizada correctamente")
        else:
            messages.error(request, "Error al actualizar la cita")

    return redirect('Listar_citas')

def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    
    if request.method == "POST":
        cita.delete()
        return redirect('Listar_citas')  
    
    return render(request, 'citas/eliminar_cita.html', {'cita': cita})

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
