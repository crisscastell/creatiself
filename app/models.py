from django.db import models

# Rol
class Rol(models.Model):
    nombre_rol = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_rol

# Usuario
class Usuario(models.Model):
    cedula = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(unique=True)
    status = models.BooleanField(default=True)  
    fecha_registro = models.DateField(auto_now_add=True)
    clave = models.CharField(max_length=255)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

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
    parentesco = models.ForeignKey('Parentesco', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# Parentesco
class Parentesco(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

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
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE)
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
