import numpy as np
import simpy
import matplotlib.pyplot as plt
from random import *

tope = 100
global tiempoTotal
global tiempoAS
global tiempoAI
global tiempoAM
global cantAccesoS
global cantAccesoM
global cantAccesoI
cantAccesoS = 0
cantAccesoM = 0
cantAccesoI = 0
tiempoTotal = 0
tiempoAS = 0
tiempoAI = 0
tiempoAM = 0
tiempoExperimentoPromedio = []


def histograma(datos, label, titulo, color):
    kwargs = dict(alpha=0.5, bins=200)
    p = plt.hist(datos, **kwargs, color=color, label=label)
    plt.gca().set(title=titulo)
    plt.legend()
    plt.show()
    plt.close()


def intervaloDeConfianza(media, desvio, total):
    inferior = media - (2.57 * (desvio / np.sqrt(total)))
    superior = media + (2.57 * (desvio / np.sqrt(total)))
    return inferior, superior


def calcularMediaVarianza(datos):
    media = np.mean(datos)
    varianza = np.var(datos)
    desvioEstandar = np.std(datos)
    return media, varianza, desvioEstandar


def retirarAlfombras(env, i, superior):
    global tiempoAS
    global tiempoAM
    global datosCorridas
    global tiempoTotal
    retardo = np.random.uniform(1, 5)
    yield env.timeout(retardo)
    tiempoTotal += retardo
    if superior == 1:
        tiempoAS += retardo
    else:
        tiempoAM += retardo
    datosCorridas.append(retardo)


def aplicarDetergente(env, i, tope1, tope2):
    global tiempoAS
    global tiempoAM
    global datosCorridas
    global tiempoTotal
    retardo = np.random.uniform(tope1, tope2)
    yield env.timeout(retardo)
    tiempoTotal += retardo
    if tope1 == 1:
        tiempoAS += retardo
    else:
        tiempoAM += retardo
    datosCorridas.append(retardo)


def enjuagarAlfombras(env, i):
    global tiempoAS
    global datosCorridas
    global tiempoTotal
    retardo = np.random.uniform(1, 3)
    yield env.timeout(retardo)
    tiempoTotal += retardo
    tiempoAS += retardo
    datosCorridas.append(retardo)


def mojarVehiculo(env, i):
    global tiempoAM
    global datosCorridas
    global tiempoTotal
    retardo = np.random.uniform(1, 6)
    yield env.timeout(retardo)
    tiempoTotal += retardo
    tiempoAM += retardo
    datosCorridas.append(retardo)


def enjuagarVehiculo(env, i, medio):
    global tiempoAM
    global tiempoAI
    global datosCorridas
    global tiempoTotal
    retardo = np.random.uniform(5, 10)
    yield env.timeout(retardo)
    tiempoTotal += retardo
    if medio == 1:
        tiempoAM += retardo
    else:
        tiempoAI += retardo
    datosCorridas.append(retardo)


def aspirarInteriores(env, i):
    global tiempoAI
    global datosCorridas
    global tiempoTotal
    retardo = np.random.uniform(10, 15)
    yield env.timeout(retardo)
    tiempoTotal += retardo
    tiempoAI += retardo
    datosCorridas.append(retardo)


def accesoSuperior(env, empleados, i):
    global cantAccesoS
    yield env.process(retirarAlfombras(env, i, 1))
    yield env.process(aplicarDetergente(env, i, 1, 3))
    yield env.process(enjuagarAlfombras(env, i))
    cantAccesoS += 1


def accesoMedio(env, empledos, i):
    global cantAccesoM
    yield env.process(retirarAlfombras(env, i, 0))
    yield env.process(mojarVehiculo(env, i))
    yield env.process(aplicarDetergente(env, i, 6, 12))
    yield env.process(enjuagarVehiculo(env, i, 1))
    cantAccesoM += 1


def accesoInferior(env, empleados, i):
    yield env.process(enjuagarVehiculo(env, i, 0))
    yield env.process(aspirarInteriores(env, i))


def actividad(env, empleados, i):
    global tiempoTotal
    yield env.timeout(0)

    with empleados.request() as request:
        yield request
        numero = randint(0, 1)
        if numero == 0:
            yield env.process(accesoSuperior(env, empleados, i))
        else:
            yield env.process(accesoMedio(env, empleados, i))
        yield env.process(accesoInferior(env, empleados, i))


datosCorridas = []
env = simpy.Environment()
empleados = simpy.Resource(env, 2)
np.random.seed(12345)
for j in range(30):
    tiempoTotal = 0
    for i in range(100):
        env.process(actividad(env, empleados, i))
    env.run()
    tiempoExperimentoPromedio.append(tiempoTotal / 100)
media, varianza, desvioEstandar = calcularMediaVarianza(tiempoExperimentoPromedio)
inferior, superior = intervaloDeConfianza(media, varianza, desvioEstandar)
criticidadS = (3 / 9) * 100
criticidadM = (4 / 9) * 100
criticidadI = (2 / 9) * 100
cantAccesoI = 3000
print("El promedio de tiempo del acceso superior es ", tiempoAS / cantAccesoS)
print("El promedio de tiempo del acceso medio es ", tiempoAM / cantAccesoM)
print("El promedio de tiempo del acceso inferior es ", tiempoAI / cantAccesoI)
print("El promedio de duracion del proyecto es: " + str(media))
print("El intervalo de confianza es: Inferior " + str(inferior) + " " + "Superior " + str(superior))
histograma(datosCorridas, "Datos de 3000 corridas", "Histograma", "cyan")
histograma(tiempoExperimentoPromedio, "Promedios de 30 corridas", "Histograma", "red")
print("El porcentaje de criticidad del acceso superior es " + str(criticidadS) + " %")
print("El porcentaje de criticidad del acceso medio es " + str(criticidadM) + " %")
print("El porcentaje de criticidad del acceso inferior es " + str(criticidadI) + " %")

