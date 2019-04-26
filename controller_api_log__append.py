import json

from django.http import HttpResponse

from models.fldiagppal import fldiagppal_def as diagppal


# @class_declaration interna_append #
class interna_append():
    pass


# @class_declaration diagnosis_append #
class diagnosis_append(interna_append):

    @staticmethod
    def start(pk, data):
        if "log" in data:
            for log in data["log"]:
                diagppal.iface.log("{}. {}".format(log["msg_type"], str(log["msg"]).replace("'", "\"")), log["process_name"], log["customer_name"])
            result = {"msg": "Log insertado"}
        else:
            result = {"msg": "Nada que insertar"}

        return HttpResponse(json.dumps(result), status=200, content_type="application/json")


# @class_declaration append #
class append(diagnosis_append):
    pass
