# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration diagnosis #
from YBLEGACY.constantes import *
from YBUTILS.viewREST import cacheController


class diagnosis(interna):

    def diagnosis_getDesc(self):
        return "descripcion"

    def diagnosis_drawif_procesosgrid(self, cursor):
        if self.iface.get_estado() != "procesos":
            return "hidden"

    def diagnosis_drawif_botonprocesos(self, cursor):
        if self.iface.get_estado() == "procesos":
            return "disabled"

    def diagnosis_drawif_erroneosgrid(self, cursor):
        if self.iface.get_estado() != "erroneos":
            return "hidden"

    def diagnosis_drawif_botonerroneos(self, cursor):
        if self.iface.get_estado() == "erroneos":
            return "disabled"

    def diagnosis_drawif_loggrid(self, cursor):
        if self.iface.get_estado() != "log":
            return "hidden"

    def diagnosis_drawif_botonlog(self, cursor):
        if self.iface.get_estado() == "log":
            return "disabled"

    def diagnosis_drawif_configform(self, cursor):
        if self.iface.get_estado() != "config":
            return "hidden"

    def diagnosis_drawif_botonconfig(self, cursor):
        if self.iface.get_estado() == "config":
            return "disabled"

    def diagnosis_get_estado(self):
        estado = cacheController.getSessionVariable("estado_gruposprocesos", None)

        if not estado:
            self.iface.set_estado("procesos")
            estado = "procesos"

        return estado

    def diagnosis_set_estado(self, estado):
        cacheController.setSessionVariable("estado_gruposprocesos", estado)
        return True

    def __init__(self, context=None):
        super().__init__(context)

    def getDesc(self):
        return self.ctx.diagnosis_getDesc()

    def drawif_procesosgrid(self, cursor):
        return self.ctx.diagnosis_drawif_procesosgrid(cursor)

    def drawif_botonprocesos(self, cursor):
        return self.ctx.diagnosis_drawif_botonprocesos(cursor)

    def drawif_erroneosgrid(self, cursor):
        return self.ctx.diagnosis_drawif_erroneosgrid(cursor)

    def drawif_botonerroneos(self, cursor):
        return self.ctx.diagnosis_drawif_botonerroneos(cursor)

    def drawif_loggrid(self, cursor):
        return self.ctx.diagnosis_drawif_loggrid(cursor)

    def drawif_botonlog(self, cursor):
        return self.ctx.diagnosis_drawif_botonlog(cursor)

    def drawif_configform(self, cursor):
        return self.ctx.diagnosis_drawif_configform(cursor)

    def drawif_botonconfig(self, cursor):
        return self.ctx.diagnosis_drawif_botonconfig(cursor)

    def get_estado(self):
        return self.ctx.diagnosis_get_estado()

    def set_estado(self, estado):
        return self.ctx.diagnosis_set_estado(estado)


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
