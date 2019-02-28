# @class_declaration interna_yb_log #
from YBUTILS.viewREST import helpers
from models.fldiagppal import models as modelos
import importlib


class interna_yb_log(modelos.mtd_yb_log, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration diagnosis_yb_log #
class diagnosis_yb_log(interna_yb_log, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def queryGrid_diagnosismonitor(template):
        return form.iface.queryGrid_diagnosismonitor(template)

    def field_timestamp(self):
        return form.iface.field_timestamp(self)

    def field_descripcion(self):
        return form.iface.field_descripcion(self)

    def field_colorRow(self):
        return form.iface.field_colorRow(self)

    @helpers.decoradores.csr()
    def addlog(params):
        return form.iface.addlog(params)


# @class_declaration yb_log #
class yb_log(diagnosis_yb_log, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.fldiagppal.yb_log_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
