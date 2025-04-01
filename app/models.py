from django.db import models
from django.contrib.auth.models import AbstractUser
# Rol
class Rol(models.Model):
    nombre_rol = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_rol

# Usuario
class Usuario(AbstractUser):
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    rol = models.ForeignKey('Rol', on_delete=models.CASCADE, null=True, blank=True)

# Define related_name únicos para evitar conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='usuario_set',  # related_name único
        related_query_name='usuario',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='usuario_set',  # related_name único
        related_query_name='usuario',
    )

    def __str__(self):
        return self.username

# País
class Pais(models.Model):
    nombre_pais = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_pais

# Estado
class Estado(models.Model):
    nombre_estado = models.CharField(max_length=50)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_estado

# Ciudad
class Ciudad(models.Model):
    nombre_ciudad = models.CharField(max_length=50)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_ciudad

# Representante
class Representante(models.Model):
    cedula = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    edad = models.IntegerField()
    sexo = models.CharField(max_length=10, choices=[('masculino', 'Masculino'), ('femenino', 'Femenino')])
    parentesco = models.CharField(
    max_length=20,
    choices = [
    ('padre', 'Padre'),
    ('madre', 'Madre'),
    ('abuelo', 'Abuelo'),
    ('abuela', 'Abuela'),
    ('bisabuelo', 'Bisabuelo'),
    ('bisabuela', 'Bisabuela'),
    ('hermano', 'Hermano'),
    ('hermana', 'Hermana'),
    ('tio', 'Tío'),
    ('tia', 'Tía'),
    ('primo', 'Primo'),
    ('prima', 'Prima'),
    ('padrino', 'Padrino'),
    ('madrina', 'Madrina'),
    ('sin_parentesco', 'Sin parentesco'),
    ],
    default='sin_parentesco'
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


# Paciente
class Paciente(models.Model):
    tipo_paciente = models.CharField(max_length=10, choices=[('individual', 'Individual'), ('infantil', 'Infantil'), ('pareja', 'Pareja') ])
    cedula = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=50)
    nombre2 = models.CharField(max_length=50, blank=True, null=True)
    apellido = models.CharField(max_length=50)
    apellido2 = models.CharField(max_length=50, blank=True, null=True)
    telefono = models.CharField(max_length=20)
    edad = models.IntegerField()
    sexo = models.CharField(max_length=10, choices=[('masculino', 'Masculino'), ('femenino', 'Femenino')])
    direccion = models.TextField()
    nivel_academico = models.CharField(
    max_length=20,
    choices=[
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria'),
        ('bachillerato', 'Bachillerato'),
        ('tecnico', 'Técnico'),
        ('tecnologo', 'Tecnólogo'),
        ('pregrado', 'Pregrado'),
        ('licenciatura', 'Licenciatura'),
        ('especializacion', 'Especialización'),
        ('maestria', 'Maestría'),
        ('doctorado', 'Doctorado'),
        ('postdoctorado', 'Postdoctorado'),
        ('diplomado', 'Diplomado'),
        ('curso', 'Curso'),
        ('sin_estudios', 'Sin estudios formales'),
    ],
    default='sin_estudios'
    )
    pais = models.ForeignKey('Pais', on_delete=models.CASCADE)
    estado = models.ForeignKey('Estado', on_delete=models.CASCADE)
    ciudad = models.ForeignKey('Ciudad', on_delete=models.CASCADE)
    antecedentes_personales = models.ForeignKey('AntecedentesPersonales', on_delete=models.SET_NULL, null=True, blank=True)
    condicion = models.ForeignKey('Condicion', on_delete=models.SET_NULL, null=True, blank=True)
 
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    # Relación Paciente-Representante
class PacienteRepresentante(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    representante = models.ForeignKey(Representante, on_delete=models.CASCADE)

# Antecedentes Personales
class AntecedentesPersonales(models.Model):
    descripcion = models.TextField()

    def __str__(self):
        return self.descripcion[:50]

# Condición
class Condicion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=100, default="Sin descripción")

    def __str__(self):
        return self.nombre
    
# Cita
class Cita(models.Model):
    hora = models.TimeField()
    fecha = models.DateTimeField()
    modalidad = models.CharField(max_length=50, choices=[('virtual', 'Virtual'), ('presencial', 'Presencial')])
    motivo_consulta = models.TextField()
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cita {self.id} - {self.paciente.nombre}"

# Detalle de Cita
class DetalleCita(models.Model):
    titulo = models.CharField(max_length=100)
    anotacion = models.TextField()
    conclusion = models.TextField()
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

# Relación Paciente-Cita
class PacienteCita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE)

# Empleado
class Empleado(models.Model):
    cedula = models.CharField(max_length=20, unique=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    nombre2 = models.CharField(max_length=50, blank=True, null=True)
    apellido = models.CharField(max_length=50)
    apellido2 = models.CharField(max_length=50, blank=True, null=True)
    cargo = models.CharField(max_length=50)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField()
    fecha_ingreso = models.DateField()
    edad = models.IntegerField()
    sexo = models.CharField(max_length=10, choices=[('masculino', 'Masculino'), ('femenino', 'Femenino')])
    nivel_academico = models.CharField(
    max_length=20,
    choices=[
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria'),
        ('bachillerato', 'Bachillerato'),
        ('tecnico', 'Técnico'),
        ('tecnologo', 'Tecnólogo'),
        ('pregrado', 'Pregrado'),
        ('licenciatura', 'Licenciatura'),
        ('especializacion', 'Especialización'),
        ('maestria', 'Maestría'),
        ('doctorado', 'Doctorado'),
        ('postdoctorado', 'Postdoctorado'),
        ('diplomado', 'Diplomado'),
        ('curso', 'Curso'),
        ('sin_estudios', 'Sin estudios formales'),
    ],
    default='sin_estudios'
    )
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)  

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class RelacionPaciente(models.Model):
    paciente1 = models.ForeignKey(Paciente, related_name='relaciones_como_paciente1', on_delete=models.CASCADE)
    paciente2 = models.ForeignKey(Paciente, related_name='relaciones_como_paciente2', on_delete=models.CASCADE)
    tipo_relacion = models.CharField(max_length=50, choices=[
        ('pareja', 'Pareja'),
        ('familiar', 'Familiar'),
        ('otro', 'Otro'),
    ])
    fecha_relacion = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('paciente1', 'paciente2')  # Evita duplicados

    def __str__(self):
        return f"{self.paciente1} - {self.tipo_relacion} - {self.paciente2}"
