import numpy as np
import simpy
import matplotlib.pyplot as plt
from random import *
from collections import namedtuple
import time

ocupacionCajero1 = 0
ocupacionCajero2 = 0
ocupacionCajero3 = 0


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


def iniciar(env, comercio, i):
    global tiempo
    global tiempoTotal
    global ocupacionCajero1
    global ocupacionCajero2
    global ocupacionCajero3
    retardoLlegada = np.random.exponential(10)
    yield env.timeout(retardoLlegada)
    llegada = env.now
    v = yield comercio.get()
    if (v.id == 1 or v.id == 3):
        media = v.media
        desvio = v.desvio
        retardo = np.random.normal(media, desvio)
        if (v.id == 1):
            ocupacionCajero1 += retardo
        else:
            ocupacionCajero3 += retardo
    else:
        promedio = v.promedio
        retardo = np.random.exponential(promedio)
        ocupacionCajero2 += retardo
    atencion = env.now
    if (retardo < 0):
        retardo = 0
    yield env.timeout(retardo)
    tiempoEspera = atencion - llegada
    tiempoTotal.append(tiempoEspera)
    tiempo.append(tiempoEspera)
    yield comercio.put(v)


datosCorridas = []
tiempo = []
tiempoTotal = []
np.random.seed(4243)
datos = []
tiempoSimulacion = 0
promedioExperimentos = []
empleadoNormal = namedtuple('empleadoNormal', 'id media desvio')
empleadoExponencial = namedtuple('empledoExponencial', 'id promedio')
empleado1 = empleadoNormal(id=1, media=15, desvio=3)
empleado2 = empleadoExponencial(id=2, promedio=12)
empleado3 = empleadoNormal(id=3, media=14, desvio=6)
env = simpy.Environment()
comercio = simpy.FilterStore(env, 3)
comercio.items = [empleado1, empleado2, empleado3]
mediaExperimentos = []
for j in range(122):  # 8 horas x 365 dias
    mediaE = 0.0
    tiempo = []
    for i in range(100):
        env.process(iniciar(env, comercio, i))
    env.run()
    tiempoSimulacion += env.now
    mediaE = np.mean(tiempo)
    mediaExperimentos.append(mediaE)
media, desvioE = calcularMediaDesvio(tiempoTotal)
inferior, superior = intervaloDeConfianza(media, desvioE, 1.96)
histograma(mediaExperimentos, "Promedio de cada corrida", "Histograma", "green")
print("El tiempo promedio de espera de los clientes es: " + tiempoHHMMSS(media))
print("El intervalo de confianza es: Inferior " + str(inferior) + " " + "Superior " + str(superior))
porcentaje1 = (tiempoSimulacion / ocupacionCajero1) * 100
porcentaje2 = (tiempoSimulacion / ocupacionCajero2) * 100
porcentaje3 = (tiempoSimulacion / ocupacionCajero3) * 100

print("El Porcentaje de ocupacion del cajero 1 es de: " + tiempoHHMMSS(porcentaje1))
print("El Porcentaje de ocupacion del cajero 2 es de: " + tiempoHHMMSS(porcentaje2))
print("El Porcentaje de ocupacion del cajero 3 es de: " + tiempoHHMMSS(porcentaje3))

