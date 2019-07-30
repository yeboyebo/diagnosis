from AQNEXT.celery import app
from YBLEGACY import qsatype
from YBUTILS import globalValues
from YBUTILS import DbRouter

from controllers.base.default.managers.task_manager import TaskManager

from models.fldiagppal import fldiagppal_def as diagppal

task_manager = TaskManager()

globalValues.registrarmodulos()


@app.task
def startall(customer, in_production):
    server_port = "24100" if in_production else "9000"
    virtual_env = "/var/www/django/docker_diagnosis" if in_production else "/var/www/django/dev"

    DbRouter.ThreadLocalMiddleware.process_request_celery(None, {
            "name": "fake",
            "user": "sincro_user",
            "META": {
                "SERVER_PORT": server_port,
                "VIRTUAL_ENV": virtual_env
        }
    })

    cursor = qsatype.FLSqlCursor("yb_procesos")
    cursor.select("cliente = '{}' AND NOT activo AND syncauto AND (NOT syncrecieve OR syncrecieve IS NULL)".format(customer))

    correctos = 0
    erroneos = 0

    diagppal.iface.log("Info. Comenzando el arrancado de procesos de {} ({} procesos)".format(customer, cursor.size()), "admin", "admin")

    while cursor.next():
        resul = diagppal.iface.single_start(cursor, in_production=in_production)
        if resul and "msg" in resul and resul["msg"] == "Tarea encolada correctamente":
            diagppal.iface.log("Éxito. Proceso {} de {} arrancado".format(cursor.valueBuffer("proceso"), customer), "admin", "admin")
            diagppal.iface.log("Info. Proceso arrancado", cursor.valueBuffer("proceso"), customer)
            correctos += 1
        else:
            diagppal.iface.log("Error. Proceso {} de {} no arrancado".format(cursor.valueBuffer("proceso"), customer), "admin", "admin")
            erroneos += 1

    diagppal.iface.log("Info. Terminado el arrancado de procesos de {} ({} correctos, {} erroneos)".format(customer, correctos, erroneos), "admin", "admin")

    return True
