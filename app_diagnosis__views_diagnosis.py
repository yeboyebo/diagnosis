# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration diagnosis #
class diagnosis(interna):

    def diagnosis_get_menu(self, menu):
        menu["items"] = []

        menu["items"].append({
            "NAME": "admin",
            "TEXT": "Admin",
            "URL": "diagnosis/yb_clientessincro/master",
            "ICON": "adb",
            "COLOR": "rgb(225, 140, 0)"
        })

        qclientes = self.iface.get_qclientes()
        while qclientes.next():
            menu["items"].append({
                "NAME": "{}".format(qclientes.value("cliente")),
                "TEXT": "{}".format(qclientes.value("descripcion")),
                "URL": "diagnosis/yb_clientessincro/{}".format(qclientes.value("id")),
                "ICON": "settings",
                "COLOR": "rgb(0, 0, 0)"
            })

            if qclientes.value("cliente") == "elganso":
                menu["items"].append({
                    "NAME": "elgansodiagproc",
                    "TEXT": "ELGANSO DIAGNOSIS",
                    "URL": "diagnosis/yb_log/custom/elganso_diagnosis",
                    "ICON": "local_hospital",
                    "COLOR": "rgb(182, 0, 6)"
                })

            qgrupos = self.iface.get_qgrupos(qclientes.value("cliente"))
            while qgrupos.next():
                icon = qgrupos.value("icon")
                rgb = qgrupos.value("rgb")

                menu["items"].append({
                    "NAME": qgrupos.value("codigo"),
                    "TEXT": qgrupos.value("descripcion"),
                    "URL": "diagnosis/yb_gruposprocesos/{}".format(qgrupos.value("id")),
                    "ICON": icon if icon and icon != "" else "language",
                    "COLOR": "rgb(" + rgb + ")" if rgb and rgb != "" else "rgb(0, 103, 186)"
                })

        return menu

    def diagnosis_get_qclientes(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("id, cliente, descripcion")
        q.setFrom("yb_clientessincro")
        q.setWhere("cliente <> 'admin' ORDER BY id")

        if not q.exec():
            print("Not exec")
            return []

        return q

    def diagnosis_get_qgrupos(self, cliente):
        q = qsatype.FLSqlQuery()
        q.setSelect("id, codigo, descripcion, icon, rgb")
        q.setFrom("yb_gruposprocesos")
        q.setWhere("cliente = '{}' ORDER BY id".format(cliente))

        if not q.exec():
            return []

        return q

    def __init__(self, context=None):
        super().__init__(context)

    def get_menu(self, menu):
        return self.ctx.diagnosis_get_menu(menu)

    def get_qclientes(self):
        return self.ctx.diagnosis_get_qclientes()

    def get_qgrupos(self, cliente):
        return self.ctx.diagnosis_get_qgrupos(cliente)


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
