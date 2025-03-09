from django.contrib.auth.decorators import user_passes_test

def es_administrador(user):
    return user.is_authenticated and user.rol.nombre_rol.lower() == "administrador"