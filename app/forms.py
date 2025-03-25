# forms.py
from django import forms
from .models import *
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
        fields = [
            'cedula', 'usuario', 'nombre', 'nombre2', 'apellido', 'apellido2',
            'cargo', 'direccion', 'telefono', 'fecha_nacimiento', 'fecha_ingreso',
            'edad', 'sexo', 'nivel_academico', 'pais', 'estado', 'ciudad', 'status'
        ]

        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
            'nivel_academico': forms.Select(attrs={'class': 'form-control border-2 border-gray-200 rounded-lg p-3 w-full'})
        }
       
    


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['fecha', 'hora','paciente','modalidad','motivo_consulta']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
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


