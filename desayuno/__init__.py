import numpy as np
import simpy
import matplotlib.pyplot as plt

tope = 100
global tiempoTotal
global tiempoAS
global tiempoAI
global tiempoAM

tiempoTotal = 0
tiempoAI = 0
tiempoAM = 0
tiempoAS = 0
media = 0
varianza = 0
desvioEstandar = 0


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


def romperHuevos(env, i):
    global tiempoAS
    global datosCorridas
    global tiempoTotal
    retardo = np.random.uniform(2, 4)
    yield env.timeout(retardo)
    tiempoTotal += retardo
    tiempoAS += retardo
    datosCorridas.append(retardo)


def revolverHuevos(env, i):
    global tiempoAS
    global datosCorridas
    global tiempoTotal
    retardo = np.random.uniform(3, 6)
    yield env.timeout(retardo)
    tiempoTotal += retardo
    tiempoAS += retardo
    datosCorridas.append(retardo)


def cocinarHuevos(env, i):
    global tiempoAS
    global tiempoTotal
    global datosCorridas
    retardo = np.random.uniform(2, 5)
    yield env.timeout(retardo)
    tiempoTotal += retardo
    tiempoAS += retardo
    datosCorridas.append(retardo)


def cortarPanes(env, i):
    global tiempoTotal
    global tiempoAM
    global datosCorridas
    retardo = np.random.uniform(3, 6)
    yield env.timeout(retardo)
    tiempoTotal += retardo
    tiempoAM += retardo
    datosCorridas.append(retardo)

    return


def prepararTostadas(env, i):
    global tiempoTotal
    global tiempoAM
    global datosCorridas
    retardo = np.random.uniform(2, 5)
    yield env.timeout(retardo)
    datosCorridas.append(retardo)
    tiempoTotal += retardo
    tiempoAM += retardo


def prepararBebidasCalientes(env):
    global tiempoTotal
    global tiempoAI
    global datosCorridas
    retardo = np.random.uniform(4, 8)
    yield env.timeout(retardo)
    datosCorridas.append(retardo)
    tiempoTotal += retardo
    tiempoAI += retardo


def prepararBebidasFrias(env):
    global tiempoTotal
    global tiempoAI
    global datosCorridas
    retardo = np.random.uniform(3, 7)
    yield env.timeout(retardo)
    datosCorridas.append(retardo)
    tiempoTotal += retardo
    tiempoAI += retardo


def accesoSuperior(env, i, empleados):
    yield env.process(romperHuevos(env, i))
    yield env.process(revolverHuevos(env, i))
    yield env.process(cocinarHuevos(env, i))


def accesoMedio(env, i, empledos):
    yield env.process(cortarPanes(env, i))
    yield env.process(prepararTostadas(env, i))


def accesoInferior(env, i, empleados):
    yield env.process(prepararBebidasCalientes(env))
    yield env.process(prepararBebidasFrias(env))


def actividad(env, empleados, i):
    global tiempoTotal
    yield env.timeout(0)
    with empleados.request() as request:
        yield request
        yield env.process(accesoSuperior(env, i, empleados))
        yield env.process(accesoMedio(env, i, empleados))
        yield env.process(accesoInferior(env, i, empleados))


datosCorridas = []
tiempoExperimentoPromedio = []
env = simpy.Environment()
empleados = simpy.Resource(env, 3)
np.random.seed(8769012)
cantAccesos = 3000
for j in range(30):
    tiempoTotal = 0
    for i in range(100):
        env.process(actividad(env, empleados, i))
    env.run()
    tiempoExperimentoPromedio.append(tiempoTotal / 100)
media, varianza, desvioEstandar = calcularMediaVarianza(tiempoExperimentoPromedio)
inferior, superior = intervaloDeConfianza(media, varianza, desvioEstandar)
criticidadS = (3 / 7) * 100
criticidadM = (2 / 7) * 100
criticidadI = (2 / 7) * 100
print("El promedio de duracion del proyecto es: " + str(media))
print("El intervalo de confianza es: Inferior " + str(inferior) + " " + "Superior " + str(superior))
histograma(datosCorridas, "Datos de 3000 corridas", "Histograma", "blue")
histograma(tiempoExperimentoPromedio, "Promedios de 30 corridas", "Histograma", "purple")
print("El promedio de tiempo del acceso superior es ", tiempoAS / cantAccesos)
print("El promedio de tiempo del acceso medio es ", tiempoAM / cantAccesos)
print("El promedio de tiempo del acceso inferior es ", tiempoAI / cantAccesos)
print("El porcentaje de criticidad del acceso superior es " + str(criticidadS) + " %")
print("El porcentaje de criticidad del acceso medio es " + str(criticidadM) + " %")
print("El porcentaje de criticidad del acceso inferior es " + str(criticidadI) + " %")

