# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration diagnosis #
import time
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
            {"verbose_name": "ultsincro", "func": "field_ultsincro"}
        ]

        if template.endswith("activity"):
            ff.append({"verbose_name": "activas", "func": "field_activas"})
            ff.append({"verbose_name": "programadas", "func": "field_programadas"})
            ff.append({"verbose_name": "reservadas", "func": "field_reservadas"})

        return ff

    def diagnosis_field_activas(self, model):
        try:
            return cacheController.getSessionVariable("activity")["active"]
        except Exception:
            return None

    def diagnosis_field_programadas(self, model):
        try:
            return cacheController.getSessionVariable("activity")["scheduled"]
        except Exception:
            return None

    def diagnosis_field_reservadas(self, model):
        try:
            return cacheController.getSessionVariable("activity")["reserved"]
        except Exception:
            return None

    def diagnosis_field_ultsincro(self, model):
        q = qsatype.FLSqlQuery()
        q.setSelect("timestamp, texto")
        q.setFrom("yb_log")
        q.setWhere("cliente = '{}' AND tipo = '{}' AND texto LIKE 'Éxito%' ORDER BY timestamp DESC LIMIT 1".format(model.cliente, model.proceso))

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

    def diagnosis_get_server_url(self, cliente, syncapi=None):
        if syncapi:
            q = qsatype.FLSqlQuery()
            q.setSelect("url, test_url")
            q.setFrom("yb_clientessincro")
            q.setWhere("cliente = '{}'".format(cliente))

            if not q.exec_():
                return False

            if q.first():
                url = None
                if qsatype.FLUtil.isInProd():
                    url = q.value("url")
                else:
                    url = q.value("test_url")

                return url
            else:
                return False
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

            return url

    def diagnosis_get_url(self, cliente, proceso, syncapi=None):
        try:
            server_url = self.get_server_url(cliente, syncapi=syncapi)
            if not server_url:
                return False

            if syncapi:
                q = qsatype.FLSqlQuery()
                q.setSelect("url")
                q.setFrom("yb_procesos")
                q.setWhere("cliente = '{}' AND proceso = '{}'".format(cliente, proceso))

                if not q.exec_():
                    return False

                if not q.first():
                    return False

                return "{}/{}".format(server_url, q.value("url"))
            else:
                return "{}/{}".format(server_url, proceso)

        except Exception as e:
            qsatype.debug(e)
            return False

    def diagnosis_get_extra_data(self, cursor):
        extra_data = {}

        if cursor.valueBuffer("syncstore"):
            extra_data["codtienda"] = cursor.valueBuffer("proceso")[-4:].upper()

        return extra_data

    def diagnosis_start(self, model, cursor):
        try:
            if cursor.valueBuffer("activo"):
                return True

            return self.single_start(cursor)

        except Exception as e:
            qsatype.debug(e)
            return False

        return True

    def diagnosis_stop(self, model, cursor):
        if not cursor.valueBuffer("activo"):
            return True

        if not qsatype.FLUtil.sqlUpdate("yb_procesos", ["activo"], [False], "id = {}".format(cursor.valueBuffer("id"))):
            return False

        return True

    def diagnosis_startall(self, model, oParam):
        where = self.get_where_procesos(oParam["mainfilter"])

        cursor = qsatype.FLSqlCursor("yb_procesos")
        cursor.select("{} AND NOT activo".format(where))

        while cursor.next():
            self.single_start(cursor)

        return True

    def diagnosis_stopall(self, model, oParam):
        where = self.get_where_procesos(oParam["mainfilter"])

        if not qsatype.FLUtil.sqlUpdate("yb_procesos", ["activo"], [False], "{} AND activo".format(where)):
            return False

        return True

    def diagnosis_single_start(self, cursor):
        try:
            cliente = cursor.valueBuffer("cliente")
            proceso = cursor.valueBuffer("proceso")
            syncapi = cursor.valueBuffer("syncapi")

            url = self.get_url(cliente, proceso, syncapi)

            if not url:
                return False

            if syncapi:
                header = {"Content-Type": "application/json"}
                data = {
                    "passwd": "bUqfqBMnoH",
                    "continuous": True,
                    "production": qsatype.FLUtil.isInProd()
                }

                data.update(self.get_extra_data(cursor))

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

                if cursor.valueBuffer("syncstore"):
                    data["codtienda"] = url[-4:].upper()
                    url = url[:-4]

                resul = notifications.post_request(url, header, data)

                if not resul:
                    return False

            if not qsatype.FLUtil.sqlUpdate("yb_procesos", ["activo"], [True], "cliente = '{}' AND proceso = '{}'".format(cliente, proceso)):
                return False

            diagppal.iface.log("Info. Proceso arrancado", proceso, cliente)

            return resul

        except Exception as e:
            qsatype.debug(e)
            return False

    def diagnosis_get_where_procesos(self, mainfilter):
        where = ""

        for mfilter in mainfilter:
            a_filter = mfilter.split("_")

            if a_filter[0] != "s":
                continue

            if where != "":
                where = "{} AND ".format(where)

            if a_filter[3] == "exact":
                where = "{}{} = '{}'".format(where, a_filter[1], mainfilter[mfilter])

            elif a_filter[3] == "startswith":
                where = "{}{} LIKE '{}%%'".format(where, a_filter[1], mainfilter[mfilter])

            elif a_filter[3] == "endswith":
                where = "{}{} LIKE '%%{}'".format(where, a_filter[1], mainfilter[mfilter])

        return where

    def diagnosis_getActivity(self, name):
        try:
            customer = name.split("_activity")[0]

            syncapi = False
            if qsatype.FLUtil.sqlSelect("yb_procesos", "id", "cliente = '{}' AND syncapi LIMIT 1".format(customer)):
                syncapi = True

            url = self.get_server_url(customer, syncapi)
            if not url:
                return False

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
            return False

    def diagnosis_revoke(self, model, cursor, oParam):
        try:
            customer = cursor.valueBuffer("cliente")

            syncapi = False
            if qsatype.FLUtil.sqlSelect("yb_procesos", "id", "cliente = '{}' AND syncapi LIMIT 1".format(customer)):
                syncapi = True

            url = self.get_server_url(customer, syncapi)
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

    def get_server_url(self, cliente, syncapi=None):
        return self.ctx.diagnosis_get_server_url(cliente, syncapi)

    def get_url(self, cliente, proceso, syncapi=None):
        return self.ctx.diagnosis_get_url(cliente, proceso, syncapi)

    def get_extra_data(self, cursor):
        return self.ctx.diagnosis_get_extra_data(cursor)

    def start(self, model, cursor):
        return self.ctx.diagnosis_start(model, cursor)

    def stop(self, model, cursor):
        return self.ctx.diagnosis_stop(model, cursor)

    def startall(self, model, oParam):
        return self.ctx.diagnosis_startall(model, oParam)

    def stopall(self, model, oParam):
        return self.ctx.diagnosis_stopall(model, oParam)

    def single_start(self, cursor):
        return self.ctx.diagnosis_single_start(cursor)

    def get_where_procesos(self, mainfilter):
        return self.ctx.diagnosis_get_where_procesos(mainfilter)

    def getActivity(self, name):
        return self.ctx.diagnosis_getActivity(name)

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
