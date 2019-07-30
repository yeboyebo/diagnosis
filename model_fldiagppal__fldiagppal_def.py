# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration diagnosis #
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

    def __init__(self, context=None):
        super().__init__(context)

    def log(self, text, process, customer):
        return self.ctx.diagnosis_log(text, process, customer)

    def failed(self, customer, process, error, pk):
        return self.ctx.diagnosis_failed(customer, process, error, pk)

    def get_server_url(self, cliente, syncapi=None):
        return self.ctx.diagnosis_get_server_url(cliente, syncapi)


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
