# @class_declaration interna #
from YBLEGACY import qsatype
from YBLEGACY.constantes import *


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration diagnosis #
import datetime
from YBUTILS import notifications


class diagnosis(interna):

    def diagnosis_checkdiagnosis(self, params):
        response = {}
        if "passwd" in params and params['passwd'] == "prnAc9Pgi5uq":
            if "cliente" in params:
                cliente = params['cliente']
                if cliente == "elganso" and "proceso" in params:
                    return self.iface.checkDiagnosisElganso(cliente, params)
                elif cliente == "guanabana" and "proceso" in params:
                    return self.iface.checkDiagnosisGuanabana(cliente, params)
                elif cliente == "sanhigia" and "proceso" in params:
                    return self.iface.checkDiagnosisSanhigia(cliente, params)
        return response

    def diagnosis_checkDiagnosisElganso(self, cliente, params):
        _i = self.iface

        response = {}
        proceso = params['proceso']

        procContinuos = ["mgsyncstock", "mgsyncpoints", "mgsyncorders", "mgsynccust", "mgsyncprices"]
        procDiag = ["diagegpda", "diagsincroventasobjeto", "diagidlerroneos", "diagventastiendaficticia", "diagventassinlineas", "diagventassinpagos", "diagdirectordersnoidl", "diagfacturaseci", "diagcontabilidad","diagventaseci", "diagventassinfacturar", "diagfacturacionsii", "diagfichprocesados"]

        if proceso in procContinuos:
            response = _i.checkContinuos(cliente, proceso)
        elif proceso in procDiag:
            response = _i.checkDiag(cliente, proceso)

        elif proceso == "tiendaSM":
            fComprobacion = datetime.datetime.now() - datetime.timedelta(days=2)
            fComprobacion = str(fComprobacion)[:10]
            ultimasincro = qsatype.FLUtil.sqlSelect("flsettings", "valor", "flkey = 'fechaSincroTiendasSM'")
            ultimasincro = json.loads((ultimasincro))['fecha']
            if fComprobacion > ultimasincro:
                status = notifications.sendNotification("tiendaSM", "Error sincronización", "juanma")
                if status:
                    response = {"status": "ok"}
                else:
                    response = {"status": "error"}
                qsatype.debug(ustr("Error sincroTiendaSM", fComprobacion))

        return response

    def diagnosis_checkDiagnosisGuanabana(self, cliente, params):
        _i = self.iface

        response = {}
        proceso = params['proceso']

        procContinuos = ["gbsyncstock", "gbsyncorders", "gbsynccust", "gbsyncprices"]
        procDiag = []

        if proceso in procContinuos:
            response = _i.checkContinuos(cliente, proceso)
        elif proceso in procDiag:
            response = _i.checkDiag(cliente, proceso)

        return response

    def diagnosis_checkDiagnosisSanhigia(self, cliente, params):
        _i = self.iface

        response = {}
        proceso = params['proceso']

        procContinuos = ["shsyncstock", "shsyncorders", "shsynccust", "shsyncprices"]
        procDiag = []

        if proceso in procContinuos:
            response = _i.checkContinuos(cliente, proceso)
        elif proceso in procDiag:
            response = _i.checkDiag(cliente, proceso)

        return response

    def diagnosis_checkContinuos(self, cliente, proceso):
        _i = self.iface
        response = {}

        hSyncCont = datetime.datetime.now() - _i.dameTiempoSincro("continuo")
        sincronizadosCont = qsatype.FLUtil.sqlSelect("yb_log", "COUNT(*)", "cliente = '" + cliente + "' AND timestamp >= '" + str(hSyncCont) + "' AND tipo = '" + proceso + "' AND texto NOT LIKE 'Info.%'")

        hSyncHora = datetime.datetime.now() - datetime.timedelta(hours=1)
        sincronizadosHora = qsatype.FLUtil.sqlSelect("yb_log", "COUNT(*)", "cliente = '" + cliente + "' AND timestamp >= '" + str(hSyncHora) + "' AND tipo = '" + proceso + "' AND texto NOT LIKE 'Info.%'")

        errores = qsatype.FLUtil.sqlSelect("yb_log", "texto LIKE '%Error%'", "cliente = '" + cliente + "' AND tipo = '" + proceso + "' ORDER BY timestamp DESC LIMIT 1")

        if sincronizadosCont == 0:
            curProc = qsatype.FLSqlCursor("yb_procesos")
            curProc.select("proceso = '" + proceso + "' AND cliente = '" + cliente + "'")
            if not curProc.first():
                return False
            if not curProc.valueBuffer("activo"):
                return {"status": "ok"}
            qsatype.FLSqlQuery().execSql("INSERT INTO yb_log (texto, cliente, tipo, timestamp) VALUES ('Info. Detectado bloqueo', '" + cliente + "', '" + proceso + "', '" + qsatype.Date().now() + "')")
            # yb_procesos.stop(None, curProc)
            # curProc.setValueBuffer("activo", False)
            # time.sleep(200)
            # yb_procesos.start(None, curProc)

            response = {"status": "ok"}
            status = notifications.sendNotification("Error. " + proceso + " - " + cliente, "Reinicie proceso", _i.dameNotificadosSincro("continuo"))
            if status:
                response = {"status": "ok"}
            else:
                response = {"status": "error"}
        elif errores or sincronizadosHora == 0:
            response = {"status": "ok"}
            status = notifications.sendNotification(proceso + " - " + cliente, "Error sincronización", _i.dameNotificadosSincro("continuo"))
            if status:
                response = {"status": "ok"}
            else:
                response = {"status": "error"}
        else:
            response = {"status": "ok"}
        qsatype.debug(ustr(proceso, response))

        return response

    def diagnosis_checkDiag(self, cliente, proceso):
        _i = self.iface
        response = {}

        hSync = datetime.datetime.now() - _i.dameTiempoSincro(proceso)
        sincronizados = qsatype.FLUtil.sqlSelect("yb_log", "COUNT(*)", "cliente = '" + cliente + "' AND timestamp >= '" + str(hSync) + "' AND tipo = '" + proceso + "'")
        errores = qsatype.FLUtil.sqlSelect("yb_log", "texto LIKE '%Error%'", "cliente = '" + cliente + "' AND tipo = '" + proceso + "' ORDER BY timestamp DESC LIMIT 1")

        if sincronizados == 0 or errores:
            response = {"status": "ok"}
            # Function notificados
            status = notifications.sendNotification(proceso + " - " + cliente, "Error sincronización", _i.dameNotificadosSincro(proceso))
            if status:
                response = {"status": "ok"}
            else:
                response = {"status": "error"}
        else:
            response = {"status": "ok"}
        qsatype.debug(ustr(proceso, response))

    def diagnosis_dameTiempoSincro(self, proceso):
        if proceso == "continuo":
            return datetime.timedelta(minutes=15)
        elif proceso == "diagegpda":
            return datetime.timedelta(hours=30)
        elif proceso == "diagsincroventasobjeto":
            return datetime.timedelta(hours=24)
        elif proceso == "diagidlerroneos":
            return datetime.timedelta(hours=24)
        elif proceso == "diagventastiendaficticia":
            return datetime.timedelta(hours=24)
        elif proceso == "diagventassinlineas":
            return datetime.timedelta(hours=24)
        elif proceso == "diagventassinpagos":
            return datetime.timedelta(hours=24)
        elif proceso == "diagdirectordersnoidl":
            return datetime.timedelta(hours=24)
        elif proceso == "diagfacturaseci":
            return datetime.timedelta(hours=24)
        elif proceso == "diagcontabilidad":
            return datetime.timedelta(hours=24)
        elif proceso == "diagventaseci":
            return datetime.timedelta(hours=24)
        elif proceso == "diagventassinfacturar":
            return datetime.timedelta(hours=24)
        elif proceso == "diagfacturacionsii":
            return datetime.timedelta(hours=24)
        elif proceso == "diagfichprocesados":
            return datetime.timedelta(hours=24)
        else:
            return 0

    def diagnosis_dameNotificadosSincro(self, proceso):
        if proceso == "continuo":
            return ["javier", "ivan"]
        elif proceso == "diagegpda":
            return ["juanma", "santiago", "jesus"]
        elif proceso == "diagsincroventasobjeto":
            return ["lorena", "santiago", "jesus"]
        elif proceso == "diagidlerroneos":
            return ["lorena", "santiago", "jesus"]
        elif proceso == "diagventastiendaficticia":
            return ["lorena", "santiago", "jesus"]
        elif proceso == "diagventassinlineas":
            return ["lorena", "santiago", "jesus"]
        elif proceso == "diagventassinpagos":
            return ["lorena", "santiago", "jesus"]
        elif proceso == "diagdirectordersnoidl":
            return ["lorena", "santiago", "jesus"]
        elif proceso == "diagfacturaseci":
            return ["lorena", "santiago", "jesus"]
        elif proceso == "diagcontabilidad":
            return ["lorena", "santiago", "jesus"]
        elif proceso == "diagventaseci":
            return ["lorena", "santiago", "jesus"]
        elif proceso == "diagventassinfacturar":
            return ["lorena", "santiago", "jesus"]
        elif proceso == "diagfacturacionsii":
            return ["lorena", "santiago", "jesus"]
        elif proceso == "diagfichprocesados":
            return ["lorena", "santiago", "jesus"]
        else:
            return ["javier"]

    def diagnosis_getForeignFields(self, model, template=None):
        return [{"verbose_name": "conditions", "func": "field_condition"}]

    def diagnosis_field_condition(self, model):
        if model.tipo == "Ventas Tpv":
            hMax = datetime.datetime.now() - datetime.timedelta(hours=2)
            hMin = datetime.datetime.now() - datetime.timedelta(hours=4)
            return {
                "ok": qsatype.FLUtil.sqlSelect("yb_subregdiagnosis", "COUNT(idsubreg)", "idreg = " + str(model.idreg) + " AND timestamp >= '" + str(hMax) + "'"),
                "error": qsatype.FLUtil.sqlSelect("yb_subregdiagnosis", "COUNT(idsubreg)", "idreg = " + str(model.idreg) + " AND timestamp < '" + str(hMin) + "'"),
                "warn": qsatype.FLUtil.sqlSelect("yb_subregdiagnosis", "COUNT(idsubreg)", "idreg = " + str(model.idreg) + " AND timestamp < '" + str(hMax) + "' AND timestamp >= '" + str(hMin) + "'")
            }
        elif model.tipo == "Stock":
            hMax = datetime.datetime.now() - datetime.timedelta(hours=24)
            hMin = datetime.datetime.now() - datetime.timedelta(hours=48)
            return {
                "ok": qsatype.FLUtil.sqlSelect("yb_subregdiagnosis", "COUNT(idsubreg)", "idreg = " + str(model.idreg) + " AND timestamp >= '" + str(hMax) + "'"),
                "error": qsatype.FLUtil.sqlSelect("yb_subregdiagnosis", "COUNT(idsubreg)", "idreg = " + str(model.idreg) + " AND timestamp < '" + str(hMin) + "'"),
                "warn": qsatype.FLUtil.sqlSelect("yb_subregdiagnosis", "COUNT(idsubreg)", "idreg = " + str(model.idreg) + " AND timestamp < '" + str(hMax) + "' AND timestamp >= '" + str(hMin) + "'")
            }
        elif model.tipo == "Arqueos Tpv":
            hMax = datetime.datetime.now() - datetime.timedelta(hours=1)
            hMin = datetime.datetime.now() - datetime.timedelta(hours=2)
            return {
                "ok": qsatype.FLUtil.sqlSelect("yb_subregdiagnosis", "COUNT(idsubreg)", "idreg = " + str(model.idreg) + " AND timestamp >= '" + str(hMax) + "'"),
                "error": qsatype.FLUtil.sqlSelect("yb_subregdiagnosis", "COUNT(idsubreg)", "idreg = " + str(model.idreg) + " AND timestamp < '" + str(hMin) + "'"),
                "warn": qsatype.FLUtil.sqlSelect("yb_subregdiagnosis", "COUNT(idsubreg)", "idreg = " + str(model.idreg) + " AND timestamp < '" + str(hMax) + "' AND timestamp >= '" + str(hMin) + "'")
            }
        else:
            hMax = datetime.datetime.now() - datetime.timedelta(hours=4)
            hMin = datetime.datetime.now() - datetime.timedelta(hours=8)
            return {
                "ok": qsatype.FLUtil.sqlSelect("yb_subregdiagnosis", "COUNT(idsubreg)", "idreg = " + str(model.idreg) + " AND timestamp >= '" + str(hMax) + "'"),
                "error": qsatype.FLUtil.sqlSelect("yb_subregdiagnosis", "COUNT(idsubreg)", "idreg = " + str(model.idreg) + " AND timestamp < '" + str(hMin) + "'"),
                "warn": qsatype.FLUtil.sqlSelect("yb_subregdiagnosis", "COUNT(idsubreg)", "idreg = " + str(model.idreg) + " AND timestamp < '" + str(hMax) + "' AND timestamp >= '" + str(hMin) + "'")
            }

    def diagnosis_dameSubregistrosDiagnosis(self, model):
        haySubReg = qsatype.FLUtil().sqlSelect("yb_subregdiagnosis", "idsubreg", "idreg = " + str(model.pk))
        if haySubReg:
            return '/diagnosis/yb_regdiagnosis/' + str(model.pk)
        else:
            return False

    def __init__(self, context=None):
        super().__init__(context)

    def checkdiagnosis(self, params):
        return self.ctx.diagnosis_checkdiagnosis(params)

    def getForeignFields(self, model, template=None):
        return self.ctx.diagnosis_getForeignFields(model, template)

    def field_condition(self, model):
        return self.ctx.diagnosis_field_condition(model)

    def dameSubregistrosDiagnosis(self, model):
        return self.ctx.diagnosis_dameSubregistrosDiagnosis(model)

    def checkDiagnosisElganso(self, cliente, params):
        return self.ctx.diagnosis_checkDiagnosisElganso(cliente, params)

    def checkDiagnosisGuanabana(self, cliente, params):
        return self.ctx.diagnosis_checkDiagnosisGuanabana(cliente, params)

    def checkDiagnosisSanhigia(self, cliente, params):
        return self.ctx.diagnosis_checkDiagnosisSanhigia(cliente, params)

    def checkContinuos(self, cliente, proceso):
        return self.ctx.diagnosis_checkContinuos(cliente, proceso)

    def checkDiag(self, cliente, proceso):
        return self.ctx.diagnosis_checkDiag(cliente, proceso)

    def dameTiempoSincro(self, proceso):
        return self.ctx.diagnosis_dameTiempoSincro(proceso)

    def dameNotificadosSincro(self, proceso):
        return self.ctx.diagnosis_dameNotificadosSincro(proceso)


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
