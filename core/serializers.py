# core/serializers.py
from rest_framework import serializers
from . import models

# --- Serializers para Seguridad y Usuarios ---

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Rol
        fields = '__all__' 

class UsuarioSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True) 

    class Meta:
        model = models.Usuario
        fields = ['id', 'rut', 'nombre_completo', 'email', 'username', 'rol', 'rol_nombre', 'activo', 'fecha_creacion'] 


class LogAuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LogAuditoria
        fields = '__all__'

# --- Serializers para Núcleo Clínico ---

class MadreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Madre
        fields = '__all__'

class PartoSerializer(serializers.ModelSerializer):
    madre_nombre = serializers.CharField(source='madre.nombre_encrypted', read_only=True) # Campo anidado
    usuario_registro_nombre = serializers.CharField(source='usuario_registro.nombre_completo', read_only=True)

    class Meta:
        model = models.Parto
        fields = '__all__'

class RecienNacidoSerializer(serializers.ModelSerializer):
    parto_fecha = serializers.DateTimeField(source='parto.fecha_parto', read_only=True) # Campo anidado
    usuario_registro_nombre = serializers.CharField(source='usuario_registro.nombre_completo', read_only=True)

    class Meta:
        model = models.RecienNacido
        fields = '__all__'

# --- Serializers para Soporte y Reportes ---

class DiagnosticoCIE10Serializer(serializers.ModelSerializer):
    class Meta:
        model = models.DiagnosticoCIE10
        fields = '__all__'

class PartoDiagnosticoSerializer(serializers.ModelSerializer):
    diagnostico = DiagnosticoCIE10Serializer(read_only=True)
    diagnostico_id = serializers.PrimaryKeyRelatedField(queryset=models.DiagnosticoCIE10.objects.all(), source='diagnostico', write_only=True)

    class Meta:
        model = models.PartoDiagnostico
        fields = ['parto', 'diagnostico', 'diagnostico_id'] # Ajusta según necesidad

class DefuncionSerializer(serializers.ModelSerializer):
    madre_nombre = serializers.CharField(source='madre.nombre_encrypted', read_only=True, allow_null=True)
    recien_nacido_id = serializers.CharField(source='recien_nacido.id', read_only=True, allow_null=True)
    causa_defuncion_nombre = serializers.CharField(source='causa_defuncion.descripcion', read_only=True)

    class Meta:
        model = models.Defuncion
        fields = '__all__'

# --- Serializer para Integración NoSQL ---

class DocumentoReferenciaSerializer(serializers.ModelSerializer):
    parto_fecha = serializers.DateTimeField(source='parto.fecha_parto', read_only=True) # Campo anidado
    usuario_generacion_nombre = serializers.CharField(source='usuario_generacion.nombre_completo', read_only=True)

    class Meta:
        model = models.DocumentoReferencia
        fields = '__all__'