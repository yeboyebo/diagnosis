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

        qsatype.FLSqlQuery().execSql("DELETE FROM yb_log WHERE timestamp < '{}'".format(tsDel))

        qsatype.FLSqlQuery().execSql("INSERT INTO yb_log (texto, cliente, tipo, timestamp) VALUES ('{}', '{}', '{}', '{}')".format(text, customer, process, tmstmp))

    def __init__(self, context=None):
        super().__init__(context)

    def log(self, text, process, customer):
        return self.ctx.diagnosis_log(text, process, customer)


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
