# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration diagnosis #
from YBLEGACY.constantes import *
import datetime


class diagnosis(interna):

    def diagnosis_getForeignFields(self, model, template=None):
        return [{"verbose_name": "conditions", "func": "field_condition"}]

    def diagnosis_field_condition(self, model):
        tipo = qsatype.FLUtil.sqlSelect("yb_regdiagnosis", "tipo", "idreg = " + str(model.idreg))

        if tipo == "Ventas Tpv":
            hMax = datetime.datetime.now() - datetime.timedelta(hours=2)
            hMin = datetime.datetime.now() - datetime.timedelta(hours=4)
            return {
                "ok": model.timestamp >= str(hMax),
                "error": model.timestamp < str(hMin),
                "warn": model.timestamp < str(hMax) and model.timestamp >= str(hMin)
            }
        elif tipo == "Stock":
            hMax = datetime.datetime.now() - datetime.timedelta(hours=24)
            hMin = datetime.datetime.now() - datetime.timedelta(hours=48)
            return {
                "ok": model.timestamp >= str(hMax),
                "error": model.timestamp < str(hMin),
                "warn": model.timestamp < str(hMax) and model.timestamp >= str(hMin)
            }
        elif tipo == "Arqueos Tpv":
            hMax = datetime.datetime.now() - datetime.timedelta(hours=1)
            hMin = datetime.datetime.now() - datetime.timedelta(hours=2)
            return {
                "ok": model.timestamp >= str(hMax),
                "error": model.timestamp < str(hMin),
                "warn": model.timestamp < str(hMax) and model.timestamp >= str(hMin)
            }
        else:
            hMax = datetime.datetime.now() - datetime.timedelta(hours=4)
            hMin = datetime.datetime.now() - datetime.timedelta(hours=8)
            return {
                "ok": model.timestamp >= str(hMax),
                "error": model.timestamp < str(hMin),
                "warn": model.timestamp < str(hMax) and model.timestamp >= str(hMin)
            }

    def __init__(self, context=None):
        super().__init__(context)

    def getForeignFields(self, model, template=None):
        return self.ctx.diagnosis_getForeignFields(model, template)

    def field_condition(self, model):
        return self.ctx.diagnosis_field_condition(model)


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
