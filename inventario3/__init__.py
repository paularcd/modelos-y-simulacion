import numpy as np
import simpy
import matplotlib.pyplot as plt

costoXOrden=0
costoXOrdenar=93
costoAlmacenamiento=35
costoXFaltante=20
costoXfalta=0
costoXMes=0
costoXAlmacenar=0
dia=0
demanda=0
costoTotal=0
costoMensual=[]
unidadesEnInventario=150

def demandaDiaria(env,j):
    global demanda
    yield env.timeout(0)
    demanda=np.random.poisson(37)


def calcularCostoXOrdenar():
    global unidadesEnInventario
    global costoXOrdenar
    global costoXOrden
    costoXOrden=costoXOrdenar*100

def calcularCostoXAlmacenamiento(env,j):
    global costoXAlmacenar
    yield env.timeout(0)
    if (unidadesEnInventario>0):
        costoXAlmacenar=unidadesEnInventario*costoAlmacenamiento


def reponerInventario(env,j,estrategia):
    global dia
    global unidadesEnInventario
    yield env.timeout(0)
    if (dia==0):
        if(unidadesEnInventario<=estrategia):
            calcularCostoXOrdenar()
    if(dia==3):
        unidadesEnInventario+=100
        dia=0
    calcularCostoXFaltante()
    dia=dia+1

def calcularUnidadesEnInventario(env,j):
    global unidadesEnInventario
    global demanda
    yield env.timeout(0)
    unidadesEnInventario-=demanda

def calcularCostoXFaltante():
    global costoXFaltante
    global costoXFalta
    if (unidadesEnInventario<0):
        costoXFalta=abs(unidadesEnInventario)*costoXFaltante

def calcularMediaDesvio(datos):
    media=np.mean(datos)
    desvioEstandar=np.std(datos)
    return media,desvioEstandar


def intervaloDeConfianza(media, desvio,total,z):
    inferior=media-(z*(desvio/np.sqrt(total)))
    superior=media+(z*(desvio/np.sqrt(total)))
    return inferior, superior

def histograma(datos, label, titulo,color):
    kwargs = dict(alpha=0.5, bins=200)
    p=plt.hist(datos, **kwargs, color=color, label=label)
    plt.gca().set(title=titulo)
    plt.legend()
    plt.show()
    plt.close()

def iniciarSimulacion(env,r,j,estrategia):
    global costoXMes
    global costoXOrden
    global costoXAlmacenar
    global costoXfalta
    costoXfalta=0
    costoXAlmacenar=0
    costoXOrden=0
    with r.request() as request:
        yield request
        yield env.timeout(1)
        yield env.process(demandaDiaria(env,j))
        yield env.process(calcularUnidadesEnInventario(env,j))
        yield env.process(reponerInventario(env,j,estrategia))
        yield env.process(calcularCostoXAlmacenamiento(env,j))
        costoXMes+=costoXOrden+costoXAlmacenar+costoXfalta


env = simpy.Environment()
r = simpy.Resource(env, 1)
np.random.seed(693)

for h in range (3):
    if (h==0):
        estrategia=30
    else:
        if(h==1):
            estrategia=15
        else:
            estrategia=40
    for i in range(12):
        costoXMes=0
        for j in range(30):
            env.process(iniciarSimulacion(env,r,j,h))
        env.run()
        costoTotal+=costoXMes
        costoMensual.append(costoXMes)
    mediaT = np.mean(costoMensual)
    mediaCM,desvio = calcularMediaDesvio(costoMensual)

    i,s=intervaloDeConfianza(mediaCM,desvio, costoTotal,1.96)
    print("El intervalo de confianza es : limite inferior = "+ str(i)+"  limite superior = "+ str(s))
    if h == 0:
        print("Costos con la estrategia punto de reorden 30 o menos unidades ")
        color = "red"

    elif h == 1:
        print("Costos con la estrategia punto de reorden 15 o menos unidades ")
        color = "blue"
    else:
        print("Costos con la estrategia punto de reorden 40 o menos unidades ")
        color = "purple"
    print("El costo total anual es: " + str(costoTotal))
    print("El promedio de costo mensual es: " + str(mediaT))

    print("El intervalo de confianza es : limite inferior = " + str(i) + "  limite superior = " + str(s))
    histograma(costoMensual, "Promedio de costos mensuales", "Histograma", color)
    print("----------------------------------------------------------------")
