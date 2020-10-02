from django.shortcuts import render
from AppTestPandemiaVuelo.models import Preguntastes,Tipodocumento,Usuario, Test
from django.utils.datastructures import MultiValueDictKeyError
from datetime import datetime, timezone
from collections import Counter
import random
import pyqrcode
import png
from pyqrcode import QRCode
from PIL import ImageFile, ImageOps, Image

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
        url = str(request.build_absolute_uri)
        print("Parcero esta es la url = "+url)
        # Generate QR code 
        url = pyqrcode.create(url)  
        url.png("media/codigosqr/"+identificacion+".png", scale = 6)
        image = "media/codigosqr/"+identificacion+".png"
        img = ImageFile.Image.open(image)
        obtenerultimoregistro.codigoqr = img
        obtenerultimoregistro.identificacion = identificacion
        obtenerultimoregistro.fechaprueba = datetime.now()   
        nombrescompletos = obtenerultimoregistro.usuario.nombres + " " +obtenerultimoregistro.usuario.apellidos 
        obtenerultimoregistro.save()
        
        return render(request,"mostrarresultados.html",{"nombres":nombrescompletos,"colorqr":obtenerultimoregistro.colorqr})
    return render(request,"preguntas.html",{"validar":validar})
