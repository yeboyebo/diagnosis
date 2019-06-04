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
from models.fldiagppal import fldiagppal_def as diagppal


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

    def diagnosis_get_server_url(self, cliente, force_notdb=False):
        q = qsatype.FLSqlQuery()
        q.setSelect("url, test_url")
        q.setFrom("yb_clientessincro")
        q.setWhere("cliente = '{}'".format(cliente))

        if not q.exec_():
            return False

        if q.first() and not force_notdb:
            url = None
            if qsatype.FLUtil.isInProd():
                url = q.value("url")
            else:
                url = q.value("test_url")

            return "{}sync".format(url), True
        else:
            if qsatype.FLUtil.isInProd():
                if cliente == "elganso":
                    url = "https://api.elganso.com"
                elif cliente == "guanabana":
                    url = "http://api.guanabana.store:8080"
                elif cliente == "sanhigia":
                    url = "http://store.sanhigia.com:9000"
                else:
                    return False
            else:
                url = "http://127.0.0.1:8000"

            url = "{}/models/REST".format(url)
            if cliente in ("elganso", "guanabana"):
                url = "{}/tpv_comandas/csr".format(url)
            else:
                url = "{}/empresa/csr".format(url)

            return url, False

    def diagnosis_get_url(self, cliente, proceso):
        try:
            force_notdb = False

            if cliente == "elganso" and (proceso == "mgsyncdevweb" or proceso.startswith("egsync")):
                force_notdb = True

            server_url, frombd = self.get_server_url(cliente, force_notdb=force_notdb)
            if not server_url:
                return False

            if frombd:
                q = qsatype.FLSqlQuery()
                q.setSelect("url")
                q.setFrom("yb_procesos")
                q.setWhere("cliente = '{}' AND proceso = '{}'".format(cliente, proceso))

                if not q.exec_():
                    return False

                if not q.first():
                    return False

                return "{}/{}".format(server_url, q.value("url")), True
            else:
                return "{}/{}".format(server_url, proceso), False

        except Exception as e:
            qsatype.debug(e)
            return False

    def diagnosis_start(self, model, cursor):
        try:
            if cursor.valueBuffer("activo"):
                return True

            cliente = cursor.valueBuffer("cliente")
            proceso = cursor.valueBuffer("proceso")

            url, fromdb = self.get_url(cliente, proceso)
            if not url:
                return False

            if fromdb:
                header = {"Content-Type": "application/json"}
                data = {
                    "passwd": "bUqfqBMnoH",
                    "continuous": True,
                    "production": qsatype.FLUtil.isInProd()
                }

                resul = notifications.post_request(url, header, data)

                if not resul:
                    return False
            else:
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
                    }
                }

                proceso = cursor.valueBuffer("proceso")
                if cursor.valueBuffer("cliente") == "elganso" and proceso.startswith("egsync"):
                    codTienda = proceso[-4:]
                    # proceso = proceso[:len(proceso) - 4]
                    data["codtienda"] = codTienda

                    url = url[:-4]

                resul = notifications.post_request(url, header, data)

                if not resul:
                    return False

            if not qsatype.FLUtil.sqlUpdate("yb_procesos", ["activo"], [True], "id = " + str(cursor.valueBuffer("id"))):
                return False

            diagppal.iface.log("Info. Proceso arrancado", proceso, cliente)

            return resul

        except Exception as e:
            qsatype.debug(e)
            return False

        return True

    def diagnosis_stop(self, model, cursor):
        if not cursor.valueBuffer("activo"):
            return True

        if not qsatype.FLUtil.sqlUpdate("yb_procesos", ["activo"], [False], "id = " + str(cursor.valueBuffer("id"))):
            return False

        return True

    def diagnosis_getActivity(self, name):
        try:
            customer = name.split("_activity")[0]

            url, frombd = self.get_server_url(customer)
            if not url:
                return False

            if frombd:
                url = "{}/celery".format(url)

            url = "{}/getactivity".format(url)

            response = requests.get(url)
            if response and response.status_code == 200:
                return response.json()
            else:
                raise Exception("Mala respuesta")

        except Exception as e:
            qsatype.debug(e)
            return False

    def diagnosis_revoke(self, model, cursor, oParam):
        try:
            customer = cursor.valueBuffer("cliente")

            url, frombd = self.get_server_url(customer)
            if not url:
                return False

            if frombd:
                url = "{}/celery/revoke/{}".format(url, oParam["id"])

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

    def get_server_url(self, cliente, force_notdb=False):
        return self.ctx.diagnosis_get_server_url(cliente, force_notdb)

    def get_url(self, cliente, proceso):
        return self.ctx.diagnosis_get_url(cliente, proceso)

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
