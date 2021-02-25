# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration diagnosis #
from YBUTILS import notifications
from models.flsyncppal import flsyncppal_def as syncppal


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

    def diagnosis_get_server_url(self, cliente, syncapi=None, in_production=None):
        if syncapi:
            q = qsatype.FLSqlQuery()
            q.setSelect("url, test_url")
            q.setFrom("yb_clientessincro")
            q.setWhere("cliente = '{}'".format(cliente))

            if not q.exec_():
                return False

            if q.first():
                url = None
                if in_production:
                    url = q.value("url")
                else:
                    url = q.value("test_url")

                return url
            else:
                return False
        else:
            if in_production:
                if cliente == "elganso":
                    url = "https://api.elganso.com"
                elif cliente == "guanabana":
                    url = "http://api.guanabana.store:8080"
                elif cliente == "sanhigia":
                    url = "http://sincroweb.sanhigia.com:9000"
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

    def diagnosis_get_url(self, cliente, proceso, syncapi=None, in_production=None):
        try:
            server_url = self.get_server_url(cliente, syncapi=syncapi, in_production=in_production)
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

    def diagnosis_single_start(self, cursor, in_production=None):
        try:
            if cursor.valueBuffer("activo"):
                return True

            cliente = cursor.valueBuffer("cliente")
            proceso = cursor.valueBuffer("proceso")
            syncapi = cursor.valueBuffer("syncapi")

            url = self.iface.get_url(cliente, proceso, syncapi, in_production)

            if not url:
                return False

            if not qsatype.FLUtil.sqlUpdate("yb_procesos", ["activo"], [True], "cliente = '{}' AND proceso = '{}'".format(cliente, proceso)):
                return False

            if syncapi:
                header = {"Content-Type": "application/json"}
                data = {
                    "passwd": cursor.valueBuffer("passwd"),
                    "continuous": True,
                    "production": in_production
                }

                data.update(self.get_extra_data(cursor))

                resul = notifications.post_request(url, header, data)

                if not resul:
                    if not qsatype.FLUtil.sqlUpdate("yb_procesos", ["activo"], [False], "cliente = '{}' AND proceso = '{}'".format(cliente, proceso)):
                        return False
                    return False
            else:
                server_port = "24100" if in_production else "9000"
                virtual_env = "/var/www/django/docker_diagnosis" if in_production else "/var/www/django/dev"

                header = {"Content-Type": "application/json"}
                data = {
                    "passwd": cursor.valueBuffer("passwd"),
                    "fakeRequest": {
                        "name": "fake",
                        "user": "sincro_user",
                        "META": {
                            "SERVER_PORT": server_port,
                            "VIRTUAL_ENV": virtual_env
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

    def get_server_url(self, cliente, syncapi=None, in_production=None):
        return self.ctx.diagnosis_get_server_url(cliente, syncapi, in_production)

    def get_url(self, cliente, proceso, syncapi=None, in_production=None):
        return self.ctx.diagnosis_get_url(cliente, proceso, syncapi, in_production)

    def single_start(self, cursor, in_production=None):
        return self.ctx.diagnosis_single_start(cursor, in_production)

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
