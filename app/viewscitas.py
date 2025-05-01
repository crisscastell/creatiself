from django.shortcuts import render, redirect, get_object_or_404,  redirect
from django.http import HttpResponse
from app.models import Cita, DetalleCita, Paciente
from app.forms import CitaForm, DetalleCitaForm
from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse 

def crear_cita(request):
    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Listar_citas')
    else:
        form = CitaForm()

    return render(request, 'citas/crear_cita.html', {
        'form': form,
    })

def listar_citas(request):
    citas = Cita.objects.all()
    
    return render(request, 'citas/listar_citas.html', {'citas': citas})

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
