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

        qsatype.FLSqlQuery().execSql("INSERT INTO yb_log (texto, cliente, tipo, timestamp) VALUES ('{}', '{}', '{}', '{}')".format(text, customer, process, tmstmp))

    def diagnosis_failed(self, customer, process, error, pk):
        tmstmp = qsatype.Date().now()
        tsDel = qsatype.FLUtil.addDays(tmstmp, -10)

        qsatype.FLSqlQuery().execSql("DELETE FROM yb_procesos_erroneos WHERE resuelto AND cliente = '{}' AND timestamp < '{}'".format(customer, tsDel))

        qsatype.FLSqlQuery().execSql("INSERT INTO yb_procesos_erroneos (cliente, proceso, error, codregistro, resuelto, timestamp) VALUES ('{}', '{}', '{}', '{}', {}, '{}')".format(customer, process, error, pk, False, tmstmp))

    def __init__(self, context=None):
        super().__init__(context)

    def log(self, text, process, customer):
        return self.ctx.diagnosis_log(text, process, customer)

    def failed(self, customer, process, error, pk):
        return self.ctx.diagnosis_failed(customer, process, error, pk)


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
