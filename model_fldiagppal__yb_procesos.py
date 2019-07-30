# @class_declaration interna_yb_procesos #
from YBUTILS.viewREST import helpers
from models.fldiagppal import models as modelos
import importlib


class interna_yb_procesos(modelos.mtd_yb_procesos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration diagnosis_yb_procesos #
class diagnosis_yb_procesos(interna_yb_procesos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def field_ultsincro(self):
        return form.iface.field_ultsincro(self)

    def field_activo_ext(self):
        return form.iface.field_activo_ext(self)

    @helpers.decoradores.accion(aqparam=["cursor"])
    def start(self, cursor):
        return form.iface.start(self, cursor)

    @helpers.decoradores.accion(aqparam=["cursor"])
    def stop(self, cursor):
        return form.iface.stop(self, cursor)

    @helpers.decoradores.accion(aqparam=["oParam"])
    def startall(self, oParam):
        return form.iface.startall(self, oParam)

    @helpers.decoradores.accion(aqparam=["oParam"])
    def stopall(self, oParam):
        return form.iface.stopall(self, oParam)

    @helpers.decoradores.accion(aqparam=["cursor", "oParam"])
    def revoke(self, cursor, oParam):
        return form.iface.revoke(self, cursor, oParam)


# @class_declaration yb_procesos #
class yb_procesos(diagnosis_yb_procesos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.fldiagppal.yb_procesos_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
