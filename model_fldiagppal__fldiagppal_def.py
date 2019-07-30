# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration diagnosis #
from YBUTILS import notifications


class diagnosis(interna):

    def diagnosis_log(self, text, process, customer):
        tmstmp = qsatype.Date().now()
        tsDel = qsatype.FLUtil.addDays(tmstmp, -5)

        qsatype.FLSqlQuery().execSql("DELETE FROM yb_log WHERE cliente = '{}' AND tipo = '{}' AND timestamp < '{}'".format(customer, process, tsDel))

        grupoprocesos = qsatype.FLUtil.sqlSelect("yb_procesos", "grupoprocesos", "cliente = '{}' AND proceso = '{}'".format(customer, process))

        qsatype.FLSqlQuery().execSql("INSERT INTO yb_log (texto, cliente, tipo, grupoprocesos, timestamp) VALUES ('{}', '{}', '{}', '{}', '{}')".format(text, customer, process, grupoprocesos, tmstmp))

    def diagnosis_failed(self, customer, process, error, pk):
        tmstmp = qsatype.Date().now()
        tsDel = qsatype.FLUtil.addDays(tmstmp, -10)

        qsatype.FLSqlQuery().execSql("DELETE FROM yb_procesos_erroneos WHERE resuelto AND cliente = '{}' AND timestamp < '{}'".format(customer, tsDel))

        grupoprocesos = qsatype.FLUtil.sqlSelect("yb_procesos", "grupoprocesos", "cliente = '{}' AND proceso = '{}'".format(customer, process))

        qsatype.FLSqlQuery().execSql("INSERT INTO yb_procesos_erroneos (cliente, proceso, grupoprocesos, error, codregistro, resuelto, timestamp) VALUES ('{}', '{}', '{}', '{}', '{}', {}, '{}')".format(customer, process, grupoprocesos, error, pk, False, tmstmp))

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

    def diagnosis_single_start(self, cursor):
        try:
            if cursor.valueBuffer("activo"):
                return True

            cliente = cursor.valueBuffer("cliente")
            proceso = cursor.valueBuffer("proceso")
            syncapi = cursor.valueBuffer("syncapi")

            url = self.iface.get_url(cliente, proceso, syncapi)

            if not url:
                return False

            if not qsatype.FLUtil.sqlUpdate("yb_procesos", ["activo"], [True], "cliente = '{}' AND proceso = '{}'".format(cliente, proceso)):
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
                    if not qsatype.FLUtil.sqlUpdate("yb_procesos", ["activo"], [False], "cliente = '{}' AND proceso = '{}'".format(cliente, proceso)):
                        return False
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
                    data["codtienda"] = url[-4:]
                    url = url[:-4]

                resul = notifications.post_request(url, header, data)

                if not resul:
                    if not qsatype.FLUtil.sqlUpdate("yb_procesos", ["activo"], [False], "cliente = '{}' AND proceso = '{}'".format(cliente, proceso)):
                        return False
                    return False

            return resul

        except Exception as e:
            qsatype.debug(e)
            return False

    def diagnosis_get_extra_data(self, cursor):
        extra_data = {}

        if cursor.valueBuffer("syncstore"):
            extra_data["codtienda"] = cursor.valueBuffer("proceso")[-4:].upper()

        return extra_data

    def __init__(self, context=None):
        super().__init__(context)

    def log(self, text, process, customer):
        return self.ctx.diagnosis_log(text, process, customer)

    def failed(self, customer, process, error, pk):
        return self.ctx.diagnosis_failed(customer, process, error, pk)

    def get_server_url(self, cliente, syncapi=None):
        return self.ctx.diagnosis_get_server_url(cliente, syncapi)

    def get_url(self, cliente, proceso, syncapi=None):
        return self.ctx.diagnosis_get_url(cliente, proceso, syncapi)

    def single_start(self, cursor):
        return self.ctx.diagnosis_single_start(cursor)

    def get_extra_data(self, cursor):
        return self.ctx.diagnosis_get_extra_data(cursor)


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


form = FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
iface = form.iface
