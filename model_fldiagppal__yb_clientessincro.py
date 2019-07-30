# @class_declaration interna_yb_clientessincro #
import importlib

from YBUTILS.viewREST import helpers

from models.fldiagppal import models as modelos


class interna_yb_clientessincro(modelos.mtd_yb_clientessincro, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration diagnosis_yb_clientessincro #
class diagnosis_yb_clientessincro(interna_yb_clientessincro, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def drawif_gruposgrid(cursor):
        return form.iface.drawif_gruposgrid(cursor)

    def drawif_botongrupos(cursor):
        return form.iface.drawif_botongrupos(cursor)

    @helpers.decoradores.accion(aqparam=[])
    def set_estado_grupos(self):
        return form.iface.set_estado("grupos")

    def drawif_activitybox(cursor):
        return form.iface.drawif_activitybox(cursor)

    def drawif_botonactivity(cursor):
        return form.iface.drawif_botonactivity(cursor)

    @helpers.decoradores.accion(aqparam=[])
    def set_estado_activity(self):
        return form.iface.set_estado("activity")

    def drawif_configform(cursor):
        return form.iface.drawif_configform(cursor)

    def drawif_botonconfig(cursor):
        return form.iface.drawif_botonconfig(cursor)

    @helpers.decoradores.accion(aqparam=[])
    def set_estado_config(self):
        return form.iface.set_estado("config")

    def field_activas(self):
        return form.iface.field_activas(self)

    def field_programadas(self):
        return form.iface.field_programadas(self)

    def field_reservadas(self):
        return form.iface.field_reservadas(self)


# @class_declaration yb_clientessincro #
class yb_clientessincro(diagnosis_yb_clientessincro, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.fldiagppal.yb_clientessincro_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
