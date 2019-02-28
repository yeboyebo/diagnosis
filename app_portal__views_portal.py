
# @class_declaration diagnosis #
from YBSYSTEM.models.flsisppal.sis_usernotifications import sis_usernotifications
from django.shortcuts import render


class diagnosis(interna):

    def diagnosis_setToken(self, request, param):
        usr = qsatype.FLUtil.nameUser()

        newtoken = sis_usernotifications(usuario=usr, token=param, fechaalta=qsatype.Date().toString()[:10])
        newtoken.save()

        return render(request, 'login/login.html')

    def __init__(self, context=None):
        super().__init__(context)

    def setToken(self, request, param):
        return self.ctx.diagnosis_setToken(request, param)

