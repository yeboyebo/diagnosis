from AQNEXT.celery import app
from YBUTILS import globalValues

from controllers.base.default.managers.task_manager import TaskManager

task_manager = TaskManager()

globalValues.registrarmodulos()


@app.task
def startall():
    # Buscar todos los procesos con inicio automatico del cliente (recibimos por param)
    # Vamos llamando uno a uno a inciarse
    pass


@app.task
def stopall():
    # Hacemos un update sobre todos los procesos iniciados del cliente (recibimos por param)
    pass
