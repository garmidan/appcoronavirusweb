from django.contrib import admin
from AppTestPandemiaVuelo.models import Preguntastest,Tipodocumento,Usuario, Test, Preguntastestriesgos

admin.site.register(Preguntastest)
admin.site.register(Preguntastestriesgos)
admin.site.register(Tipodocumento)
admin.site.register(Usuario)
admin.site.register(Test)
