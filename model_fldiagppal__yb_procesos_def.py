# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration diagnosis #
import requests
from YBLEGACY.constantes import *
from YBUTILS import notifications
from YBUTILS.viewREST import cacheController


class diagnosis(interna):

    def diagnosis_initValidation(self, name, data=None):
        response = True
        if name.endswith("activity"):
            activity = self.iface.getActivity(name)
            cacheController.setSessionVariable("activity", activity)
        return response

    def diagnosis_getForeignFields(self, model, template=None):
        ff = [
            {'verbose_name': 'ultsincro', 'func': 'field_ultsincro'}
        ]

        if template.endswith("activity"):
            ff.append({'verbose_name': 'activas', 'func': 'field_activas'})
            ff.append({'verbose_name': 'programadas', 'func': 'field_programadas'})
            ff.append({'verbose_name': 'reservadas', 'func': 'field_reservadas'})

        return ff

    def diagnosis_field_activas(self, model):
        try:
            return cacheController.getSessionVariable('activity')['active']
        except Exception:
            return None

    def diagnosis_field_programadas(self, model):
        try:
            return cacheController.getSessionVariable('activity')['scheduled']
        except Exception:
            return None

    def diagnosis_field_reservadas(self, model):
        try:
            return cacheController.getSessionVariable('activity')['reserved']
        except Exception:
            return None

    def diagnosis_field_ultsincro(self, model):
        q = qsatype.FLSqlQuery()
        q.setSelect("timestamp, texto")
        q.setFrom("yb_log")
        q.setWhere("cliente = '" + model.cliente + "' AND tipo = '" + model.proceso + "' AND texto LIKE 'Éxito%' ORDER BY timestamp DESC LIMIT 1")

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
            if parseFloat(str(ahora - tm)[2:4]) < 5.0:
                return "Sincronizado " + h
            f = "Hoy"
        elif f == qsatype.FLUtil.addDays(qsatype.Date(), -1)[:10]:
            f = "Ayer"
        else:
            f = qsatype.FLUtil.dateAMDtoDMA(f)

        return f + " - " + h

    def diagnosis_getActivity(self, name):
        try:
            header = {"Content-Type": "application/json"}

            url = None
            if qsatype.FLUtil.isInProd():
                if name.startswith("elganso"):
                    url = 'https://api.elganso.com/models/REST/tpv_comandas/csr/getactivity'
                elif name.startswith("guanabana"):
                    url = 'http://api.guanabana.store:8080/models/REST/tpv_comandas/csr/getactivity'
                elif name.startswith("sanhigia"):
                    url = 'http://store.sanhigia.com:9000/models/REST/empresa/csr/getactivity'
                else:
                    return False
            else:
                if name.startswith("sanhigia"):
                    url = 'http://127.0.0.1:8000/models/REST/empresa/csr/getactivity'
                else:
                    url = 'http://127.0.0.1:8000/models/REST/tpv_comandas/csr/getactivity'

            response = requests.get(url, headers=header)
            stCode = response.status_code
            json = None
            if response and stCode == 200:
                json = response.json()
            else:
                raise Exception("Mala respuesta")

            return json

        except Exception as e:
            print(e)
            qsatype.debug(e)
            return False

        return resul

    def diagnosis_start(self, model, cursor):
        try:
            if cursor.valueBuffer("activo"):
                return True

            request = qsatype.FLUtil.request()
            meta = getattr(request, "META", None)
            if not meta:
                meta = request["META"]

            try:
                virtualEnv = meta["VIRTUAL_ENV"]
            except Exception:
                virtualEnv = getattr(meta, "VIRTUAL_ENV", None)

            header = {"Content-Type": "application/json"}
            data = {
                "passwd": "bUqfqBMnoH",
                "fakeRequest": {
                    "name": "fake",
                    "user": qsatype.FLUtil.nameUser(),
                    "META": {
                        "SERVER_PORT": meta["SERVER_PORT"],
                        "VIRTUAL_ENV": virtualEnv
                    }
                },
                "continuous": True
            }

            proceso = cursor.valueBuffer("proceso")
            if cursor.valueBuffer("cliente") == "elganso":
                if proceso.startswith("egsync"):
                    codTienda = proceso[-4:]
                    proceso = proceso[:len(proceso) - 4]
                    data["codtienda"] = codTienda
                resul = None
                if qsatype.FLUtil.isInProd():
                    resul = notifications.post_request('https://api.elganso.com/models/REST/tpv_comandas/csr/' + proceso, header, data)
                else:
                    resul = notifications.post_request('http://127.0.0.1:8000/models/REST/tpv_comandas/csr/' + proceso, header, data)
            elif cursor.valueBuffer("cliente") == "guanabana":
                if qsatype.FLUtil.isInProd():
                    resul = notifications.post_request('http://api.guanabana.store:8080/models/REST/tpv_comandas/csr/' + proceso, header, data)
                else:
                    resul = notifications.post_request('http://127.0.0.1:8000/models/REST/tpv_comandas/csr/' + proceso, header, data)
            elif cursor.valueBuffer("cliente") == "sanhigia":
                if qsatype.FLUtil.isInProd():
                    resul = notifications.post_request('http://store.sanhigia.com:9000/models/REST/empresa/csr/' + proceso, header, data)
                else:
                    resul = notifications.post_request('http://127.0.0.1:8000/models/REST/empresa/csr/' + proceso, header, data)
            else:
                return False

            if not resul:
                return False

            if not qsatype.FLUtil.sqlUpdate("yb_procesos", ["activo"], [True], "id = " + str(cursor.valueBuffer("id"))):
                return False

            tmstmp = qsatype.Date().now()
            qsatype.FLSqlQuery().execSql("INSERT INTO yb_log (texto, cliente, tipo, timestamp) VALUES ('Info. Proceso arrancado', '" + cursor.valueBuffer("cliente") + "', '" + cursor.valueBuffer("proceso") + "', '" + tmstmp + "')")

        except Exception as e:
            print(e)
            qsatype.debug(e)
            return False

        return True

    def diagnosis_stop(self, model, cursor):
        if not cursor.valueBuffer("activo"):
            print("Ya está inactivo")
            return True

        if not qsatype.FLUtil.sqlUpdate("yb_procesos", ["activo"], [False], "id = " + str(cursor.valueBuffer("id"))):
            return False

        return True

    def diagnosis_revoke(self, model, cursor, oParam):
        try:
            request = qsatype.FLUtil.request()
            meta = getattr(request, "META", None)
            if not meta:
                meta = request["META"]

            try:
                virtualEnv = meta["VIRTUAL_ENV"]
            except Exception:
                virtualEnv = getattr(meta, "VIRTUAL_ENV", None)

            header = {"Content-Type": "application/json"}
            data = {
                "passwd": "bUqfqBMnoH",
                "fakeRequest": {
                    "name": "fake",
                    "user": qsatype.FLUtil.nameUser(),
                    "META": {
                        "SERVER_PORT": meta["SERVER_PORT"],
                        "VIRTUAL_ENV": virtualEnv
                    }
                },
                "id": oParam["id"]
            }

            if cursor.valueBuffer("cliente") == "elganso":
                resul = None
                if qsatype.FLUtil.isInProd():
                    resul = notifications.post_request('https://api.elganso.com/models/REST/tpv_comandas/csr/revoke', header, data)
                else:
                    resul = notifications.post_request('http://127.0.0.1:8000/models/REST/tpv_comandas/csr/revoke', header, data)
            elif cursor.valueBuffer("cliente") == "guanabana":
                if qsatype.FLUtil.isInProd():
                    resul = notifications.post_request('http://api.guanabana.store:8080/models/REST/tpv_comandas/csr/revoke', header, data)
                else:
                    resul = notifications.post_request('http://127.0.0.1:8000/models/REST/tpv_comandas/csr/revoke', header, data)
            elif cursor.valueBuffer("cliente") == "sanhigia":
                if qsatype.FLUtil.isInProd():
                    resul = notifications.post_request('http://store.sanhigia.com:9000/models/REST/empresa/csr/revoke', header, data)
                else:
                    resul = notifications.post_request('http://127.0.0.1:8000/models/REST/empresa/csr/revoke', header, data)
            else:
                return False

            if not resul:
                return False

        except Exception as e:
            print(e)
            qsatype.debug(e)
            return False

        return True

    def __init__(self, context=None):
        super().__init__(context)

    def initValidation(self, name, data=None):
        return self.ctx.diagnosis_initValidation(name, data=None)

    def getForeignFields(self, model, template=None):
        return self.ctx.diagnosis_getForeignFields(model, template)

    def field_activas(self, model):
        return self.ctx.diagnosis_field_activas(model)

    def field_programadas(self, model):
        return self.ctx.diagnosis_field_programadas(model)

    def field_reservadas(self, model):
        return self.ctx.diagnosis_field_reservadas(model)

    def field_ultsincro(self, model):
        return self.ctx.diagnosis_field_ultsincro(model)

    def getActivity(self, name):
        return self.ctx.diagnosis_getActivity(name)

    def start(self, model, cursor):
        return self.ctx.diagnosis_start(model, cursor)

    def stop(self, model, cursor):
        return self.ctx.diagnosis_stop(model, cursor)

    def revoke(self, model, cursor, oParam):
        return self.ctx.diagnosis_revoke(model, cursor, oParam)


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
