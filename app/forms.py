# forms.py
from django import forms
from .models import *
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms
from .models import Cita
from django.utils import timezone
import datetime as dt
from datetime import datetime, date, time, timedelta

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
       
class UsuarioCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Correo electrónico'
    }))
    
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    is_active = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'})
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'rol', 'is_active', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })

class UsuarioChangeForm(UserChangeForm):
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
    TIPO_CITA_CHOICES = [
        ('paciente', 'Individual'),
        ('relacion', 'Relación'),
    ]
    
    tipo_cita = forms.ChoiceField(
        choices=TIPO_CITA_CHOICES,
        widget=forms.RadioSelect,
        initial='paciente'
    )

    class Meta:
        model = Cita
        fields = ['tipo_cita', 'paciente', 'relacion', 'fecha', 'hora', 'modalidad', 'motivo_consulta', 'estatus']
        widgets = {
            'hora': forms.TimeInput(attrs={'type': 'time'}),
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.editing = kwargs.pop('editing', False)
        super().__init__(*args, **kwargs)
        
        self.fields['relacion'].queryset = RelacionPaciente.objects.all()
        self.fields['paciente'].required = False
        self.fields['relacion'].required = False
        
        if self.instance and self.instance.pk:
            self.fields['tipo_cita'].disabled = True
            self.fields['tipo_cita'].initial = 'paciente' if self.instance.paciente else 'relacion'
            
            if self.instance.paciente:
                self.fields['paciente'].widget = forms.HiddenInput()
                self.fields['relacion'].widget = forms.HiddenInput()
                self.fields['paciente'].initial = self.instance.paciente
            elif self.instance.relacion:
                self.fields['paciente'].widget = forms.HiddenInput()
                self.fields['relacion'].widget = forms.HiddenInput()
                self.fields['relacion'].initial = self.instance.relacion

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha < timezone.localdate():
            raise forms.ValidationError('No puede agendar citas en fechas pasadas')
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        tipo_cita = cleaned_data.get('tipo_cita')
        paciente = cleaned_data.get('paciente')
        relacion = cleaned_data.get('relacion')
        
        if tipo_cita == 'paciente' and not paciente:
            self.add_error('paciente', 'Debe seleccionar un paciente para citas individuales')
        elif tipo_cita == 'relacion' and not relacion:
            self.add_error('relacion', 'Debe seleccionar una relación')
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.instance and self.instance.pk:
            if self.instance.paciente:
                instance.tipo_cita = 'paciente'
                instance.paciente = self.instance.paciente
                instance.relacion = None
            elif self.instance.relacion:
                instance.tipo_cita = 'relacion'
                instance.relacion = self.instance.relacion
                instance.paciente = None
        else:
            if self.cleaned_data['tipo_cita'] == 'paciente':
                instance.relacion = None
            else:
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