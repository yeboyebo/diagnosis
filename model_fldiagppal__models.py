from django.db import models

from YBLEGACY.FLUtil import FLUtil
from YBLEGACY.clasesBase import BaseModel


def _miextend(self, **kwargs):
    self._legacy_mtd = kwargs
    return self


models.Field._miextend = _miextend


class mtd_yb_log(models.Model, BaseModel):

    id = models.AutoField(
        db_column="id",
        verbose_name=FLUtil.translate("MetaData", "Identificador"),
        primary_key=True
    )._miextend(
        visiblegrid=False,
        OLDTIPO="SERIAL"
    )
    cliente = models.CharField(
        db_column="cliente",
        verbose_name=FLUtil.translate("MetaData", "Cliente"),
        max_length=100
    )._miextend(
        OLDTIPO="STRING"
    )
    tipo = models.CharField(
        db_column="tipo",
        verbose_name=FLUtil.translate("MetaData", "Tipo"),
        max_length=100
    )._miextend(
        OLDTIPO="STRING"
    )
    texto = models.TextField(
        db_column="texto",
        verbose_name=FLUtil.translate("MetaData", "Log")
    )._miextend(
        OLDTIPO="STRING"
    )
    timestamp = models.DateTimeField(
        db_column="timestamp",
        verbose_name=FLUtil.translate("MetaData", "Ult.Sincro")
    )._miextend(
        OLDTIPO="DATE"
    )

    class Meta:
        managed = True
        verbose_name = FLUtil.translate("MetaData", "Registros de logs")
        db_table = u"yb_log"
        # app_label = "secondary"


class mtd_yb_regdiagnosis(models.Model, BaseModel):
    _YB_LEGACY = True
    idreg = models.AutoField(
        db_column="idreg",
        verbose_name=FLUtil.translate("MetaData", "Identificador"),
        primary_key=True
    )._miextend(
        visiblegrid=False,
        OLDTIPO="SERIAL"
    )
    cliente = models.CharField(
        db_column="cliente",
        verbose_name=FLUtil.translate("MetaData", "Cliente"),
        max_length=50
    )._miextend(
        OLDTIPO="STRING"
    )
    tipo = models.CharField(
        db_column="tipo",
        verbose_name=FLUtil.translate("MetaData", "Tipo"),
        max_length=50
    )._miextend(
        OLDTIPO="STRING"
    )
    timestamp = models.CharField(
        db_column="timestamp",
        verbose_name=FLUtil.translate("MetaData", "Ult.Sincro"),
        max_length=50
    )._miextend(
        OLDTIPO="STRING"
    )

    class Meta:
        managed = True
        verbose_name = FLUtil.translate("MetaData", "Registros de diagnosis")
        db_table = u"yb_regdiagnosis"
        # app_label = "secondary"


class mtd_yb_subregdiagnosis(models.Model, BaseModel):
    _YB_LEGACY = True
    idsubreg = models.AutoField(
        db_column="idsubreg",
        verbose_name=FLUtil.translate("MetaData", "Identificador"),
        primary_key=True
    )._miextend(
        visiblegrid=False,
        OLDTIPO="SERIAL"
    )
    idreg = models.IntegerField(
        db_column="idreg",
        verbose_name=FLUtil.translate("MetaData", "Registro")
    )._miextend(
        OLDTIPO="UINT"
    )
    destino = models.CharField(
        db_column="destino",
        verbose_name=FLUtil.translate("MetaData", "Destino"),
        max_length=50
    )._miextend(
        OLDTIPO="STRING"
    )
    timestamp = models.CharField(
        db_column="timestamp",
        verbose_name=FLUtil.translate("MetaData", "Ult.Sincro"),
        max_length=50
    )._miextend(
        OLDTIPO="STRING"
    )

    class Meta:
        managed = True
        verbose_name = FLUtil.translate("MetaData", "Subregistros de diagnosis")
        db_table = u"yb_subregdiagnosis"
        # app_label = "secondary"


class mtd_yb_clientessincro(models.Model, BaseModel):

    id = models.AutoField(
        db_column="id",
        verbose_name=FLUtil.translate("MetaData", "Identificador"),
        primary_key=True
    )._miextend(
        visiblegrid=False,
        OLDTIPO="SERIAL"
    )
    cliente = models.CharField(
        db_column="cliente",
        verbose_name=FLUtil.translate("MetaData", "Cliente"),
        max_length=100
    )._miextend(
        OLDTIPO="STRING"
    )
    url = models.TextField(
        db_column="url",
        verbose_name=FLUtil.translate("MetaData", "URL"),
        max_length=250
    )._miextend(
        OLDTIPO="STRING"
    )
    test_url = models.TextField(
        db_column="test_url",
        verbose_name=FLUtil.translate("MetaData", "TEST URL"),
        max_length=250
    )._miextend(
        OLDTIPO="STRING"
    )

    class Meta:
        managed = True
        verbose_name = FLUtil.translate("MetaData", "Clientes de sincronización")
        db_table = u"yb_clientessincro"
        # app_label = "secondary"


class mtd_yb_procesos(models.Model, BaseModel):

    id = models.AutoField(
        db_column="id",
        verbose_name=FLUtil.translate("MetaData", "Identificador"),
        primary_key=True
    )._miextend(
        visiblegrid=False,
        OLDTIPO="SERIAL"
    )
    cliente = models.CharField(
        db_column="cliente",
        verbose_name=FLUtil.translate("MetaData", "Cliente"),
        max_length=100
    )._miextend(
        OLDTIPO="STRING"
    )
    proceso = models.CharField(
        db_column="proceso",
        verbose_name=FLUtil.translate("MetaData", "Proceso"),
        max_length=100
    )._miextend(
        OLDTIPO="STRING"
    )
    descripcion = models.TextField(
        db_column="descripcion",
        verbose_name=FLUtil.translate("MetaData", "Descripción")
    )._miextend(
        OLDTIPO="STRING"
    )
    activo = models.BooleanField(
        db_column="activo",
        verbose_name=FLUtil.translate("MetaData", "Activo"),
        default=False,
        null=False
    )._miextend(
        OLDTIPO="BOOL"
    )
    url = models.TextField(
        db_column="url",
        verbose_name=FLUtil.translate("MetaData", "URL"),
        max_length=150
    )._miextend(
        OLDTIPO="STRING"
    )
    syncapi = models.BooleanField(
        db_column="syncapi",
        verbose_name=FLUtil.translate("MetaData", "Sincro por API"),
        default=False,
        null=False
    )._miextend(
        OLDTIPO="BOOL"
    )
    syncstore = models.BooleanField(
        db_column="syncstore",
        verbose_name=FLUtil.translate("MetaData", "Sincro de tienda"),
        default=False,
        null=False
    )._miextend(
        OLDTIPO="BOOL"
    )

    class Meta:
        managed = True
        verbose_name = FLUtil.translate("MetaData", "Procesos automáticos")
        db_table = u"yb_procesos"
        # app_label = "secondary"


class mtd_yb_procesos_erroneos(models.Model, BaseModel):

    id = models.AutoField(
        db_column="id",
        verbose_name=FLUtil.translate("MetaData", "Identificador"),
        primary_key=True
    )._miextend(
        visiblegrid=False,
        OLDTIPO="SERIAL"
    )
    cliente = models.CharField(
        db_column="cliente",
        verbose_name=FLUtil.translate("MetaData", "Cliente"),
        max_length=100
    )._miextend(
        OLDTIPO="STRING"
    )
    proceso = models.CharField(
        db_column="proceso",
        verbose_name=FLUtil.translate("MetaData", "Proceso"),
        max_length=100
    )._miextend(
        OLDTIPO="STRING"
    )
    error = models.TextField(
        db_column="error",
        verbose_name=FLUtil.translate("MetaData", "Error")
    )._miextend(
        OLDTIPO="STRING"
    )
    codregistro = models.CharField(
        db_column="codregistro",
        verbose_name=FLUtil.translate("MetaData", "Cod. Registro"),
        max_length=100
    )._miextend(
        OLDTIPO="STRING"
    )
    resuelto = models.BooleanField(
        db_column="resuelto",
        verbose_name=FLUtil.translate("MetaData", "Resuelto"),
        default=False,
        null=False
    )._miextend(
        OLDTIPO="BOOL"
    )
    timestamp = models.CharField(
        db_column="timestamp",
        verbose_name=FLUtil.translate("MetaData", "Ult.Sincro"),
        max_length=50
    )._miextend(
        OLDTIPO="STRING"
    )

    class Meta:
        managed = True
        verbose_name = FLUtil.translate("MetaData", "Procesos erróneos")
        db_table = u"yb_procesos_erroneos"
        # app_label = "secondary"
