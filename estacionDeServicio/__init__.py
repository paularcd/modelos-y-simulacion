import numpy as np
import simpy
import matplotlib.pyplot as plt
from random import *
from collections import namedtuple
import time

ocupacionSurtidor1 = 0
ocupacionSurtidor2 = 0
ocupacionSurtidor3 = 0
ocupacionSurtidor4 = 0
ocupacionSurtidor5 = 0


def histograma(datos, label, titulo, color):
    kwargs = dict(alpha=0.5, bins=200)
    p = plt.hist(datos, **kwargs, color=color, label=label)
    plt.gca().set(title=titulo)
    plt.legend()
    plt.show()
    plt.close()


def tiempoHHMMSS(tiempo):
    return time.strftime('%H:%M:%S', time.gmtime(tiempo))


def intervaloDeConfianza(media, desvio, total):
    inferior = media - (2.57 * (desvio / np.sqrt(total)))
    superior = media + (2.57 * (desvio / np.sqrt(total)))
    return inferior, superior


def calcularMediaDesvio(datos):
    media = np.mean(datos)
    desvioEstandar = np.std(datos)
    return media, desvioEstandar


def iniciar(env, estaciones, i):
    global tiempo
    global tiempoTotal
    global ocupacionSurtidor1
    global ocupacionSurtidor2
    global ocupacionSurtidor3
    global ocupacionSurtidor4
    global ocupacionSurtidor5
    retardoLlegada = np.random.exponential(15)
    yield env.timeout(retardoLlegada)
    llegada = env.now
    v = yield estaciones.get()
    if (v.id == 1 or v.id == 4 or v.id == 5):
        media = v.media
        desvio = v.desvio
        retardo = np.random.normal(media, desvio)
        if (v.id == 1):
            ocupacionSurtidor1 += retardo
        elif (v.id == 4):
            ocupacionSurtidor4 += retardo
        else:
            ocupacionSurtidor5 += retardo
    elif (v.id == 2 or v.id == 3):
        promedio = v.promedio
        retardo = np.random.exponential(promedio)
        if (v.id == 2):
            ocupacionSurtidor2 += retardo
        else:
            ocupacionSurtidor3 += retardo

    atencion = env.now
    yield env.timeout(retardo)
    tiempoEspera = atencion - llegada
    tiempoTotal.append(tiempoEspera)
    tiempo.append(tiempoEspera)
    yield estaciones.put(v)


datosCorridas = []
tiempo = []
tiempoTotal = []
np.random.seed(46)
datos = []
tiempoSimulacion = 0
promedioExperimentos = []
empleadoNormal = namedtuple('empleadoNormal', 'id media desvio')
empleadoExponencial = namedtuple('empledoExponencial', 'id promedio')
empleado1 = empleadoNormal(id=1, media=18, desvio=4)
empleado2 = empleadoExponencial(id=2, promedio=15)
empleado3 = empleadoExponencial(id=3, promedio=16)
empleado4 = empleadoNormal(id=4, media=14, desvio=3)
empleado5 = empleadoNormal(id=5, media=19, desvio=5)
env = simpy.Environment()
estacion = simpy.FilterStore(env, 5)
estacion.items = [empleado1, empleado2, empleado3, empleado4, empleado5]
mediaExperimentos = []
for j in range(60):
    mediaE = 0.0
    tiempo = []
    for i in range(100):
        env.process(iniciar(env, estacion, i))
    env.run()
    tiempoSimulacion += env.now
    mediaE = np.mean(tiempo)
    mediaExperimentos.append(mediaE)
media, desvioE = calcularMediaDesvio(tiempoTotal)
inferior, superior = intervaloDeConfianza(media, desvioE, 1.96)
histograma(mediaExperimentos, "Promedio de cada corrida", "Histograma", "blue")
print("El tiempo total de ejecucion es de : " + tiempoHHMMSS(tiempoSimulacion))
print("El tiempo promedio de espera de los camiones es: " + tiempoHHMMSS(media))
print("El intervalo de confianza es: Inferior " + str(inferior) + " " + "Superior " + str(superior))
porcentaje1 = (tiempoSimulacion / ocupacionSurtidor1) * 100
porcentaje2 = (tiempoSimulacion / ocupacionSurtidor2) * 100
porcentaje3 = (tiempoSimulacion / ocupacionSurtidor3) * 100
porcentaje4 = (tiempoSimulacion / ocupacionSurtidor4) * 100
porcentaje5 = (tiempoSimulacion / ocupacionSurtidor5) * 100
print("El Porcentaje de ocupacion del surtidor 1 es de: " + tiempoHHMMSS(porcentaje1))
print("El Porcentaje de ocupacion del surtidor 2 es de: " + tiempoHHMMSS(porcentaje2))
print("El Porcentaje de ocupacion del surtidor 3 es de: " + tiempoHHMMSS(porcentaje3))
print("El Porcentaje de ocupacion del surtidor 4 es de: " + tiempoHHMMSS(porcentaje4))
print("El Porcentaje de ocupacion del surtidor 5 es de: " + tiempoHHMMSS(porcentaje5))

