from django.db import models


class Tipodocumento(models.Model):
    tipodocumento = models.CharField(max_length=30)
    def __str__(self):
        return self.tipodocumento

class Usuario(models.Model):
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    celular = models.CharField(max_length=15)
    correo = models.CharField(max_length=30)
    numerodocumento = models.CharField(max_length=15)
    tipodocumento = models.ForeignKey(Tipodocumento, on_delete=models.CASCADE)
    def __str__(self):
        return self.nombres

class Test(models.Model):
    identificacion = models.CharField(max_length=20,null=True, blank=True)
    codigoqr = models.ImageField(upload_to = 'codigosqr',null=True, blank=True)
    colorqr = models.CharField(max_length=15,null=True, blank=True)
    fechaprueba = models.DateTimeField('date published',null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    def __unicode__(self,):
        return str(self.codigoqr)

class Preguntastest(models.Model):
    pregunta = models.CharField(max_length=80)
    def __str__(self):
        return self.pregunta

class Preguntastestriesgos(models.Model):
    pregunta = models.CharField(max_length=100)
    def __str__(self):
        return self.pregunta
