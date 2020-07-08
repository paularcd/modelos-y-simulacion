import numpy as np
from collections import namedtuple
import math
import matplotlib.pyplot as plt

evento = namedtuple('evento', 'tiempo nombre')

def inicializacion(listaEventos):
    global sigue
    global inicio
    inicio = 1
    sigue=1
    listaEventos.append(evento(tiempo=0+reloj, nombre="generarProduccion"))


def generarTiempoEspera():
    return np.random.uniform(2, 4)


def generarEvento(tipo):
    tiempo = generarTiempoEspera()
    if tipo == "generarProduccion":
        listaEventos.append(evento(tiempo=tiempo+reloj, nombre="generarProduccion"))
    elif tipo == "generarDemanda":
        listaEventos.append(evento(tiempo=tiempo+reloj, nombre="generarDemanda"))
    else:
        if tipo == "calcularDemanda":
            listaEventos.append(evento(tiempo=tiempo+reloj, nombre="calcularDemanda"))
        else:

            listaEventos.append(evento(tiempo=tiempo+reloj, nombre="calcularCostoMantenimientoDiario"))
    return tiempo


def removerEvento(e, listaEventos):
    return listaEventos.remove(e)

def procesarEventos(reloj, e, listaEventos):
    global unidades
    global unidadesRestantes
    global demanda
    global sigue
    global inicio
    global turno
    tiempo = 0
    global total
    costo=0
    if (reloj == e.tiempo and "generarProduccion" == e.nombre):
        unidades = generarProduccion()
        removerEvento(e, listaEventos)
        tiempo = generarEvento("generarDemanda")

    elif (reloj == e.tiempo and "generarDemanda" == e.nombre):
        demanda = generarDemanda()
        removerEvento(e, listaEventos)
        tiempo = generarEvento("calcularDemanda")

    elif (reloj == e.tiempo and "calcularDemanda" == e.nombre):
            unidadesRestantes = calcularDemanda(unidades, demanda)
            if (unidadesRestantes < 50 and inicio == 1):
                turno.append(2)
                inicio=0
                removerEvento(e, listaEventos)
                tiempo = generarEvento("generarProduccion")

            else:
                if (inicio==1):
                     turno.append(1)

                removerEvento(e, listaEventos)
                tiempo = generarEvento("calcularCostoMantenimientoDiario")
    else:
            removerEvento(e, listaEventos)
            costo =calcularCostoMantenimientoDiario(unidadesRestantes)
            costosMantenimiento.append(costo)
            sigue = 0

    return tiempo,costo

def generarProduccion():
    global inicio
    if (inicio == 1):
        return 80
    else:
        return 130

def generarDemanda():
    return   math.floor(np.random.normal(150, 25,1))

def calcularDemanda(unidades, demanda):
   return   unidades - demanda

def calcularCostoMantenimientoDiario(unidadesRestantes):
    if (unidadesRestantes>0):
        return unidadesRestantes * 70
    else:
        return 0

def histograma(datos, label, titulo,color):
    kwargs = dict(alpha=0.5, bins=200)
    p=plt.hist(datos, **kwargs, color=color, label=label)
    plt.gca().set(title=titulo)
    plt.legend()
    plt.show()
    plt.close()

def intervaloDeConfianza(media, desvio,total,z):
    inferior=media-(z*(desvio/np.sqrt(total)))
    superior=media+(z*(desvio/np.sqrt(total)))
    return inferior, superior

def calcularMediaDesvio(datos):
    media=np.mean(datos)
    desvioEstandar=np.std(datos)
    return media,desvioEstandar

np.random.seed(43)
total=7500
for h in range(3):
    unidades = 0
    demanda = 0
    listaEventos = []
    reloj = 0
    unidadesRestantes = 0
    sigue = 1
    turno=[]
    costosMantenimiento=[]
    mediat=0
    mediaCM=0
    total=0
    for i in range(30):
        for j in range(250):
            inicializacion(listaEventos)
            while (sigue == 1):
                for e in listaEventos:
                    tiempoT,costo = procesarEventos(reloj, e, listaEventos)
                    reloj += tiempoT
                    total+=costo
    mediaT = np.mean(turno)
    mediaCM,desvio = calcularMediaDesvio(costosMantenimiento)
    i, s = intervaloDeConfianza(mediaCM, desvio, total, 2.57)

    if h==0:
        print("Costos de mantenimiento con 80 unidades iniciales")
        color="cyan"

    elif h==1:
        print("Costos de mantenimiento con 70 unidades iniciales")
        color="magenta"
    else:
        print("Costos de mantenimiento con 60 unidades iniciales")
        color="yellow"
    print("El promedio de turnos necesarios es: " + str(mediaT))
    print("El promedio de costos de mantenimiento anual es: " + str(mediaCM))
    print("El intervalo de confianza es : limite inferior = " + str(i) + "  limite superior = " + str(s))
    histograma(costosMantenimiento, "Promedio de costos de mantenimiento anual", "Histograma", color)
    print("----------------------------------------------------------------")
