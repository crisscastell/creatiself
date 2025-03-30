# forms.py
from django import forms
from .models import *
from django.contrib.auth.forms import UserChangeForm
from django import forms
from .models import Cita

class AntecedentesPersonalesForm(forms.ModelForm):
    class Meta:
        model = AntecedentesPersonales
        fields = '__all__'

class CondicionForm(forms.ModelForm):
    class Meta:
        model = Condicion
        fields = '__all__'

class PaisForm(forms.ModelForm):
    class Meta:
        model = Pais
        fields = ['nombre_pais']
        widgets = {
            'nombre_pais': forms.TextInput(attrs={
                'class': 'form-control border-2 border-gray-200 rounded-lg p-3 w-full focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all',
                'placeholder': 'Ingrese el nombre del país'
            })
        }

class EstadoForm(forms.ModelForm):
    class Meta:
        model = Estado
        fields = ['nombre_estado', 'pais']
        widgets = {
            'nombre_estado': forms.TextInput(attrs={
                'class': 'form-control border-2 border-gray-200 rounded-lg p-3 w-full focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all',
                'placeholder': 'Ingrese el nombre del estado'
            }),
            'pais': forms.Select(attrs={
                'class': 'form-control border-2 border-gray-200 rounded-lg p-3 w-full focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all'
            })
        }

class CiudadForm(forms.ModelForm):
    class Meta:
        model = Ciudad
        fields = ['nombre_ciudad', 'estado']
        widgets = {
            'nombre_ciudad': forms.TextInput(attrs={
                'class': 'form-control border-2 border-gray-200 rounded-lg p-3 w-full focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all',
                'placeholder': 'Ingrese el nombre de la ciudad'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control border-2 border-gray-200 rounded-lg p-3 w-full focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all'
            })
        }

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'  # Usa todos los campos o especifica campos individuales si es necesario
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'rows': 3}),
            'motivo_consulta': forms.Textarea(attrs={'rows': 4}),
        }

        
class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = '__all__' 

        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
            'nivel_academico': forms.Select(attrs={'class': 'form-control border-2 border-gray-200 rounded-lg p-3 w-full'})
        }
       
class UsuarioForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'cedula', 'telefono', 'rol', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
        }  


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['hora', 'fecha', 'modalidad', 'motivo_consulta', 'paciente']
        widgets = {
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'modalidad': forms.Select(attrs={'class': 'form-control'}),
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'paciente': forms.Select(attrs={'class': 'form-control'}),
        }


class DetalleCitaForm(forms.ModelForm):
    class Meta:
        model = DetalleCita
        fields = ['titulo', 'anotacion', 'conclusion', 'cita']  # Campos del modelo

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personaliza los campos si es necesario
        self.fields['titulo'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Título'})
        self.fields['anotacion'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Anotación', 'rows': 3})
        self.fields['conclusion'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Conclusión', 'rows': 3})
        self.fields['cita'].widget.attrs.update({'class': 'form-control'})


