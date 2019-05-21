#!/usr/bin/python3
import subprocess
import threading
import psutil
import json
import time

############################# IDEAS ###################################################
#dict de procesos 
# historico cpu, mem, io
# historico de net
# alerta cuando algo cambia drásticamente sin sentido notify-send "hola cara bola"
#######################################################################################

# Historial de dispositivos conectados

# 1. Si se quiere inicializar con lista vacía para detectar nuevos en la primera iteración
# dispositivos_conectados = []

# 2. Si se quiere inicializar con el estado actual de dispositivos
df = subprocess.run(['lsusb'], stdout=subprocess.PIPE)
dispositivos_conectados = df.stdout.split(b"\n")

#######################################################################################

# Función encargada de detectar los recursos utilizados por cada proceso (memoria, CPU, etc.)
def top():
    procesos = {}
    cabeceras = ["pid", "user", "pr", "ni", "virt", "res", "shr", "s" "cpu", "mem", "time"]
    top = subprocess.run(['top', '-n 1', '-b'], stdout=subprocess.PIPE)
    lineas = top.stdout.split(b"\n")
    for linea in lineas[7:]:
        campos = linea.split()
        if len(campos) == 12:
            campos = list(map(lambda x: x.decode('ascii'), campos))
            valor = [[c] for c in campos[0:10]]
            dicValor = dict(zip(cabeceras, valor))
            if campos[11] not in procesos:
                procesos[campos[11]] = dicValor
            else:
                for c in cabeceras:
                    procesos[campos[11]][c] = procesos[campos[11]][c] + dicValor[c]
            # print(procesos)
            # exit()
    return procesos

#######################################################################################

# procesos_actuales = top()
# print(json.dumps(procesos_actuales, sort_keys=True, indent=4))

# PROCNAME = "firefox"
# p = None
# for proc in psutil.process_iter():
#     if proc.name() == PROCNAME:
#         print(proc)
#         p = proc

# p.cpu_percent()
# p.memory_full_info()
# p.io_counters()
# psutil.net_io_counters()

#######################################################################################

# Función encargada de detectar cuándo se ha conectado un nuevo dispositivo USB
def lsusb():
    df = subprocess.run(['lsusb'], stdout=subprocess.PIPE)
    dispositivos_actuales = df.stdout.split(b"\n")
    
    global dispositivos_conectados
    if(dispositivos_actuales > dispositivos_conectados):
        print("¡Un nuevo dispositivo ha sido conectado al sistema!")
    elif(dispositivos_actuales < dispositivos_conectados):
        print("¡Un dispositivo ha sido desconectado del sistema!")

    dispositivos_conectados = dispositivos_actuales

########################################################################################

### Ejecución del script en segundo plano
while(True):
    print("Comprobando lista de dispositivos conectados...")
    lsusb()
    time.sleep(3)
