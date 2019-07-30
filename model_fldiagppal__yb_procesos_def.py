# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration diagnosis #
import time
from YBLEGACY.constantes import *
from YBUTILS.viewREST import cacheController
from models.fldiagppal import fldiagppal_def as diagppal


class diagnosis(interna):

    def diagnosis_getForeignFields(self, model, template=None):
        ff = [
            {"verbose_name": "ultsincro", "func": "field_ultsincro"},
            {"verbose_name": "activo_ext", "func": "field_activo_ext"}
        ]

        return ff

    def diagnosis_field_ultsincro(self, model):
        q = qsatype.FLSqlQuery()
        q.setSelect("timestamp, texto")
        q.setFrom("yb_log")
        q.setWhere("cliente = '{}' AND tipo = '{}' AND texto LIKE 'Éxito%' ORDER BY timestamp DESC LIMIT 1".format(model.cliente.cliente, model.proceso))

        if not q.exec_():
            return "Error. Falló la query."

        if not q.first():
            return "No hay registros."

        tm = qsatype.Date(q.value("timestamp"))
        stm = tm.toString()
        f = stm[:10]
        h = stm[11:19]
        ahora = qsatype.Date()
        if f == ahora.toString()[:10]:
            if parseFloat(str(ahora - tm)[2:4]) < 10.0:
                return "Sincronizado {}".format(h)
            f = "Hoy"
        elif f == qsatype.FLUtil.addDays(qsatype.Date(), -1)[:10]:
            f = "Ayer"
        else:
            f = qsatype.FLUtil.dateAMDtoDMA(f)

        return "{} - {}".format(f, h)

    def diagnosis_field_activo_ext(self, model):
        if model.syncrecieve:
            return "Recepción"

        if model.activo:
            return "Sí"

        return "No"

    def diagnosis_start(self, model, cursor):
        try:
            if cursor.valueBuffer("syncrecieve"):
                return {
                    "status": 1,
                    "msg": "Proceso de recepción"
                }
            if cursor.valueBuffer("activo"):
                return True

            resul = diagppal.iface.single_start(cursor)
            if resul and "msg" in resul and resul["msg"] == "Tarea encolada correctamente":
                diagppal.iface.log("Info. Proceso arrancado", cursor.valueBuffer("proceso"), cursor.valueBuffer("cliente"))
            return resul

        except Exception as e:
            qsatype.debug(e)
            return False

        return True

    def diagnosis_stop(self, model, cursor):
        if cursor.valueBuffer("syncrecieve"):
            return {
                "status": 1,
                "msg": "Proceso de recepción"
            }
        if not cursor.valueBuffer("activo"):
            return True

        if not qsatype.FLUtil.sqlUpdate("yb_procesos", ["activo"], [False], "id = {}".format(cursor.valueBuffer("id"))):
            return False

        return True

    def __init__(self, context=None):
        super().__init__(context)

    def getForeignFields(self, model, template=None):
        return self.ctx.diagnosis_getForeignFields(model, template)

    def field_ultsincro(self, model):
        return self.ctx.diagnosis_field_ultsincro(model)

    def field_activo_ext(self, model):
        return self.ctx.diagnosis_field_activo_ext(model)

    def start(self, model, cursor):
        return self.ctx.diagnosis_start(model, cursor)

    def stop(self, model, cursor):
        return self.ctx.diagnosis_stop(model, cursor)


# @class_declaration head #
class head(diagnosis):

    def __init__(self, context=None):
        super().__init__(context)


# @class_declaration ifaceCtx #
class ifaceCtx(head):

    def __init__(self, context=None):
        super().__init__(context)


# @class_declaration FormInternalObj #
class FormInternalObj(qsatype.FormDBWidget):
    def _class_init(self):
        self.iface = ifaceCtx(self)
