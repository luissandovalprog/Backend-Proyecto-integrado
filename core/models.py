# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid # Para generar UUIDs

# --- Tablas de Seguridad y Usuarios ---

class Rol(models.Model):
    """
    Almacena los roles del sistema para el Control de Acceso Basado en Roles (RBAC).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=50, unique=True) # Ej: 'Matrona', 'Médico', 'Administrativo', 'Administrador del Sistema (TI)'
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Rol' # Nombre exacto de la tabla en la BD
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    """
    Almacena la información de los usuarios del sistema.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rut = models.CharField(max_length=255, unique=True) # RUT del usuario (hasheado/cifrado)
    nombre_completo = models.TextField() # Nombre del personal (cifrado)
    email = models.TextField(unique=True, blank=True, null=True) # Email del usuario (cifrado)
    username = models.CharField(max_length=100, unique=True) # Nombre de usuario único para el login
    password_hash = models.CharField(max_length=255) # Contraseña almacenada de forma segura (hash)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='usuarios')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.username} ({self.nombre_completo})"

class LogAuditoria(models.Model):
    """
    Almacena logs de auditoría para trazabilidad.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='logs_auditoria')
    accion = models.CharField(max_length=255) # Ej: "CREAR_PACIENTE", "UPDATE_PARTO"
    tabla_afectada = models.CharField(max_length=100, blank=True, null=True) # Nombre de la tabla afectada
    registro_id_uuid = models.UUIDField(blank=True, null=True) # UUID del registro afectado
    detalles = models.TextField(blank=True, null=True) # Detalles adicionales del evento
    ip_usuario = models.CharField(max_length=45, blank=True, null=True) # IP del usuario que generó el log
    fecha_accion = models.DateTimeField(auto_now_add=True) # Fecha y hora de la acción (con zona horaria)

    class Meta:
        db_table = 'LogAuditoria'
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'

    def __str__(self):
        return f"{self.usuario.username} - {self.accion} - {self.fecha_accion}"

# --- Tablas del Núcleo Clínico ---

class Madre(models.Model):
    """
    Almacena la información demográfica y clínica de la paciente.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ficha_clinica_id = models.CharField(max_length=255, unique=True, blank=True, null=True) # ID clínico único del hospital
    rut_hash = models.CharField(max_length=255, unique=True, blank=True, null=True) # Hash del RUT para búsquedas
    rut_encrypted = models.TextField(blank=True, null=True) # RUT cifrado (dato sensible)
    nombre_hash = models.CharField(max_length=255, blank=True, null=True) # Hash del nombre para búsquedas
    nombre_encrypted = models.TextField(blank=True, null=True) # Nombre completo cifrado (dato sensible)
    telefono_hash = models.CharField(max_length=255, blank=True, null=True) # Hash del teléfono para búsquedas
    telefono_encrypted = models.TextField(blank=True, null=True) # Teléfono cifrado (dato sensible)
    fecha_nacimiento = models.DateField()
    nacionalidad = models.CharField(max_length=100, blank=True, null=True)
    pertenece_pueblo_originario = models.BooleanField(default=False)
    prevision = models.CharField(max_length=50, choices=[('FONASA', 'FONASA'), ('ISAPRE', 'ISAPRE'), ('PARTICULAR', 'PARTICULAR'), ('NINGUNA', 'NINGUNA')], blank=True, null=True)
    antecedentes_medicos = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True) # Fecha y hora de la creación del registro

    class Meta:
        db_table = 'Madre'
        verbose_name = 'Madre'
        verbose_name_plural = 'Madres'

    def __str__(self):
        return f"{self.nombre_encrypted} ({self.ficha_clinica_id or self.rut_hash})"

class Parto(models.Model):
    """
    Almacena la información del parto.
    """
    TIPO_PARTO_CHOICES = [
        ('Eutócico', 'Eutócico'),
        ('Cesárea Electiva', 'Cesárea Electiva'),
        ('Cesárea Urgencia', 'Cesárea Urgencia'),
        ('Fórceps', 'Fórceps'),
        ('Vacuum', 'Vacuum'),
    ]
    ANESTESIA_CHOICES = [
        ('Epidural', 'Epidural'),
        ('Raquídea', 'Raquídea'),
        ('General', 'General'),
        ('Otra', 'Otra'),
        ('Ninguna', 'Ninguna'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    madre = models.ForeignKey(Madre, on_delete=models.CASCADE, related_name='partos')
    fecha_parto = models.DateTimeField()
    edad_gestacional = models.IntegerField(blank=True, null=True)
    tipo_parto = models.CharField(max_length=50, choices=TIPO_PARTO_CHOICES)
    anestesia = models.CharField(max_length=50, choices=ANESTESIA_CHOICES, blank=True, null=True)
    partograma_data = models.JSONField(blank=True, null=True) # Datos del partograma en formato JSON
    epicrisis_data = models.JSONField(blank=True, null=True) # Datos de la epicrisis en formato JSON para la UI
    usuario_registro = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='partos_registrados')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Parto'
        verbose_name = 'Parto'
        verbose_name_plural = 'Partos'

    def __str__(self):
        return f"Parto de {self.madre.nombre_encrypted} el {self.fecha_parto}"

class RecienNacido(models.Model):
    """
    Almacena los datos de cada recién nacido, vinculado a un parto.
    """
    ESTADO_CHOICES = [
        ('Vivo', 'Vivo'),
        ('Nacido Muerto', 'Nacido Muerto'),
    ]
    SEXO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Indeterminado', 'Indeterminado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parto = models.ForeignKey(Parto, on_delete=models.CASCADE, related_name='recien_nacidos')
    rut_provisorio = models.CharField(max_length=255, blank=True, null=True)
    estado_al_nacer = models.CharField(max_length=50, choices=ESTADO_CHOICES) # 'Vivo' o 'Nacido Muerto'. Crítico para reportes REM A09.
    sexo = models.CharField(max_length=50, choices=SEXO_CHOICES, blank=True, null=True) # Sexo biológico
    peso_gramos = models.IntegerField(blank=True, null=True) # Peso al nacer, medido en gramos (ej. 3500).
    talla_cm = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True) # Talla en centímetros (ej. 49.5).
    apgar_1_min = models.SmallIntegerField(blank=True, null=True) # Puntuación Apgar al primer minuto (0-10).
    apgar_5_min = models.SmallIntegerField(blank=True, null=True) # Puntuación Apgar a los cinco minutos (0-10).
    profilaxis_vit_k = models.BooleanField(blank=True, null=True) # Indica si se administró Vitamina K.
    profilaxis_oftalmica = models.BooleanField(blank=True, null=True) # Indica si se administró profilaxis oftálmica.
    usuario_registro = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='recien_nacidos_registrados')
    fecha_registro = models.DateTimeField(auto_now_add=True) # Fecha y hora de la creación del registro

    class Meta:
        db_table = 'RecienNacido'
        verbose_name = 'Recién Nacido'
        verbose_name_plural = 'Recién Nacidos'

    def __str__(self):
        return f"RN de {self.parto.madre.nombre_encrypted} - {self.estado_al_nacer}"

# --- Tablas de Soporte y Reportes ---

class DiagnosticoCIE10(models.Model):
    """
    Catálogo maestro de diagnósticos de la Clasificación Internacional de Enfermedades (CIE-10).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=10, unique=True) # Código CIE-10
    descripcion = models.TextField() # Descripción del diagnóstico

    class Meta:
        db_table = 'DiagnosticoCIE10'
        verbose_name = 'Diagnóstico CIE-10'
        verbose_name_plural = 'Diagnósticos CIE-10'

    def __str__(self):
        return f"{self.codigo}: {self.descripcion}"

class PartoDiagnostico(models.Model):
    """
    Tabla intermedia para la relación N a N entre Parto y DiagnosticoCIE10.
    """
    parto = models.ForeignKey(Parto, on_delete=models.CASCADE)
    diagnostico = models.ForeignKey(DiagnosticoCIE10, on_delete=models.CASCADE)

    class Meta:
        db_table = 'PartoDiagnostico'
        unique_together = ('parto', 'diagnostico') # Evita duplicados
        verbose_name = 'Parto-Diagnóstico'
        verbose_name_plural = 'Partos-Diagnósticos'

    def __str__(self):
        return f"{self.parto} - {self.diagnostico}"

class Defuncion(models.Model):
    """
    Almacena información sobre defunciones de madres o recién nacidos.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recien_nacido = models.OneToOneField(RecienNacido, on_delete=models.CASCADE, related_name='defuncion', blank=True, null=True)
    madre = models.OneToOneField(Madre, on_delete=models.CASCADE, related_name='defuncion', blank=True, null=True)
    fecha_defuncion = models.DateTimeField() # Fecha y hora exactas del fallecimiento (con zona horaria).
    causa_defuncion = models.ForeignKey(DiagnosticoCIE10, on_delete=models.CASCADE, related_name='defunciones') # Causa de muerte, enlazada a DiagnosticoCIE10.
    usuario_registro = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='defunciones_registradas')
    fecha_registro = models.DateTimeField(auto_now_add=True) # Fecha y hora de la creación del registro.

    class Meta:
        db_table = 'Defuncion'
        verbose_name = 'Defunción'
        verbose_name_plural = 'Defunciones'
        # Asegura que solo uno de recien_nacido o madre esté presente
        constraints = [
            models.CheckConstraint(
                check=(models.Q(recien_nacido__isnull=False) & models.Q(madre__isnull=True)) |
                     (models.Q(recien_nacido__isnull=True) & models.Q(madre__isnull=False)),
                name='check_recien_nacido_or_madre'
            )
        ]

    def __str__(self):
        if self.recien_nacido:
            return f"Defunción de RN {self.recien_nacido.id} - {self.fecha_defuncion}"
        elif self.madre:
            return f"Defunción de Madre {self.madre.id} - {self.fecha_defuncion}"
        return f"Defunción (sin vínculo) - {self.fecha_defuncion}"

# --- Tabla de Integración NoSQL ---

class DocumentoReferencia(models.Model):
    """
    Tabla de referencia para enlazar datos transaccionales con documentos almacenados en MongoDB.
    """
    TIPO_DOCUMENTO_CHOICES = [
        ('EPICRISIS_PDF', 'Epicrisis PDF'),
        ('REPORTE_EXCEL', 'Reporte Excel'),
        ('OTRO', 'Otro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parto = models.ForeignKey(Parto, on_delete=models.CASCADE, related_name='documentos_referencia')
    mongodb_object_id = models.CharField(max_length=255, unique=True) # El ID del objeto almacenado en MongoDB (ej. ObjectId).
    nombre_archivo = models.TextField() # Nombre del archivo (ej. "Epicrisis_RUT_XXXX.pdf").
    tipo_documento = models.CharField(max_length=50, choices=TIPO_DOCUMENTO_CHOICES) # Tipo de documento
    usuario_generacion = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='documentos_generados')
    fecha_generacion = models.DateTimeField(auto_now_add=True) # Fecha y hora de generación del archivo (con zona horaria).

    class Meta:
        db_table = 'DocumentoReferencia'
        verbose_name = 'Referencia de Documento'
        verbose_name_plural = 'Referencias de Documentos'

    def __str__(self):
        return f"{self.nombre_archivo} ({self.tipo_documento}) - Parto {self.parto.id}"