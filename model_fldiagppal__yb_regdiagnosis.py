# @class_declaration interna_yb_regdiagnosis #
from YBUTILS.viewREST import helpers
from models.fldiagppal import models as diagmodels
import importlib


class interna_yb_regdiagnosis(diagmodels.mtd_yb_regdiagnosis, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration diagnosis_yb_regdiagnosis #
class diagnosis_yb_regdiagnosis(interna_yb_regdiagnosis, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    @helpers.decoradores.csr()
    def checkdiagnosis(params):
        return form.iface.checkdiagnosis(params)

    def field_condition(self):
        return form.iface.field_condition(self)

    @helpers.decoradores.accion()
    def dameSubregistrosDiagnosis(self):
        return form.iface.dameSubregistrosDiagnosis(self)

    def checkDiagnosisElganso(self, cliente, proceso):
        return form.iface.checkDiagnosisElganso(cliente, proceso)


# @class_declaration yb_regdiagnosis #
class yb_regdiagnosis(diagnosis_yb_regdiagnosis, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.fldiagppal.yb_regdiagnosis_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
