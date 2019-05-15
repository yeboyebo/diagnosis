import json

from django.http import HttpResponse

from YBLEGACY import qsatype


# @class_declaration interna_failed #
class interna_failed():
    pass


# @class_declaration diagnosis_failed #
class diagnosis_failed(interna_failed):

    @staticmethod
    def start(pk, data):
        qsatype.FLSqlQuery().execSql("INSERT INTO yb_procesos_erroneos (cliente, proceso, error, codregistro, resuelto, timestamp) VALUES ('{}', '{}', '{}', '{}', {}, '{}')".format(data["customer_name"], data["process_name"], data["error"], data["pk"], False, str(qsatype.Date())))

        return HttpResponse(json.dumps({}), status=200, content_type="application/json")


# @class_declaration failed #
class failed(diagnosis_failed):
    pass
