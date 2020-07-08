import numpy as np
import simpy
import matplotlib.pyplot as plt
from random import *

costoOrden=3800
costoTotalAnual=0
costoXFaltante=625
costoXMantenimiento=450
costoXUnidad=950
colaEventos=[]
def demandaDiaria(env,j):
    global demanda
    probabilidad = 0
    yield env.timeout(0)
    demandaD = np.random.uniform()
    if (demandaD>=0.0 and demandaD <= 0.2):
        probabilidad = 25
    elif (demandaD >0.2 and demandaD <= 0.24):
        probabilidad = 30
    elif (demandaD > 0.24 and demandaD <= 0.3):
        probabilidad = 40
    elif (demandaD > 0.3 and demandaD <= 0.42):
        probabilidad =50
    elif (demandaD > 0.42 and demandaD <= 0.62):
        probabilidad = 100
    elif (demandaD > 0.62 and demandaD <= 0.65):
        probabilidad = 150
    elif (demandaD > 0.65 and demandaD <= 0.8):
        probabilidad = 200
    elif (demandaD > 0.8 and demandaD <= 0.9):
        probabilidad = 250
    else:
        probabilidad = 300
    demanda=probabilidad

def entregaProducto(env,j):
    yield env.timeout(0)
    tiempoEntrega = 0
    probabilidad = np.random.uniform()
    if (probabilidad >=0.0 and probabilidad<=0.2):
        tiempoEntrega = 1
    elif (probabilidad >0.2 and probabilidad<=0.25):
        tiempoEntrega=randint(3,4)
    else:
        tiempoEntrega = 2
    return tiempoEntrega


def calcularUnidadesEnInventario(env,j):
    global demanda
    global unidadesEnInventario
    yield env.timeout(0)
    unidadesEnInventario -= demanda

def esperarLote(env,j):
    probabilidad = 0
    yield env.timeout(0)
    probabilidad = np.random.uniform()
    if (probabilidad >=0.0 and probabilidad<=0.1):
        tiempoEspera= 5
    elif (probabilidad >0.1 and probabilidad<=0.15):
        tiempoEspera = randint(3,4)
    elif (probabilidad >0.15 or probabilidad <=0.2):
        tiempoEspera = 2
    else:
        tiempoEspera = 1
    yield env.timeout(tiempoEspera)

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

def reponerInventario(env,j):
    yield env.timeout(0)
    global unidadesEnInventario
    global costoTotal
    global costoxOrdenar
    unidadesEnInventario=+100

def calcularCostoXOrdenar():
    return costoXUnidad*100*costoOrden

def iniciarSimulacion(env, r, j):
    global costoOrden
    global costoTotalAnual
    global costoXFaltante
    global costoMes
    global ganancia
    global unidadesEnInventario
    yield env.timeout(0)
    costo=0
    with r.request() as request:
        yield request
        yield env.timeout(2)
        yield env.process(demandaDiaria(env,j))
        yield env.process(calcularUnidadesEnInventario(env,j))

        if (unidadesEnInventario < 0):
              costo += calcularCostoXOrdenar()
              costo += (abs(unidadesEnInventario) * costoXFaltante)
              yield env.process(reponerInventario(env, j))
              yield env.process(esperarLote(env,j))
        else:
            if (unidadesEnInventario <= 15 and unidadesEnInventario > 0):  # punto de reorden
                costo += calcularCostoXOrdenar()
                yield env.process(reponerInventario(env, j))
                yield env.process(esperarLote(env,j))
        yield env.process(entregaProducto(env,j))
        costoMes+=costo
        costoTotalAnual+=costo

env = simpy.Environment()
r = simpy.Resource(env, 1)
np.random.seed(76)
unidadesEnInventario = 1500
cantidadAOrdenar = 100
puntoReorden = 15
costoxOrdenar=0
costoTotalMensual=[]
ganancia=0
for i in range(12):
    costoMes=0
    for j in range(30):
        env.process(iniciarSimulacion(env, r, j))
    env.run()
    costoTotalMensual.append(costoMes)
mediaT = np.mean(costoTotalMensual)
mediaCM,desvio = calcularMediaDesvio(costoTotalMensual)
print("El promedio de costo mensual es: "+ str(mediaT))
i,s=intervaloDeConfianza(mediaCM,desvio, costoTotalAnual,1.96)
print("El intervalo de confianza es : limite inferior = "+ str(i)+"  limite superior = "+ str(s))
histograma(costoTotalMensual,"Promedio de costos mensuales", "Histograma", "cyan")
print("----------------------------------------------------------------")
