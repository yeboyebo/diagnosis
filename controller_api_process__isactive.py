import json

from django.http import HttpResponse

from YBLEGACY import qsatype


# @class_declaration interna_isactive #
class interna_isactive():
    pass


# @class_declaration diagnosis_isactive #
class diagnosis_isactive(interna_isactive):

    @staticmethod
    def start(pk, data):
        result = {"active": False}

        try:
            active = qsatype.FLSqlQuery().execSql("SELECT activo FROM yb_procesos WHERE proceso = '{}'".format(pk))
            if active[0][0]:
                result["active"] = True
        except Exception:
            pass

        return HttpResponse(json.dumps(result), status=200, content_type="application/json")


# @class_declaration isactive #
class isactive(diagnosis_isactive):
    pass
