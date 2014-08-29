import random
import simpy

#AREA DE DATOS
#-----------------------------------------------------------------------
cant_proc = 200          #cantidad de procesos a realizar
intervalo = 10.0        #intervalo de tiempo de llegada de los procesos

#-----------------------------------------------------------------------
#-------------------------------PROGRAMA--------------------------------
#-----------------------------------------------------------------------


#-----------------------------------------------------------------------
#se crean los procesos con el tiempo de espera entre cada uno

def source (env, cant_proc, intervalo, CPU, RAM, espera):
    for i in range (cant_proc):
        cant_inst = random.randint(1,10)                    #cantidad de instrucciones
        cant_RAM = random.randint(1,10)                     #cantidad de memoria 
        tiem_proceso = random.expovariate(1.0/intervalo)    #tiempo de creacion de cada proceso
        env.process(proceso(env, 'Proceso%02d' % i,cant_RAM, CPU, RAM, espera, cant_inst))
        yield env.timeout(tiem_proceso)                     #tiempo de espera para solicitar memoria

#-----------------------------------------------------------------------
#Se evalua el proceso en cada una de las etapas

def proceso (env, proceso, cant_RAM, CPU, RAM, espera, cant_inst):
    global tiempo                           #se hace global, para usarla fuera de proceso
    arrive = env.now                        #tiempo en el que llega el proceso a solicitar RAM
    cant_RAM = random.randint(1,10)         #cantidad de RAM que solicita el proceso

    print ('Tiempo: %d NEW: El %s esperando RAM' % (env.now,proceso))

    with RAM.get(cant_RAM) as req:
        yield req                           #esperar por la memoria RAM
        wait = env.now - arrive             #tiempo de espara para la RAM
        print ('Tiempo: %d El %s llego a READY, espero RAM por %d' % (env.now,proceso,wait))

    #---------------------------------------------------------------
    #tiempo de proceso del CPU
    while cant_inst > 0:
        with CPU.request() as reqCPU:
            yield reqCPU                #esperar para ser atendidos por el CPU
            print ('Tiempo: %d El %s RUNNING: %d instrucciones' %(env.now, proceso, wait))
            yield env.timeout(1)        #tiempo del CPU

    #---------------------------------------------------------------
    #comparacion para saber el numero de instrucciones
            if cant_inst > 3:
                cant_inst = cant_inst - 3
            else:
                cant_inst = 0
    #---------------------------------------------------------------
    #si aun hay instrucciones, se envian a ready o waiting
        if cant_inst > 0:
            decision = random.choice(["ready","waiting"])
            if decision == "waiting":
                with espera.request() as reqespera:
                    yield reqespera
                    print('Tiempo: %d El %s paso a Waiting' %(env.now, proceso))
                    yield env.timeout(1)    #tiempo para I/O

            print('Tiempo: %d El %s paso a Ready' %(env.now, proceso))

    #fin del proceso
    #---------------------------------------------------------------
        tiempo_proceso = env.now - arrive
        print('Tiempo: %d El %s ha Terminado, se tardo %d' %(env.now, proceso, tiempo_proceso))
        tiempo = tiempo + tiempo_proceso    #tiempo total de ejecucion de todos los procesos
    #Se deja de utilizar RAM
    #---------------------------------------------------------------
        with RAM.put(cant_RAM) as reqDevolverRAM:
            yield reqDevolverRAM            #regreso de la RAM
            print('Tiempo: %d El %s, regreso %d de RAM' %(env.now, proceso, cant_RAM))
            
#Inicio de la simulacion
#-----------------------------------------------------------------------
env = simpy.Environment()
random.seed(10)

#Inicio de los procesos
#-----------------------------------------------------------------------
CPU = simpy.Resource(env, capacity=1)                   #CPU, cantidad de procesos
RAM = simpy.Container(env, init=100, capacity=100)      #cantidad de RAM
espera = simpy.Resource(env, capacity=1)                #control de I/O
env.process(source(env, cant_proc, intervalo, CPU, RAM, espera))
tiempo = 0                                              #tiempo total de la ejecucion

#correr la simulacion
#-----------------------------------------------------------------------
env.run()

#-----------------------------------------------------------------------
#se imprime el tiempo promedio de la ejecucion
print('Tiempo promedio: %f' %(tiempo/cant_proc))
