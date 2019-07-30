# @class_declaration interna_yb_gruposprocesos #
import importlib

from YBUTILS.viewREST import helpers

from models.fldiagppal import models as modelos


class interna_yb_gruposprocesos(modelos.mtd_yb_gruposprocesos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration diagnosis_yb_gruposprocesos #
class diagnosis_yb_gruposprocesos(interna_yb_gruposprocesos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def drawif_procesosgrid(cursor):
        return form.iface.drawif_procesosgrid(cursor)

    def drawif_botonprocesos(cursor):
        return form.iface.drawif_botonprocesos(cursor)

    @helpers.decoradores.accion(aqparam=[])
    def set_estado_procesos(self):
        return form.iface.set_estado("procesos")

    def drawif_erroneosgrid(cursor):
        return form.iface.drawif_erroneosgrid(cursor)

    def drawif_botonerroneos(cursor):
        return form.iface.drawif_botonerroneos(cursor)

    @helpers.decoradores.accion(aqparam=[])
    def set_estado_erroneos(self):
        return form.iface.set_estado("erroneos")

    def drawif_loggrid(cursor):
        return form.iface.drawif_loggrid(cursor)

    def drawif_botonlog(cursor):
        return form.iface.drawif_botonlog(cursor)

    @helpers.decoradores.accion(aqparam=[])
    def set_estado_log(self):
        return form.iface.set_estado("log")

    def drawif_configform(cursor):
        return form.iface.drawif_configform(cursor)

    def drawif_botonconfig(cursor):
        return form.iface.drawif_botonconfig(cursor)

    @helpers.decoradores.accion(aqparam=[])
    def set_estado_config(self):
        return form.iface.set_estado("config")


# @class_declaration yb_gruposprocesos #
class yb_gruposprocesos(diagnosis_yb_gruposprocesos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.fldiagppal.yb_gruposprocesos_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
