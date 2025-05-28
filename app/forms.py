# forms.py
from django import forms
from .models import *
from django.contrib.auth.forms import UserChangeForm
from django import forms
from .models import Cita
from datetime import datetime, date, time, timedelta
import datetime as dt

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
            'tipo_paciente': forms.Select(choices=[('individual', 'Individual'), ('infantil', 'Infantil')]),
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
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Nueva contraseña (dejar en blanco para no cambiar)'
        }),
        required=False,
        label="Nueva contraseña"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Confirmar nueva contraseña'
        }),
        required=False,
        label="Confirmar contraseña"
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'rol', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre de usuario'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Correo electrónico'
            }),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rol'].queryset = Rol.objects.all()
        
        # Eliminamos el campo password original del formulario
        if 'password' in self.fields:
            del self.fields['password']

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password or confirm_password:
            if new_password != confirm_password:
                self.add_error('confirm_password', "Las contraseñas no coinciden")
            elif len(new_password) < 8:
                self.add_error('new_password', "La contraseña debe tener al menos 8 caracteres")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        
        if new_password:
            user.set_password(new_password)
        
        if commit:
            user.save()
            self.save_m2m()
        
        return user

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['paciente', 'pareja', 'hora', 'fecha', 'modalidad', 'motivo_consulta']
        widgets = {
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'modalidad': forms.Select(attrs={'class': 'form-control'}),
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'pareja': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtramos solo las relaciones de tipo pareja
        self.fields['pareja'].queryset = RelacionPaciente.objects.filter(tipo_relacion='pareja')
        
        # Si estamos editando, establecer el campo correspondiente como requerido
        if self.instance and self.instance.pk:
            if self.instance.paciente:
                self.fields['paciente'].required = True
                self.fields['pareja'].required = False
            elif self.instance.pareja:
                self.fields['pareja'].required = True
                self.fields['paciente'].required = False

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        hoy = date.today()
        
        if fecha and fecha < hoy:
            raise ValidationError("La fecha de la cita no puede ser anterior a la fecha actual.")
        return fecha

    def clean_hora(self):
        hora = self.cleaned_data.get('hora')
        if hora:
            # Validar que esté en horario laboral (ejemplo: 8am a 6pm)
            if hora < time(8, 0) or hora > time(18, 0):
                raise ValidationError("El horario de atención es de 8:00 AM a 6:00 PM.")
        return hora
    
    def clean(self):
        cleaned_data = super().clean()
        paciente = cleaned_data.get('paciente')
        pareja = cleaned_data.get('pareja')
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        
        # Validar selección de paciente o pareja
        if not paciente and not pareja:
            raise ValidationError('Debe seleccionar un paciente o una pareja')
        if paciente and pareja:
            raise ValidationError('Solo puede seleccionar un paciente o una pareja, no ambos')

        # Validaciones de fecha y hora
        if fecha and hora:
            # Validar que no sea una cita en el pasado (fecha y hora)
            ahora = datetime.now()
            fecha_hora_cita = datetime.combine(fecha, hora)
            
            if fecha_hora_cita < ahora:
                raise ValidationError("La fecha y hora de la cita no pueden ser en el pasado.")

            # Validar que no haya citas en la misma fecha y hora
            citas_existentes = Cita.objects.filter(fecha=fecha, hora=hora)
            
            if self.instance.pk:  # Si es una edición, excluir la cita actual
                citas_existentes = citas_existentes.exclude(pk=self.instance.pk)
            
            if citas_existentes.exists():
                raise ValidationError('Ya existe una cita programada para esta fecha y hora exacta')
            
            # Validar margen de 2 horas
            hora_inicio = hora
            hora_fin = (datetime.combine(date.today(), hora_inicio) + timedelta(hours=2))
            hora_fin = hora_fin.time()
            
            citas_solapadas = Cita.objects.filter(
                fecha=fecha,
                hora__gte=hora_inicio,
                hora__lt=hora_fin
            )
            
            if self.instance.pk:  # Si es una edición, excluir la cita actual
                citas_solapadas = citas_solapadas.exclude(pk=self.instance.pk)
            
            if citas_solapadas.exists():
                raise ValidationError('Debe haber al menos 2 horas entre citas')
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Asegurarse de que solo uno de los dos campos esté establecido
        if instance.paciente:
            instance.pareja = None
        elif instance.pareja:
            instance.paciente = None
        
        if commit:
            instance.save()
        return instance

class DetalleCitaForm(forms.ModelForm):
    class Meta:
        model = DetalleCita
        fields = ['titulo', 'anotacion', 'conclusion']  # <--- quitamos 'cita'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['titulo'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Título'})
        self.fields['anotacion'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Anotación', 'rows': 3})
        self.fields['conclusion'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Conclusión', 'rows': 3})

class RelacionPacienteForm(forms.ModelForm):
    class Meta:
        model = RelacionPaciente
        fields = ['paciente1', 'paciente2', 'tipo_relacion']

    def __init__(self, *args, **kwargs):
        super(RelacionPacienteForm, self).__init__(*args, **kwargs)
        self.fields['paciente1'].queryset = Paciente.objects.all()
        self.fields['paciente2'].queryset = Paciente.objects.all()

        self.fields['tipo_relacion'].widget = forms.Select(choices=[
            ('pareja', 'Pareja'),
            ('familiar', 'Familiar'),
            ('otro', 'Otro')
        ])


class RepresentanteForm(forms.ModelForm):
    class Meta:
        model = Representante
        fields = '__all__'
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }