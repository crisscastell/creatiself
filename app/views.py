from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import *
from .forms import AntecedentesPersonalesForm, CondicionForm, PaisForm, EstadoForm, CiudadForm
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_POST
from datetime import date, timedelta


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

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

    return render(request, "login.html")  # Ya no se pasan roles

def index(request):
    if "usuario_id" not in request.session:
        return redirect("Login")

    # Obtener datos del usuario autenticado
    usuario_id = request.session.get("usuario_id")
    usuario = Usuario.objects.get(id=usuario_id)
    
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    
    # Estadísticas
    stats = {
        'citas_hoy': Cita.objects.filter(fecha=hoy).count(),
        'citas_semana': Cita.objects.filter(fecha__range=[inicio_semana, hoy]).count(),
        'total_pacientes': Paciente.objects.count(),
        'distribucion_sexo': {
            'masculino': Paciente.objects.filter(sexo='masculino').count(),
            'femenino': Paciente.objects.filter(sexo='femenino').count(),
        },
        'distribucion_modalidad': {
            'virtual': Cita.objects.filter(modalidad='virtual').count(),
            'presencial': Cita.objects.filter(modalidad='presencial').count(),
        }
    }
    
    # Datos existentes
    pacientes_destacados = Paciente.objects.all()[:5]
    proximas_citas = Cita.objects.filter(fecha__gte=hoy).order_by('fecha', 'hora')[:3]

    context = {
        "usuario_nombre": usuario.first_name,
        "usuario_rol": usuario.rol.nombre_rol,
        "stats": stats,
        "proximas_citas": proximas_citas,
        "pacientes": pacientes_destacados,
        "hoy": hoy
    }

    return render(request, "index.html", context)

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

@require_POST
def ocultar_antecedente(request, pk):
    antecedente = get_object_or_404(AntecedentesPersonales, pk=pk)
    antecedente.activo = False
    antecedente.save()
    return redirect('Caracteristicas') 

# Vista para ocultar condición
@require_POST
def ocultar_condicion(request, pk):
    condicion = get_object_or_404(Condicion, pk=pk)
    condicion.activo = False
    condicion.save()
    return redirect('Caracteristicas') 

def caracteristicas(request):
    # Obtener todos los antecedentes personales
    condiciones = Condicion.objects.filter(activo=True) 
    antecedentes = AntecedentesPersonales.objects.filter(activo=True) 
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

def crear_pais(request):
    if request.method == 'POST':
        form = PaisForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ País creado exitosamente")
        else:
            errors = form.errors.as_data()
            for field, error_list in errors.items():
                for error in error_list:
                    messages.error(request, f"❌ Error en {field}: {error}")
        return redirect('Tablas')
    
    # Si es GET, deberías mostrar el formulario, pero según tu flujo rediriges
    return redirect('Tablas')

def editar_pais(request, id):
    pais = get_object_or_404(Pais, id=id)
    
    if request.method == 'POST':
        form = PaisForm(request.POST, instance=pais)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ País actualizado correctamente")
        else:
            messages.error(request, "❌ Error al actualizar el país")
        return redirect('Tablas')
    
    # Para GET podrías mostrar formulario de edición
    return redirect('Tablas')

# Views para Estado
def crear_estado(request):
    if request.method == 'POST':
        form = EstadoForm(request.POST)
        if form.is_valid():
            estado = form.save()
            messages.success(request, f"✅ Estado {estado.nombre_estado} creado exitosamente")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ Error en {field}: {error}")
        return redirect('Tablas')
    
    return redirect('Tablas')

def editar_estado(request, id):
    estado = get_object_or_404(Estado, id=id)
    
    if request.method == 'POST':
        form = EstadoForm(request.POST, instance=estado)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Estado actualizado correctamente")
        else:
            messages.error(request, "❌ Error al actualizar el estado")
        return redirect('Tablas')
    
    return redirect('Tablas')

# Views para Ciudad
def crear_ciudad(request):
    if request.method == 'POST':
        form = CiudadForm(request.POST)
        if form.is_valid():
            ciudad = form.save()
            messages.success(request, f"✅ Ciudad {ciudad.nombre_ciudad} creada exitosamente")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ Error en {field}: {error}")
        return redirect('Tablas')
    
    return redirect('Tablas')

def editar_ciudad(request, id):
    ciudad = get_object_or_404(Ciudad, id=id)
    
    if request.method == 'POST':
        form = CiudadForm(request.POST, instance=ciudad)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Ciudad actualizada correctamente")
        else:
            messages.error(request, "❌ Error al actualizar la ciudad")
        return redirect('Tablas')
    
    return redirect('Tablas')

def tablas(request):
    paises = Pais.objects.all()
    estados = Estado.objects.all()
    ciudades = Ciudad.objects.all()
    
    return render(request, "tablas.html", {
        'paises': paises, 
        'estados': estados, 
        'ciudades': ciudades
    })
