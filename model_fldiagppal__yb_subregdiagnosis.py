# @class_declaration interna_yb_subregdiagnosis #
from YBUTILS.viewREST import helpers
from models.fldiagppal import models as diagmodels
import importlib


class interna_yb_subregdiagnosis(diagmodels.mtd_yb_subregdiagnosis, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration diagnosis_yb_subregdiagnosis #
class diagnosis_yb_subregdiagnosis(interna_yb_subregdiagnosis, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def field_condition(self):
        return form.iface.field_condition(self)


# @class_declaration yb_subregdiagnosis #
class yb_subregdiagnosis(diagnosis_yb_subregdiagnosis, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.fldiagppal.yb_subregdiagnosis_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
