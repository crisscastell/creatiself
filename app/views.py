from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import requests
from django.http import JsonResponse
from .models import *
from .forms import AntecedentesPersonalesForm, CondicionForm
from .serializers import PaisSerializer, EstadoSerializer, CiudadSerializer
from rest_framework import generics

def crear_antecedente(request):
    if request.method == 'POST':
        form = AntecedentesPersonalesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Listar_antecedentes')  # Nombre de la URL para listar
    else:
        form = AntecedentesPersonalesForm()
    
    return render(request, 'tablas/antecedentes_personales.html', {'form': form})

def listar_antecedentes(request):
    antecedentes = AntecedentesPersonales.objects.all()
    return render(request, 'tablas/antecedentes_personales.html', {'antecedentes': antecedentes})

def editar_antecedente(request, id):
    antecedente = get_object_or_404(AntecedentesPersonales, id=id)
    if request.method == 'POST':
        form = AntecedentesPersonalesForm(request.POST, instance=antecedente)
        if form.is_valid():
            form.save()
            return redirect('Listar_antecedentes')  # Redirige a la lista de antecedentes
    else:
        form = AntecedentesPersonalesForm(instance=antecedente)
    
    return render(request, 'tablas/editar_antecedente.html', {'form': form})

def eliminar_antecedente(request, id):
    antecedente = get_object_or_404(AntecedentesPersonales, id=id)
    if request.method == 'POST':
        antecedente.delete()
        return redirect('Listar_antecedentes')  # Redirige tras eliminar

    return render(request, 'tablas/confirmar_eliminar.html', {'antecedente': antecedente})


# 🔹 CONDICIÓN
def crear_condicion(request):
    if request.method == 'POST':
        form = CondicionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Listar_condiciones')
    else:
        form = CondicionForm()

    return render(request, 'tablas/condicion.html', {'form': form})

def listar_condiciones(request):
    condiciones = Condicion.objects.all()
    return render(request, 'tablas/condicion.html', {'condiciones': condiciones})

def editar_condicion(request, id):
    condicion = get_object_or_404(Condicion, id=id)
    if request.method == 'POST':
        form = CondicionForm(request.POST, instance=condicion)
        if form.is_valid():
            form.save()
            return redirect('Listar_condiciones')
    else:
        form = CondicionForm(instance=condicion)
    
    return render(request, 'tablas/editar_condicion.html', {'form': form})

def eliminar_condicion(request, id):
    condicion = get_object_or_404(Condicion, id=id)
    if request.method == 'POST':
        condicion.delete()
        return redirect('Listar_condiciones')

    return render(request, 'tablas/confirmar_eliminar.html', {'objeto': condicion, 'tipo': 'Condición'})

# Create your views here.

def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        role = request.POST["role"]

        try:
            # Verificar si el usuario existe en la base de datos
            usuario = Usuario.objects.get(correo=username)

            # Validar la contraseña manualmente (si la contraseña está almacenada en texto plano)
            if usuario.clave != password:
                messages.error(request, "Contraseña incorrecta")
                return redirect("Login")

            # Validar el rol del usuario
            if usuario.rol.nombre_rol.lower() != role.lower():
                messages.error(request, "Rol incorrecto")
                return redirect("Login")

            # Autenticar y redirigir
            request.session["usuario_id"] = usuario.id
            request.session["usuario_nombre"] = f"{usuario.nombre} {usuario.apellido}"
            request.session["usuario_rol"] = usuario.rol.nombre_rol

            return redirect("Index")

        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado")
            return redirect("login")

    return render(request, "login.html")


def index(request):
    if "usuario_id" not in request.session:
        return redirect("Login")  # Redirigir al login si no está autenticado

    # Obtener datos del usuario autenticado
    usuario_id = request.session.get("usuario_id")
    usuario = Usuario.objects.get(id=usuario_id)  # Obtiene el usuario desde la BD
    
    dias_del_mes = range(1, 32)  # Genera los días del mes
    pacientes_destacados = Paciente.objects.all()[:5]  # Obtiene los primeros 5 pacientes

    context = {
        "usuario_nombre": usuario.nombre,  # Pasar el nombre del usuario al template
        "usuario_rol": usuario.rol.nombre_rol,  # Pasar el rol del usuario al template
        "dias_del_mes": dias_del_mes,
        "pacientes": pacientes_destacados
    }

    return render(request, "index.html", context)  # Enviar el contexto al template


def pacientes(request):
    return render(request, "pacientes.html")

def citas(request):
    return render(request, "citas.html")

def tablas(request):
    return render(request, "tablas.html")


def obtener_paises(request):
    response = requests.get('https://restcountries.com/v3.1/all')
    paises = response.json()
    print(type(paises))  # Verifica el tipo de paises
    print(paises) 
    if response.status_code == 200:
        paises = response.json()
    else:
        print(f"Error al obtener datos de la API: {response.status_code}")
        return JsonResponse({'error': 'No se pudo obtener la lista de países'}, status=500)

    # Depuración: muestra qué países se están obteniendo
    print(paises[:5])  # Esto muestra los primeros 5 países para verificar la estructura

    # Si la API está respondiendo correctamente, agregamos los países a la base de datos
    for pais in paises:
        nombre_pais = pais.get('name', {}).get('common', '')
        if nombre_pais and not Pais.objects.filter(nombre_pais=nombre_pais).exists():
            nuevo_pais = Pais.objects.create(nombre_pais=nombre_pais)
            print(f"Pais creado: {nuevo_pais.nombre_pais}")
    
    paises = Pais.objects.all()
    return JsonResponse([{'id': pais.id, 'nombre_pais': pais.nombre_pais} for pais in paises], safe=False)

def obtener_estados(request):
    pais_id = request.GET.get('pais_id')
    estados = Estado.objects.filter(pais_id=pais_id)
    return JsonResponse([{'id': estado.id, 'nombre': estado.nombre_estado} for estado in estados], safe=False)

def obtener_ciudades(request):
    estado_id = request.GET.get('estado_id')
    ciudades = Ciudad.objects.filter(estado_id=estado_id)
    return JsonResponse([{'id': ciudad.id, 'nombre': ciudad.nombre_ciudad} for ciudad in ciudades], safe=False)