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
from datetime import date, timedelta, datetime, time
from django.views import View
from django.views.decorators.http import require_http_methods
from django.utils import timezone

import json

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
    
    # Estadísticas básicas
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
    
    # Obtener todas las citas del mes actual para el calendario
    primer_dia_mes = hoy.replace(day=1)
    ultimo_dia_mes = (primer_dia_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    citas_mes_actual = Cita.objects.filter(
        fecha__range=[primer_dia_mes, ultimo_dia_mes]
    ).select_related('paciente').order_by('fecha', 'hora')
    
    # Formatear citas para el calendario
    citas_calendario = []
    for cita in citas_mes_actual:
        # Asegurarse de que la fecha esté en formato correcto
        fecha_iso = cita.fecha.strftime('%Y-%m-%d')  # Formato ISO: YYYY-MM-DD
        
        # Manejar la hora correctamente
        if isinstance(cita.hora, time):
            hora_str = cita.hora.strftime('%H%M')
        elif isinstance(cita.hora, str):
            # Si es string, quitar posibles ':' y formatear
            hora_str = cita.hora.replace(':', '')[:4]
        else:
            hora_str = '0000'
        
        citas_calendario.append({
            'id': str(cita.id),
            'fecha': fecha_iso,  # Usamos string en formato ISO
            'hora': hora_str,
            'paciente_nombre': f"{cita.paciente.nombre} {cita.paciente.apellido}" if cita.paciente else "Pareja",
            'motivo_consulta': cita.motivo_consulta,
            'modalidad': cita.modalidad
        })
    
    # Estadísticas mensuales para los gráficos
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    año_actual = datetime.now().year
    
    # Consultas presenciales por mes
    presencial_mensual = []
    for mes in range(1, 13):
        count = Cita.objects.filter(
            modalidad='presencial',
            fecha__year=año_actual,
            fecha__month=mes
        ).count()
        presencial_mensual.append(count)
    
    # Consultas virtuales por mes
    virtual_mensual = []
    for mes in range(1, 13):
        count = Cita.objects.filter(
            modalidad='virtual',
            fecha__year=año_actual,
            fecha__month=mes
        ).count()
        virtual_mensual.append(count)
    
    # Datos existentes
    pacientes_destacados = Paciente.objects.all()[:6]
    pacientes = Paciente.objects.all()
    relaciones = RelacionPaciente.objects.all()
    proximas_citas = Cita.objects.filter(fecha__gte=hoy).order_by('fecha', 'hora')[:3]

    context = {
        "usuario_nombre": usuario.first_name,
        "usuario_rol": usuario.rol.nombre_rol,
        "stats": stats,
        "proximas_citas": proximas_citas,
        "pacientes_destacados": pacientes_destacados,
        "pacientes": pacientes,
        "relaciones": relaciones,
        "hoy": hoy,
        "presencial_mensual": presencial_mensual,
        "virtual_mensual": virtual_mensual,
        "meses": meses,
        "citas_json": json.dumps(citas_calendario, default=str)  # Usamos default=str para serializar fechas
    }

    return render(request, "index.html", context)

@require_http_methods(["POST"])
def crear_antecedente(request):
    try:
        # Verificar si es una solicitud AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if request.method == 'POST':
            form = AntecedentesPersonalesForm(request.POST)
            if form.is_valid():
                antecedente = form.save()
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'id': antecedente.id,
                        'descripcion': antecedente.descripcion,
                        'message': 'Antecedente creado exitosamente'
                    })
                else:
                    return redirect('Caracteristicas')
            else:
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': form.errors,
                        'message': 'Error en el formulario'
                    }, status=400)
                else:
                    return render(request, 'paciente/caracteristicas.html', {'form': form})
        
    except Exception as e:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
        else:
            raise e

@require_http_methods(["POST"])
def editar_antecedente(request, id):
    try:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        antecedente = get_object_or_404(AntecedentesPersonales, id=id)
        
        if request.method == 'POST':
            form = AntecedentesPersonalesForm(request.POST, instance=antecedente)
            if form.is_valid():
                antecedente = form.save()
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'id': antecedente.id,
                        'descripcion': antecedente.descripcion,
                        'message': 'Antecedente actualizado exitosamente'
                    })
                else:
                    return redirect('Caracteristicas')
            else:
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': form.errors,
                        'message': 'Error en el formulario'
                    }, status=400)
                else:
                    return render(request, 'paciente/caracteristicas.html', {'form': form})
    
    except Exception as e:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
        else:
            raise e

# 🔹 CONDICIÓN
@require_http_methods(["POST"])
def crear_condicion(request):
    try:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if request.method == 'POST':
            form = CondicionForm(request.POST)
            if form.is_valid():
                condicion = form.save()
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'id': condicion.id,
                        'nombre': condicion.nombre,
                        'message': 'Condición creada exitosamente'
                    })
                else:
                    return redirect('Caracteristicas')
            else:
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': form.errors,
                        'message': 'Error en el formulario'
                    }, status=400)
                else:
                    return render(request, 'paciente/caracteristicas.html', {'form': form})
    
    except Exception as e:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
        else:
            raise e

@require_http_methods(["POST"])
def editar_condicion(request, id):
    try:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        condicion = get_object_or_404(Condicion, id=id)
        
        if request.method == 'POST':
            form = CondicionForm(request.POST, instance=condicion)
            if form.is_valid():
                condicion = form.save()
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'id': condicion.id,
                        'nombre': condicion.nombre,
                        'message': 'Condición actualizada exitosamente'
                    })
                else:
                    return redirect('Caracteristicas')
            else:
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': form.errors,
                        'message': 'Error en el formulario'
                    }, status=400)
                else:
                    return render(request, 'paciente/caracteristicas.html', {'form': form})
    
    except Exception as e:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
        else:
            raise e

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
            pais = form.save()
            
            # Si es petición AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'id': pais.id,
                    'nombre': pais.nombre_pais,
                    'message': '✅ País creado exitosamente'
                })
            
            messages.success(request, "✅ País creado exitosamente")
        else:
            # Si es petición AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors.get_json_data(),
                    'message': '❌ Error al crear el país'
                }, status=400)
            
            # Para peticiones normales
            errors = form.errors.as_data()
            for field, error_list in errors.items():
                for error in error_list:
                    messages.error(request, f"❌ Error en {field}: {error}")
        
        # Redirección para peticiones normales
        return redirect('Tablas')
    
    # Si es GET
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        }, status=405)
    
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
        print("Datos recibidos:", request.POST)  # Depuración
        
        form = EstadoForm(request.POST)
        
        if form.is_valid():
            estado = form.save()
            print("Estado creado:", estado)  # Depuración
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'id': estado.id,
                    'nombre': estado.nombre_estado,
                    'pais_id': estado.pais.id,
                    'message': '✅ Estado creado exitosamente'
                })
            
            messages.success(request, "✅ Estado creado exitosamente")
        else:
            print("Errores de validación:", form.errors)  # Depuración
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors.get_json_data(),
                    'message': '❌ Error al crear el estado',
                    'debug': str(form.errors)
                }, status=400)
            
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ Error en {field}: {error}")
        
        return redirect('Tablas')
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)

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
        # Depuración
        print("Datos recibidos para ciudad:", request.POST)
        
        form = CiudadForm(request.POST)
        
        if form.is_valid():
            ciudad = form.save()
            print("Ciudad creada:", ciudad.nombre_ciudad)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'id': ciudad.id,
                    'nombre': ciudad.nombre_ciudad,
                    'estado_id': ciudad.estado.id,
                    'pais_id': ciudad.estado.pais.id,  # Para dependencias anidadas
                    'message': '✅ Ciudad creada exitosamente'
                })
            
            messages.success(request, "✅ Ciudad creada exitosamente")
        else:
            print("Errores en formulario:", form.errors)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors.get_json_data(),
                    'message': '❌ Error al crear ciudad',
                    'debug': {
                        'estado': request.POST.get('estado'),
                        'nombre_ciudad': request.POST.get('nombre_ciudad')
                    }
                }, status=400)
            
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {field}: {error}")
        
        return redirect('Tablas')
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)
   

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
    # Obtener todos los parámetros de la URL
    pais_query = request.GET.get('pais_query', '')
    estado_query = request.GET.get('estado_query', '')
    ciudad_query = request.GET.get('ciudad_query', '')
    pais_page = request.GET.get('pais_page', 1)
    estado_page = request.GET.get('estado_page', 1)
    ciudad_page = request.GET.get('ciudad_page', 1)

    # Búsqueda y paginación para países
    pais_list = Pais.objects.all().order_by('nombre_pais')
    if pais_query:
        pais_list = pais_list.filter(nombre_pais__icontains=pais_query)
    pais_paginator = Paginator(pais_list, 5)
    paises = pais_paginator.get_page(pais_page)

    # Búsqueda y paginación para estados
    estado_list = Estado.objects.all().order_by('nombre_estado')
    if estado_query:
        estado_list = estado_list.filter(nombre_estado__icontains=estado_query)
    estado_paginator = Paginator(estado_list, 5)
    estados = estado_paginator.get_page(estado_page)

    # Búsqueda y paginación para ciudades
    ciudad_list = Ciudad.objects.all().order_by('nombre_ciudad')
    if ciudad_query:
        ciudad_list = ciudad_list.filter(nombre_ciudad__icontains=ciudad_query)
    ciudad_paginator = Paginator(ciudad_list, 5)
    ciudades = ciudad_paginator.get_page(ciudad_page)

    # Construir contexto con todos los parámetros actuales
    context = {
        'paises': paises,
        'estados': estados,
        'ciudades': ciudades,
        'current_params': {
            'pais_query': pais_query,
            'estado_query': estado_query,
            'ciudad_query': ciudad_query,
            'pais_page': paises.number,
            'estado_page': estados.number,
            'ciudad_page': ciudades.number,
        }
    }
    
    return render(request, "tablas.html", context)

class GetAppointmentCounts(View):
    def get(self, request):
        # Obtener todas las citas futuras
        citas = Cita.objects.filter(fecha__gte=timezone.now().date())
        
        # Crear diccionario de conteos
        counts = {}
        for cita in citas:
            fecha_str = cita.fecha.strftime('%Y-%m-%d')
            counts[fecha_str] = counts.get(fecha_str, 0) + 1
        
        return JsonResponse(counts)