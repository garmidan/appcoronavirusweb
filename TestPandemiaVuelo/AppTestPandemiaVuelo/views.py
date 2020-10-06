from django.shortcuts import render, redirect
from AppTestPandemiaVuelo.models import Preguntastest,Tipodocumento,Usuario, Test, Preguntastestriesgos
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

def inicio(request):
    return render(request,"inicio.html")

#CONSULTAR TEST
def consultar(request):
    validar = 0
    if request.method == 'POST':
        cedulaconsultar = request.POST["cedulaconsultar"]
        correoconsultar = request.POST["correoconsultar"]
        if Usuario.objects.filter(numerodocumento=cedulaconsultar,correo=correoconsultar).exists():
            usuarioconsultado = Usuario.objects.get(numerodocumento=cedulaconsultar)
            if Test.objects.filter(usuario=usuarioconsultado).exists():
                validar = 3
                ultimotest = Test.objects.filter(usuario=usuarioconsultado).last()
                hora_actual = datetime.now()
                fecharegistro = datetime.date(ultimotest.fechaprueba)
                horaregistro = datetime.time(ultimotest.fechaprueba)
                combinacionfechabase = datetime.combine(fecharegistro,horaregistro)
                total = (hora_actual-combinacionfechabase).total_seconds()
                minutos = total / 60
                horas = minutos / 60
                if horas >=24:
                    return render(request,"resultadoconsulta.html",{"usuarioconsultado":usuarioconsultado,"validar":validar,"ultimotest":ultimotest})
                else:   
                    validahorita = 1  
                    return render(request,"resultadoconsulta.html",{"usuarioconsultado":usuarioconsultado,"validar":validar,"ultimotest":ultimotest,"validahorita":validahorita})
            else:
                validar = 2
                return render(request,"resultadoconsulta.html",{"usuarioconsultado":usuarioconsultado,"validar":validar})
            return render(request,"resultadoconsulta.html",{"usuarioconsultado":usuarioconsultado})
        else:
            validar = 1
            return render(request,"consultar.html",{"validar":validar})
    return render(request,"consultar.html")

def reenviar(request):
    mensaje = 0
    if request.method == 'POST':
        correo = request.POST["reenviar"]
        urlimagen = request.POST["urlimagen"]
        try:  
            #ENVIO DE CORREO
            imgfilename  = "media/codigosqr/"+urlimagen+".png"
            subject = "Reenvio Codigo QR"
            img_data = open(imgfilename, 'rb').read()
            msg = MIMEMultipart()
            msg['Subject'] = subject
            envia = settings.EMAIL_HOST_USER
            recibe= correo
            text = MIMEText("Este es su codigo QR para presentar en el aeropuerto")
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
            #ENVIO DE CORREO
            mensaje = 1
            return redirect("../consultar")
        except IOError: 
            print("error al enviar correo con imagen")
    else:
        return render(request,"resultadoconsulta.html",{"mensaje":mensaje})
    return render(request,"resultadoconsulta.html",{"mensaje":mensaje})
#TERMINACION CONSULTAR TEST
#OPCION DE REALIZAR NUEVO TEST
def realizartest(request):
    preguntas = Preguntastest.objects.all()
    if request.method == 'POST':
        validacion = 0
        cedulaconsultartest = request.POST["cedulaconsultar"]
        if Usuario.objects.filter(numerodocumento=cedulaconsultartest).exists():
            usuarioconsultadotest = Usuario.objects.get(numerodocumento=cedulaconsultartest)
            if Test.objects.filter(usuario=usuarioconsultadotest).exists():
                ultimotesting = Test.objects.filter(usuario=usuarioconsultadotest).last()
                hora_actual = datetime.now()
                fecharegistro = datetime.date(ultimotesting.fechaprueba)
                horaregistro = datetime.time(ultimotesting.fechaprueba)
                combinacionfechabase = datetime.combine(fecharegistro,horaregistro)
                total = (hora_actual-combinacionfechabase).total_seconds()
                minutos = total / 60
                horas = minutos / 60
                if horas >=24:
                    validatest = 1
                    identificacion = random.randrange(1000000000000000000,100000000000000000000)
                    return render(request,"realizartesnuevo.html",{"preguntas":preguntas,"usuariotest":usuarioconsultadotest,"validatest":validatest,"identificacionnuevotest":identificacion})
                else:
                    validacion = 3
                    imgfilename  = "media/codigosqr/"+ultimotesting.identificacion+".png"
                    subject = "Reenvio Codigo QR"
                    img_data = open(imgfilename, 'rb').read()
                    msg = MIMEMultipart()
                    msg['Subject'] = subject
                    envia = settings.EMAIL_HOST_USER
                    recibe= usuarioconsultadotest.correo
                    text = MIMEText("Este es su codigo QR para presentar en el aeropuerto")
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
                    return render(request,"resultadoconsulta.html",{"validacion":validacion,"usuario":usuarioconsultadotest,"resultadotest":ultimotesting})
            else:
               validacion = 2 
               return render(request,"testnuevo.html",{"validacion":validacion})
        else:
            validacion = 1
    return render(request,"testnuevo.html")

def nuevotest(request,identificacionnuevotest,numerodocument):
    si = 0
    no = 0
    colorqr = ""
    if request.method == 'POST':
        for preguntas in Preguntastest.objects.all():
            try:
                sipreguntastestnuevo = request.POST["si"+str(preguntas.id)]
                si = si + 1
            except MultiValueDictKeyError:
                no = no + 1
        usuarionuevotest = Usuario.objects.get(numerodocumento=numerodocument)
        fecha_actual = datetime.now()
        if si >=2:
            colorqr = "Rojo"
        elif si == 1:
            colorqr = "Amarillo"
        elif si <= 0:
            colorqr = "Verde"
        print(request.build_absolute_uri)
        testnuevoregistro = Test(fechaprueba=fecha_actual,identificacion=identificacionnuevotest,usuario=usuarionuevotest,
        colorqr=colorqr)     
        print("El color es = "+colorqr)
        validatetipotest = 2
        return render(request,"mostrarresultados.html",{"validatetipotest":validatetipotest,"colorqr":colorqr,"usuario":usuarionuevotest})
        # Generate QR code 
    return render(request,"testnuevo.html")

#TERMINACION PARTE REALIZAR NUEVO TEST

#PARTE REGISTRAR CON SU RESULTADO
def registrar(request):
    validar = 0
    listtipodocument = Tipodocumento.objects.all()
    if request.method == 'POST':
        listapreguntas = Preguntastest.objects.all()
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
                validar = 1
            else:
                if Usuario.objects.filter(correo=correo).exists():
                    validar = 2
                else:
                    documento = Tipodocumento(id=tipodocumento)
                    guardarusuario = Usuario(tipodocumento=documento,nombres=nombres,apellidos=apellidos
                    ,celular=celular,correo=correo,numerodocumento=numerodocumento)
                    guardarusuario.save()
                    usuarionumerodocumento = Usuario.objects.get(numerodocumento=numerodocumento)
                    guardarTest = Test(usuario=usuarionumerodocumento)
                    guardarTest.save()
                    return render(request,"preguntas.html",{"preguntas":listapreguntas,"validar":validar})  
            
    return render(request,"registro.html",{"listtipodocumento":listtipodocument,"validar":validar})

def sintomas(request):
    listpreguntas = Preguntastest.objects.all()
    listariesgos = Preguntastestriesgos.objects.all()
    validar = "no puede ver los resultados sin primero registrarse no debe saltearse ningun paso"
    si = 0
    validarsintomas = ""
    no = 0
    if request.method == 'POST':
        for preguntas in listpreguntas:
            try:
                sipreguntas = request.POST["si"+str(preguntas.id)]
                if sipreguntas == "Fiebre" or sipreguntas == "Dificultad para respirar":
                    validarsintomas = "yes"
                else:
                    si = si + 1
            except MultiValueDictKeyError:
                no = no + 1
        obtenerultimoregistro = Test.objects.last()
        identificacion = random.randrange(1000000000000000000,100000000000000000000)
        if validarsintomas == "yes":
            obtenerultimoregistro.colorqr = "Rojo"
        else:       
            if si >=3:
                obtenerultimoregistro.colorqr = "Rojo"
            elif si == 2:
                obtenerultimoregistro.colorqr = "Amarillo"
            elif si <= 1:
                obtenerultimoregistro.colorqr = "Verde"
        obtenerultimoregistro.save()
        validatetipotest = 1
        return render(request,"riesgos.html",{"idtest":obtenerultimoregistro.id,"validatetipotest":validatetipotest,"identificacion":identificacion,"listariesgos":listariesgos})
    return render(request,"preguntas.html",{"validar":validar})


def resultado(request,identificacion):
    listpreguntas = Preguntastestriesgos.objects.all()
    validar = "no puede ver los resultados sin primero registrarse no debe saltearse ningun paso"
    si = 0
    no = 0
    if request.method == 'POST':
        idtest = request.POST["idtest"]
        for preguntas in listpreguntas:
            try:
                sipreguntas = request.POST["si"+str(preguntas.id)]
                si = si + 1
            except MultiValueDictKeyError:
                no = no + 1
        obtenerultimoregistro = Test.objects.get(id=idtest)
         # Generate QR code 
        url = pyqrcode.create("https://github.com/garmidan/appcoronavirusweb")  
        url.png("media/codigosqr/"+identificacion+".png", scale = 6)
        obtenerultimoregistro.codigoqr = "codigosqr/"+identificacion+".png"
        obtenerultimoregistro.identificacion = identificacion
        obtenerultimoregistro.fechaprueba = datetime.now()   
        nombrescompletos = obtenerultimoregistro.usuario.nombres + " " +obtenerultimoregistro.usuario.apellidos 
        try:  
            imgfilename  = "media/codigosqr/"+identificacion+".png"
            subject = "Test"
            img_data = open(imgfilename, 'rb').read()
            msg = MIMEMultipart()
            msg['Subject'] = subject
            envia = settings.EMAIL_HOST_USER
            recibe= obtenerultimoregistro.usuario.correo
            text = MIMEText("Este es su codigo QR para presentar en el aeropuerto")
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
        if obtenerultimoregistro.colorqr == "Amarillo" or obtenerultimoregistro.colorqr == "Rojo":
            color = obtenerultimoregistro.colorqr
            obtenerultimoregistro.colorqr = color
        else:
            if si >=1:
                obtenerultimoregistro.colorqr = "Amarillo"
            elif si == 0:
                obtenerultimoregistro.colorqr = "Verde"
        obtenerultimoregistro.save()
        validatetipotest = 1
        return render(request,"mostrarresultados.html",{"nombres":nombrescompletos,"colorqr":obtenerultimoregistro.colorqr,"validatetipotest":validatetipotest})
    return render(request,"preguntas.html",{"validar":validar})

#TERMINACION PARTE REGISTRAR CON SU RESULTADO
