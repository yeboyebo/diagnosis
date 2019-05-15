import json

from django.http import HttpResponse

from models.fldiagppal import fldiagppal_def as diagppal


# @class_declaration interna_failed #
class interna_failed():
    pass


# @class_declaration diagnosis_failed #
class diagnosis_failed(interna_failed):

    @staticmethod
    def start(pk, data):
        diagppal.iface.failed(data["customer_name"], data["process_name"], data["error"], data["pk"])

        return HttpResponse(json.dumps({"msg": "Proceso erróneo insertado"}), status=200, content_type="application/json")


# @class_declaration failed #
class failed(diagnosis_failed):
    pass
