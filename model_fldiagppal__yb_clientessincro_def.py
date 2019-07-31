# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration diagnosis #
import requests

from YBLEGACY.constantes import *
from YBUTILS.viewREST import cacheController

from sync import tasks
from models.fldiagppal import fldiagppal_def as diagppal


class diagnosis(interna):

    def diagnosis_getDesc(self):
        return "descripcion"

    def diagnosis_getForeignFields(self, model, template=None):
        ff = []

        if template == "formRecord":
            ff.append({"verbose_name": "activas", "func": "field_activas"})
            ff.append({"verbose_name": "programadas", "func": "field_programadas"})
            ff.append({"verbose_name": "reservadas", "func": "field_reservadas"})

        if template == "master":
            ff.append({"verbose_name": "procesos", "func": "field_procesos"})
            ff.append({"verbose_name": "procesos_auto", "func": "field_procesos_auto"})

        return ff

    def diagnosis_drawif_gruposgrid(self, cursor):
        if self.iface.get_estado() != "grupos":
            return "hidden"

    def diagnosis_drawif_botongrupos(self, cursor):
        if self.iface.get_estado() == "grupos":
            return "disabled"

    def diagnosis_drawif_activitybox(self, cursor):
        if self.iface.get_estado() != "activity":
            return "hidden"

    def diagnosis_drawif_botonactivity(self, cursor):
        if self.iface.get_estado() == "activity":
            return "disabled"

    def diagnosis_drawif_configform(self, cursor):
        if self.iface.get_estado() != "config":
            return "hidden"

    def diagnosis_drawif_botonconfig(self, cursor):
        if self.iface.get_estado() == "config":
            return "disabled"

    def diagnosis_get_estado(self):
        estado = cacheController.getSessionVariable("estado_clientessincro", None)

        if not estado:
            self.iface.set_estado("grupos")
            estado = "grupos"

        return estado

    def diagnosis_set_estado(self, estado):
        cacheController.setSessionVariable("estado_clientessincro", estado)
        return True

    def diagnosis_drawif_master_clientesgrid(self, cursor):
        if self.iface.get_estado_master() != "clientes":
            return "hidden"

    def diagnosis_drawif_master_botonclientes(self, cursor):
        if self.iface.get_estado_master() == "clientes":
            return "disabled"

    def diagnosis_drawif_master_loggrid(self, cursor):
        if self.iface.get_estado_master() != "log":
            return "hidden"

    def diagnosis_drawif_master_botonlog(self, cursor):
        if self.iface.get_estado_master() == "log":
            return "disabled"

    def diagnosis_get_estado_master(self):
        estado = cacheController.getSessionVariable("estado_master_clientessincro", None)

        if not estado:
            self.iface.set_estado_master("clientes")
            estado = "clientes"

        return estado

    def diagnosis_set_estado_master(self, estado):
        cacheController.setSessionVariable("estado_master_clientessincro", estado)
        return True

    def diagnosis_field_activas(self, model):
        try:
            if self.get_estado() == "activity":
                activity = self.iface.get_activity(model.cliente)
                cacheController.setSessionVariable("activity", activity)
            else:
                cacheController.setSessionVariable("activity", {"active": {}, "reserved": {}, "scheduled": {}})
                return {}

            return cacheController.getSessionVariable("activity")["active"]
        except Exception:
            return {}

    def diagnosis_field_programadas(self, model):
        try:
            return cacheController.getSessionVariable("activity")["scheduled"]
        except Exception:
            return {}

    def diagnosis_field_reservadas(self, model):
        try:
            return cacheController.getSessionVariable("activity")["reserved"]
        except Exception:
            return {}

    def diagnosis_field_procesos(self, model):
        totales = qsatype.FLUtil.sqlSelect("yb_procesos", "COUNT(id)", "cliente = '{}' AND (NOT syncrecieve OR syncrecieve IS NULL)".format(model.cliente))
        activos = qsatype.FLUtil.sqlSelect("yb_procesos", "COUNT(id)", "cliente = '{}' AND activo AND (NOT syncrecieve OR syncrecieve IS NULL)".format(model.cliente))
        return "Procesos activos: {} de {}".format(activos, totales)

    def diagnosis_field_procesos_auto(self, model):
        totales = qsatype.FLUtil.sqlSelect("yb_procesos", "COUNT(id)", "cliente = '{}' AND syncauto AND (NOT syncrecieve OR syncrecieve IS NULL)".format(model.cliente))
        activos = qsatype.FLUtil.sqlSelect("yb_procesos", "COUNT(id)", "cliente = '{}' AND activo AND syncauto AND (NOT syncrecieve OR syncrecieve IS NULL)".format(model.cliente))
        return "Procesos automáticos: {} de {}".format(activos, totales)

    def diagnosis_get_activity(self, customer):
        try:
            syncapi = False
            if qsatype.FLUtil.sqlSelect("yb_procesos", "id", "cliente = '{}' AND syncapi LIMIT 1".format(customer)):
                syncapi = True

            url = diagppal.iface.get_server_url(customer, syncapi, in_production=qsatype.FLUtil.isInProd())
            if not url:
                return {"active": {}, "reserved": {}, "scheduled": {}}

            if syncapi:
                url = "{}/celery/activity/get".format(url)
            else:
                url = "{}/getactivity".format(url)

            response = requests.get(url)
            if response and response.status_code == 200:
                return response.json()
            else:
                raise Exception("Mala respuesta")

        except Exception as e:
            qsatype.debug(e)
            return {"active": {}, "reserved": {}, "scheduled": {}}

    def diagnosis_revoke(self, model, cursor, oParam):
        try:
            customer = cursor.valueBuffer("cliente")

            syncapi = False
            if qsatype.FLUtil.sqlSelect("yb_procesos", "id", "cliente = '{}' AND syncapi LIMIT 1".format(customer)):
                syncapi = True

            url = ybprocesos.iface.get_server_url(customer, syncapi)
            if not url:
                return False

            if syncapi:
                url = "{}/celery/tasks/revoke/{}".format(url, oParam["id"])

                response = requests.get(url)
                if response and response.status_code == 200:
                    return response.json()
                else:
                    raise Exception("Mala respuesta")

            url = "{}/revoke".format(url)

            header = {"Content-Type": "application/json"}
            data = {
                "passwd": "bUqfqBMnoH",
                "id": oParam["id"]
            }

            response = notifications.post_request(url, header, data)
            if response and response.status_code == 200:
                return response.json()
            else:
                raise Exception("Mala respuesta")

        except Exception as e:
            qsatype.debug(e)
            return False

        return True

    def diagnosis_start(self, model, oParam):
        tasks.startall.delay(model.cliente, qsatype.FLUtil.isInProd())
        return True

    def diagnosis_stop(self, model, oParam):
        if not qsatype.FLUtil.sqlUpdate("yb_procesos", ["activo"], [False], "cliente = '{}' AND activo".format(model.cliente)):
            return False

        return True

    def __init__(self, context=None):
        super().__init__(context)

    def getDesc(self):
        return self.ctx.diagnosis_getDesc()

    def getForeignFields(self, model, template=None):
        return self.ctx.diagnosis_getForeignFields(model, template)

    def drawif_gruposgrid(self, cursor):
        return self.ctx.diagnosis_drawif_gruposgrid(cursor)

    def drawif_botongrupos(self, cursor):
        return self.ctx.diagnosis_drawif_botongrupos(cursor)

    def drawif_activitybox(self, cursor):
        return self.ctx.diagnosis_drawif_activitybox(cursor)

    def drawif_botonactivity(self, cursor):
        return self.ctx.diagnosis_drawif_botonactivity(cursor)

    def drawif_configform(self, cursor):
        return self.ctx.diagnosis_drawif_configform(cursor)

    def drawif_botonconfig(self, cursor):
        return self.ctx.diagnosis_drawif_botonconfig(cursor)

    def get_estado(self):
        return self.ctx.diagnosis_get_estado()

    def set_estado(self, estado):
        return self.ctx.diagnosis_set_estado(estado)

    def drawif_master_clientesgrid(self, cursor):
        return self.ctx.diagnosis_drawif_master_clientesgrid(cursor)

    def drawif_master_botonclientes(self, cursor):
        return self.ctx.diagnosis_drawif_master_botonclientes(cursor)

    def drawif_master_loggrid(self, cursor):
        return self.ctx.diagnosis_drawif_master_loggrid(cursor)

    def drawif_master_botonlog(self, cursor):
        return self.ctx.diagnosis_drawif_master_botonlog(cursor)

    def get_estado_master(self):
        return self.ctx.diagnosis_get_estado_master()

    def set_estado_master(self, estado):
        return self.ctx.diagnosis_set_estado_master(estado)

    def field_activas(self, model):
        return self.ctx.diagnosis_field_activas(model)

    def field_programadas(self, model):
        return self.ctx.diagnosis_field_programadas(model)

    def field_reservadas(self, model):
        return self.ctx.diagnosis_field_reservadas(model)

    def field_procesos(self, model):
        return self.ctx.diagnosis_field_procesos(model)

    def field_procesos_auto(self, model):
        return self.ctx.diagnosis_field_procesos_auto(model)

    def get_activity(self, customer):
        return self.ctx.diagnosis_get_activity(customer)

    def revoke(self, model, cursor, oParam):
        return self.ctx.diagnosis_revoke(model, cursor, oParam)

    def start(self, model, oParam):
        return self.ctx.diagnosis_start(model, oParam)

    def stop(self, model, oParam):
        return self.ctx.diagnosis_stop(model, oParam)


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
