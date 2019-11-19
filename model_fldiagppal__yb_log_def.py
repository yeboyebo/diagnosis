# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration diagnosis #
from YBLEGACY.constantes import *


class diagnosis(interna):

    def diagnosis_getForeignFields(self, model, template=None):
        fields = [
            {'verbose_name': 'descripcionf', 'func': 'field_descripcion'},
            {'verbose_name': 'timestampf', 'func': 'field_timestamp'},
            {'verbose_name': 'rowColor', 'func': 'field_colorRow'}
        ]
        return fields

    def diagnosis_field_colorRow(self, model):
        try:
            field = model.texto
        except Exception:
            return None

        if field.startswith("Error."):
            return "cDanger"
        elif field.startswith("Info."):
            return "cInfo"
        return None

    def diagnosis_field_descripcion(self, model):
        desc = None
        if isinstance(model, dict):
            desc = model["yb_log.tipo"]
        else:
            desc = model.tipo

        if desc == "diagsincroventasobjeto":
            desc = "Sincro Ventas Objeto"
        elif desc == "diagidlerroneos":
            desc = "Envios a idl"
        elif desc == "diagventastiendaficticia":
            desc = "Ventas tiendas ficticias"
        elif desc == "diagventassinlineas":
            desc = "Ventas sin líneas"
        elif desc == "diagventassinpagos":
            desc = "Ventas sin pagos"
        elif desc == "diagdirectordersnoidl":
            desc = "Direct Order no IDL"
        elif desc == "diagfacturaseci":
            desc = "Facturación ECI"
        elif desc == "diagcontabilidad":
            desc = "Sincro Arqueos"
        elif desc == "diagventaseci":
            desc = "Ventas ECI"
        elif desc == "diagventassinfacturar":
            desc = "Ventas sin facturar"
        elif desc == "diagfacturacionsii":
            desc = "Facturación SII"
        elif desc == "diagfichprocesados":
            desc = "Ficheros procesados"
        elif desc == "diagmovimientosviajes":
            desc = "Movimientos de viajes"
        elif desc == "diagpedidosservidoseditables":
            desc = "Movimientos de viajes"
        elif desc == "diagarticulosidl":
            desc = "Artículos IDL"
        elif desc == "diagclientesidl":
            desc = "Clientes IDL"
        elif desc == "diagproveedoresidl":
            desc = "Proveedores IDL"
        elif desc == "diagpedidoscliidl":
            desc = "Pedidos cliente IDL"
        elif desc == "diagpedidoscdidl":
            desc = "Pedidos Cross Docking IDL"
        elif desc == "diagpedidosprovidl":
            desc = "Pedidos proveedor IDL"
        elif desc == "diagviajesorigenidl":
            desc = "Viajes orignen IDL"
        elif desc == "diagviajesdestinoidl":
            desc = "Viajes destino IDL"
        elif desc == "diagviajescdidl":
            desc = "Viajes Cross Docking IDL"
        elif desc == "diagpedidosecommerceidl":
            desc = "Pedidos ecommerce IDL"
        elif desc == "diagdevecorecibidas":
            desc = "Devoluciones ecommerce recibidas"
        elif desc == "diagdevecomagento":
            desc = "Devoluciones ecommerce no enviadas"
    
        return desc

    def diagnosis_field_timestamp(self, model):
        tm = None
        if isinstance(model, dict):
            tm = model["yb_log.timestamp"]
        else:
            tm = model.timestamp

        stm = str(tm)
        f = stm[:10]
        h = stm[11:19]
        ahora = qsatype.Date()
        if f == ahora.toString()[:10]:
            f = "Hoy"
        elif f == qsatype.FLUtil.addDays(qsatype.Date(), -1)[:10]:
            f = "Ayer"
        else:
            f = qsatype.FLUtil.dateAMDtoDMA(f)

        return f + " - " + h

    def diagnosis_queryGrid_diagnosismonitor(self, template):
        query = {}
        query["tablesList"] = u"yb_log"
        query["select"] = u"yb_log.tipo, yb_log.texto, yb_log.timestamp"
        query["from"] = u"yb_log"
        query["where"] = u"id IN (SELECT MAX(id) FROM yb_log GROUP BY cliente, tipo ORDER BY cliente, tipo) AND yb_log.texto LIKE 'Error.%'"
        query["orderby"] = u"cliente, tipo"
        return query

    def diagnosis_addlog(self, params):
        response = {}
        if "passwd" in params and params['passwd'] == "prnAc9Pgi5uq":
            if "cliente" not in params or "tipo" not in params or "texto" not in params:
                return {"resul": False, "msg": "Formato incorrecto"}
            cliente = params['cliente']
            texto = params['texto']
            tipo = params['tipo']
            tmstmp = qsatype.Date().now()
            tsDel = qsatype.FLUtil.addDays(tmstmp, -5)

            qsatype.FLSqlQuery().execSql("DELETE FROM yb_log WHERE timestamp < '" + tsDel + "' AND tipo ='" + tipo + "' AND cliente = '" + cliente + "'")

            qsatype.FLSqlQuery().execSql("INSERT INTO yb_log (texto, cliente, tipo, timestamp) VALUES ('" + texto + "', '" + cliente + "', '" + tipo + "', '" + tmstmp + "')")
            response["resul"] = True
            response["status"] = "Ok"
        return response

    def __init__(self, context=None):
        super().__init__(context)

    def getForeignFields(self, model, template=None):
        return self.ctx.diagnosis_getForeignFields(model, template)

    def field_timestamp(self, model):
        return self.ctx.diagnosis_field_timestamp(model)

    def field_descripcion(self, model):
        return self.ctx.diagnosis_field_descripcion(model)

    def field_colorRow(self, model):
        return self.ctx.diagnosis_field_colorRow(model)

    def queryGrid_diagnosismonitor(self, template):
        return self.ctx.diagnosis_queryGrid_diagnosismonitor(template)

    def addlog(self, params):
        return self.ctx.diagnosis_addlog(params)


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
