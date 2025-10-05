from django.db import models


class Data(models.Model):
    id = models.IntegerField(primary_key=True) # Field name made lowercase.
    tipo = models.CharField(db_column='TIPO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cantidad_de_tipo = models.FloatField(db_column='CANTIDAD DE TIPO', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    sucursal = models.CharField(db_column='SUCURSAL', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'data'


class Inventario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='PRODUCTO_ID', blank=True, null=True)  # Field name made lowercase.
    sucursal = models.ForeignKey('Sucursal', models.DO_NOTHING, db_column='SUCURSAL_ID', blank=True, null=True)  # Field name made lowercase.
    cantidad = models.FloatField(db_column='CANTIDAD', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'inventario'


class Movimiento(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='PRODUCTO_ID', blank=True, null=True)  # Field name made lowercase.
    sucursal = models.ForeignKey('Sucursal', models.DO_NOTHING, db_column='SUCURSAL_ID', blank=True, null=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='TIPO', max_length=7, blank=True, null=True)  # Field name made lowercase.
    cantidad = models.FloatField(db_column='CANTIDAD', blank=True, null=True)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='FECHA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'movimiento'


class Producto(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.
    descripcion = models.TextField(db_column='DESCRIPCION', blank=True, null=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='TIPO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    precio_unitario = models.FloatField(db_column='PRECIO_UNITARIO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'producto'


class Sucursal(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.
    ubicacion = models.CharField(db_column='UBICACION', max_length=150, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sucursal'


class InventarioCRUD(models.Model):
    producto = models.CharField(max_length=100)
    sucursal = models.CharField(max_length=100)
    cantidad = models.FloatField()
    fecha_ingreso = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.producto} - {self.sucursal} ({self.cantidad})"


class EnviosEnCurso(models.Model):
    producto = models.CharField(max_length=100)
    sucursal = models.CharField(max_length=100)
    cantidad = models.FloatField()
    destino = models.CharField(max_length=100)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    codigo_confirmacion = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.producto} → {self.destino}"


class Usuario(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.username
