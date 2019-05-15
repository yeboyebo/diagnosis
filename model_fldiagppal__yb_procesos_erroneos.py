# @class_declaration interna_yb_procesos_erroneos #
import importlib

from YBUTILS.viewREST import helpers

from models.fldiagppal import models as modelos


class interna_yb_procesos_erroneos(modelos.mtd_yb_procesos_erroneos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration diagnosis_yb_procesos_erroneos #
class diagnosis_yb_procesos_erroneos(interna_yb_procesos_erroneos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    @helpers.decoradores.accion()
    def resolve(self):
        return form.iface.resolve(self)


# @class_declaration yb_procesos_erroneos #
class yb_procesos_erroneos(diagnosis_yb_procesos_erroneos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.fldiagppal.yb_procesos_erroneos_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
