from django.shortcuts import render
from AppTestPandemiaVuelo.models import Preguntastes,Tipodocumento,Usuario, Test
from django.utils.datastructures import MultiValueDictKeyError
from datetime import datetime, timezone
from collections import Counter
import random
import pyqrcode
import png
from pyqrcode import QRCode
from pathlib import Path
from PIL import Image  
import PIL 
from django.conf import settings
from django.core.mail import send_mail
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def registrar(request):
    validahora = 0
    sumita = 0
    listtipodocument = Tipodocumento.objects.all()
    if request.method == 'POST':
        listapreguntas = Preguntastes.objects.all()
        nombres = request.POST["nombres"]
        apellidos = request.POST["apellidos"]
        tipodocumento = request.POST["tipodocumento"]
        numerodocumento = request.POST["numerodocumento"]
        correo = request.POST["correo"]
        validarcorreo = request.POST["confirmarcorreo"]
        celular = request.POST["celular"]
        identificacion = random.randrange(1000000000000000000,100000000000000000000)
        if validarcorreo == correo:
            if Usuario.objects.filter(numerodocumento=numerodocumento).exists():
                existusuario = Usuario.objects.get(numerodocumento=numerodocumento)
                if Test.objects.filter(usuario=existusuario).exists():
                    existest = Test.objects.get(usuario=existusuario)
                    hora_actual = datetime.now()
                    fecharegistro = datetime.date(existest.fechaprueba)
                    horaregistro = datetime.time(existest.fechaprueba)
                    combinacionfechabase = datetime.combine(fecharegistro,horaregistro)
                    total = (hora_actual-combinacionfechabase).total_seconds()
                    minutos = total / 60
                    horas = minutos / 60
                    if horas >=24:
                        guardartestnuevo = Test(usuario=existusuario)
                        guardartestnuevo.save()
                        return render(request,"preguntas.html",{"preguntas":listapreguntas,"validahora":validahora})
                    else:
                        validahora = 1
                        return render(request,"registro.html",{"listtipodocumento":listtipodocument,"validahora":validahora})
                else:
                    guardartestnuevo1 = Test(usuario=existusuario)
                    guardartestnuevo1.save()
                    return render(request,"preguntas.html",{"preguntas":listapreguntas,"validahora":validahora})
            else:
                documento = Tipodocumento(id=tipodocumento)
                guardarusuario = Usuario(tipodocumento=documento,nombres=nombres,apellidos=apellidos
                ,celular=celular,correo=correo,numerodocumento=numerodocumento)
                guardarusuario.save()
                usuarionumerodocumento = Usuario.objects.get(numerodocumento=numerodocumento)
                guardarTest = Test(usuario=usuarionumerodocumento)
                guardarTest.save()
                return render(request,"preguntas.html",{"preguntas":listapreguntas,"validahora":validahora,"identificacion":identificacion})
        else:
            validahora = 2   
            
    return render(request,"registro.html",{"listtipodocumento":listtipodocument,"validahora":validahora})

def resultado(request,identificacion):
    listpreguntas = Preguntastes.objects.all()
    validar = "no puede ver los resultados sin primero registrarse no debe saltearse ningun paso"
    si = 0
    no = 0
    if request.method == 'POST':
        for preguntas in listpreguntas:
            try:
                sipreguntas = request.POST["si"+str(preguntas.id)]
                si = si + 1
            except MultiValueDictKeyError:
                no = no + 1
        obtenerultimoregistro = Test.objects.last()        
        if si >=2:
            obtenerultimoregistro.colorqr = "Rojo"
        elif si == 1:
            obtenerultimoregistro.colorqr = "Amarillo"
        elif si <= 0:
            obtenerultimoregistro.colorqr = "Verde"
        print(request.build_absolute_uri)
        # Generate QR code 
        url = pyqrcode.create("https://github.com/garmidan/appcoronavirusweb")  
        url.png("media/codigosqr/"+identificacion+".png", scale = 6)
        obtenerultimoregistro.codigoqr = "codigosqr/"+identificacion+".png"
        obtenerultimoregistro.identificacion = identificacion
        obtenerultimoregistro.fechaprueba = datetime.now()   
        nombrescompletos = obtenerultimoregistro.usuario.nombres + " " +obtenerultimoregistro.usuario.apellidos 
        obtenerultimoregistro.save()
        try:  
            imgfilename  = "media/codigosqr/"+identificacion+".png"
            subject = "Test"
            img_data = open(imgfilename, 'rb').read()
            msg = MIMEMultipart()
            envia = settings.EMAIL_HOST_USER
            recibe= obtenerultimoregistro.usuario.correo
            text = MIMEText("test")
            msg.attach(text)
            image = MIMEImage(img_data, name=os.path.basename(imgfilename))
            msg.attach(image)
            s = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            s.sendmail(envia, recibe, msg.as_string())
            s.quit()
        except IOError: 
            print("errro al enviar correo con")
        return render(request,"mostrarresultados.html",{"nombres":nombrescompletos,"colorqr":obtenerultimoregistro.colorqr})
    return render(request,"preguntas.html",{"validar":validar})
