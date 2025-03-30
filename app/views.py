from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import *
from .forms import AntecedentesPersonalesForm, CondicionForm
from django.contrib.auth.hashers import make_password



def login(request):
    roles = Rol.objects.all()  # Obtiene todos los roles de la base de datos

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        role = request.POST["role"].strip().lower()  # Normalizamos el rol

        try:
            usuario = Usuario.objects.get(username=username)

            # Si la contraseña no está encriptada, la encriptamos y la guardamos
            if not usuario.password.startswith("pbkdf2_sha256$"):
                usuario.password = make_password(usuario.password)
                usuario.save()

            # Usar authenticate para verificar credenciales
            user = authenticate(request, username=username, password=password)

            if user is None:
                messages.error(request, "Contraseña incorrecta")
                return redirect("Login")

            # Validar el rol del usuario
            if usuario.rol and usuario.rol.nombre_rol.strip().lower() != role:
                messages.error(request, "Rol incorrecto")
                return redirect("Login")

            # Iniciar sesión
            auth_login(request, user)

            # Guardar datos en sesión
            request.session["usuario_id"] = usuario.id
            request.session["usuario_nombre"] = f"{usuario.first_name} {usuario.last_name}"
            request.session["usuario_rol"] = usuario.rol.nombre_rol if usuario.rol else "Sin rol"

            return redirect("Index")

        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado")
            return redirect("Login")

    return render(request, "login.html", {"roles": roles})  # Pasar los roles a la plantilla


def index(request):
    if "usuario_id" not in request.session:
        return redirect("Login")  # Redirigir al login si no está autenticado

    # Obtener datos del usuario autenticado
    usuario_id = request.session.get("usuario_id")
    usuario = Usuario.objects.get(id=usuario_id)  # Obtiene el usuario desde la BD
    
    dias_del_mes = range(1, 32)  # Genera los días del mes
    pacientes_destacados = Paciente.objects.all()[:5]  # Obtiene los primeros 5 pacientes

    context = {
        "usuario_nombre": usuario.first_name,  # Pasar el nombre del usuario al template
        "usuario_rol": usuario.rol.nombre_rol,  # Pasar el rol del usuario al template
        "dias_del_mes": dias_del_mes,
        "pacientes": pacientes_destacados
    }

    return render(request, "index.html", context)  # Enviar el contexto al template


def crear_antecedente(request):
    if request.method == 'POST':
        form = AntecedentesPersonalesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Caracteristicas')  # Nombre de la URL para listar
    else:
        form = AntecedentesPersonalesForm()
    
    return render(request, 'paciente/caracteristicas.html', {'form': form})

def editar_antecedente(request, id):
    antecedente = get_object_or_404(AntecedentesPersonales, id=id)
    if request.method == 'POST':
        form = AntecedentesPersonalesForm(request.POST, instance=antecedente)
        if form.is_valid():
            form.save()
            return redirect('Caracteristicas')  # Redirige a la lista de antecedentes
    else:
        form = AntecedentesPersonalesForm(instance=antecedente)
    
    return render(request, 'paciente/caracteristicas.html', {'form': form})

# 🔹 CONDICIÓN
def crear_condicion(request):
    if request.method == 'POST':
        form = CondicionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Caracteristicas')
    else:
        form = CondicionForm()

    return render(request, 'paciente/caracteristicas.html', {'form': form})

def editar_condicion(request, id):
    condicion = get_object_or_404(Condicion, id=id)
    if request.method == 'POST':
        form = CondicionForm(request.POST, instance=condicion)
        if form.is_valid():
            form.save()
            return redirect('Caracteristicas')
    else:
        form = CondicionForm(instance=condicion)
    
    return render(request, 'paciente/caracteristicas.html', {'form': form})


def pacientes(request):
    return render(request, "pacientes.html")

def citas(request):
    return render(request, "citas.html")

def tablas(request):
    return render(request, "tablas.html")

def caracteristicas(request):
    # Obtener todos los antecedentes personales
    antecedentes = AntecedentesPersonales.objects.all()

    # Obtener todas las condiciones
    condiciones = Condicion.objects.all()
    
    # Paginación para antecedentes
    paginator_antecedentes = Paginator(antecedentes, 5)  # 5 antecedentes por página
    page_number_antecedentes = request.GET.get('page_antecedentes')  # Obtener el número de página para antecedentes desde la URL
    page_obj_antecedentes = paginator_antecedentes.get_page(page_number_antecedentes)  # Obtener la página actual de antecedentes

    # Paginación para condiciones
    paginator_condiciones = Paginator(condiciones, 5)  # 5 condiciones por página
    page_number_condiciones = request.GET.get('page_condiciones')  # Obtener el número de página para condiciones desde la URL
    page_obj_condiciones = paginator_condiciones.get_page(page_number_condiciones)  # Obtener la página actual de condiciones

    # Manejo del formulario de antecedentes
    if request.method == 'POST' and 'antecedente' in request.POST:
        form_antecedente = AntecedentesPersonalesForm(request.POST)
        if form_antecedente.is_valid():
            form_antecedente.save()
            return redirect('Caracteristicas')  # Asegúrate de que el nombre de la URL sea correcto
    else:
        form_antecedente = AntecedentesPersonalesForm()  # Form vacío para mostrar en el template
    
    # Manejo del formulario de condiciones
    if request.method == 'POST' and 'condicion' in request.POST:
        form_condicion = CondicionForm(request.POST)
        if form_condicion.is_valid():
            form_condicion.save()
            return redirect('Caracteristicas')  # Asegúrate de que el nombre de la URL sea correcto
    else:
        form_condicion = CondicionForm()  # Form vacío para mostrar en el template
    
    # Renderizar la página
    return render(request, 'paciente/caracteristicas.html', {
        'form_antecedente': form_antecedente, 
        'form_condicion': form_condicion,  # Pasar el formulario de condiciones
        'page_obj_antecedentes': page_obj_antecedentes,  # Pasar solo el paginador de antecedentes
        'page_obj_condiciones': page_obj_condiciones,  # Pasar solo el paginador de condiciones
    })