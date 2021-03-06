#!/usr/bin/python3
import statistics
import subprocess
import threading
import psutil
import json
import time
import os

############################# IDEAS ###################################################
# dict de procesos 
# historico cpu, mem, io
# historico de net
# alerta cuando algo cambia drásticamente sin sentido notify-send "hola cara bola"
#######################################################################################

### Historial de dispositivos conectados
# 1. Si se quiere inicializar con lista vacía para detectar nuevos en la primera iteración
# dispositivos_conectados = []

# 2. Si se quiere inicializar con el estado actual de dispositivos
df = subprocess.run(['lsusb'], stdout=subprocess.PIPE)
dispositivos_conectados = df.stdout.split(b"\n")

### Historial de procesos
procesos = {}
for proc in psutil.process_iter():
    procesos[proc.pid] = {
        "name": proc.name(),
        "cpu": [proc.cpu_percent()],
        "mem": [proc.memory_full_info().vms], 
        "ior": [proc.io_counters().read_bytes], 
        "iow": [proc.io_counters().write_bytes]
    }

### Historial de red
red = {}
red["bytes_sent"] = [psutil.net_io_counters().bytes_sent]
red["bytes_recv"] = [psutil.net_io_counters().bytes_recv]

#######################################################################################

# Función utilizada por el resto de funciones para enviar notificaciones al usuario del sistema
def notificar(title, message):
    userID = subprocess.run(['id', '-u', os.environ['SUDO_USER']],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True).stdout.decode("utf-8").replace('\n', '')

    subprocess.run(['sudo', '-u', os.environ['SUDO_USER'], 'DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{}/bus'.format(userID), 
        'notify-send', '-i', 'important', title, message],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True)

#######################################################################################

# Función encargada de detectar los recursos utilizados por cada proceso (memoria, CPU, etc.)
def listarProcesos():
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

# Función encargada de detectar anomalías en el uso de un recurso por parte de un proceso
def detectarAnomalias():
    global procesos
    for proc in psutil.process_iter():
        if proc.pid in procesos:
            procesos[proc.pid]["cpu"] += [proc.cpu_percent()]
            procesos[proc.pid]["mem"] += [proc.memory_full_info().vms]
            procesos[proc.pid]["ior"] += [proc.io_counters().read_bytes]
            procesos[proc.pid]["iow"] += [proc.io_counters().write_bytes]
            procesos[proc.pid]["cpu"] = procesos[proc.pid]["cpu"][-5:]
            procesos[proc.pid]["mem"] = procesos[proc.pid]["mem"][-5:]
            procesos[proc.pid]["ior"] = procesos[proc.pid]["ior"][-5:]
            procesos[proc.pid]["iow"] = procesos[proc.pid]["iow"][-5:]
        else:
            procesos[proc.pid] = {
                "name": proc.name(),
                "cpu": [proc.cpu_percent()],
                "mem": [proc.memory_full_info().vms], 
                "ior": [proc.io_counters().read_bytes], 
                "iow": [proc.io_counters().write_bytes]
            }

    tituloMensaje = "¡Anomalía detectada!"
    for key in procesos:
        if len(procesos[key]["cpu"]) == 5 and statistics.variance(procesos[key]["cpu"]) > 50:
            notificar(tituloMensaje, "El proceso " + procesos[key]["name"] + " es anómalo en CPU.")
        if len(procesos[key]["mem"]) == 5 and statistics.variance(procesos[key]["mem"]) > 500*1024*1024:
            notificar(tituloMensaje, "El proceso " + procesos[key]["name"] + " es anómalo en memoria.")
        if len(procesos[key]["ior"]) == 5 and statistics.variance(procesos[key]["ior"]) > 500*1024*1024:
            notificar(tituloMensaje, "El proceso " + procesos[key]["name"] + " es anómalo en lectura de disco.")
        if len(procesos[key]["iow"]) == 5 and statistics.variance(procesos[key]["iow"]) > 200*1024*1024:
            notificar(tituloMensaje, "El proceso " + procesos[key]["name"] + " es anómalo en escritura de disco.")

#######################################################################################

# Función encargada de detectar anomalías en el uso de la red
def detectarRed():
    global red
    red["bytes_sent"] += [psutil.net_io_counters().bytes_sent]
    red["bytes_recv"] += [psutil.net_io_counters().bytes_recv]
    red["bytes_sent"] = red["bytes_sent"][-5:]
    red["bytes_recv"] = red["bytes_recv"][-5:]
    
    tituloMensaje = "¡Anomalía en la red!"
    valorMax = 50*1024*1024
    if len(red["bytes_sent"]) == 5 and statistics.variance(red["bytes_sent"]) > valorMax:
        notificar(tituloMensaje, "Se han enviado muchos datos a través de la red")
    if len(red["bytes_recv"]) == 5 and statistics.variance(red["bytes_recv"]) > valorMax:
        notificar(tituloMensaje, "Se han recibido muchos datos a través de la red")

#######################################################################################

# Función encargada de detectar cuándo se ha conectado un nuevo dispositivo USB
def listarDispositivos():
    df = subprocess.run(['lsusb'], stdout=subprocess.PIPE)
    dispositivos_actuales = df.stdout.split(b"\n")
    
    global dispositivos_conectados
    tituloMensaje = "¡Alerta de conexión de dispositivos!"
    if(dispositivos_actuales > dispositivos_conectados):
        print(" - ¡Un nuevo dispositivo ha sido conectado al sistema!")
        notificar(tituloMensaje, "¡Un nuevo dispositivo ha sido conectado al sistema!")
    elif(dispositivos_actuales < dispositivos_conectados):
        print(" - ¡Un dispositivo ha sido desconectado del sistema!")
        notificar(tituloMensaje, "¡Un dispositivo ha sido desconectado del sistema!")

    dispositivos_conectados = dispositivos_actuales

########################################################################################

# Función encargada de comprobar si existe algún usuario sin contraseña
def comprobarUsuariosSinPassword():
    df = subprocess.run(['sudo awk -F: \'($2 == "") {print}\' /etc/shadow'], stdout=subprocess.PIPE)
    if(len(df.stdout) > 0):
        print(" - ¡Se ha encontrado un usuario sin contraseña registrado en el sistema!")
        notificar("¡Problema de seguridad!", "¡Encontrado un usuario sin contraseña en el sistema!")

########################################################################################

# Función encargada de comprobar si el usuario root acepta login vía SSH
def comprobarPasswordRootSsh():
    subprocess.run(['grep "PermitRootLogin " /etc/ssh/sshd_config 2>/dev/null | grep -v "#" | awk \'{print  $2}\''],
        stdout=subprocess.PIPE)
    if(len(df.stdout) > 0):
        print(" - ¡El usuario root está aceptando conexiones a través de SSH!")
        notificar("¡Problema de seguridad!", "¡El usuario root acepta conexiones entrantes por SSH!")

########################################################################################

# Ejecución de grupo de funciones de detección: cada 5 segundos
def fanomalia(f_stop):
    detectarAnomalias()
    detectarRed()
    listarDispositivos()
    if not f_stop.is_set():
        threading.Timer(10, fanomalia, [f_stop]).start()

########################################################################################

# Ejecución de grupo de funciones de comprobación de contraseñas: cada 20 segundos
def fusuario(f_stop_usuario):
    comprobarPasswordRootSsh()
    comprobarUsuariosSinPassword()
    if not f_stop_usuario.is_set():
        threading.Timer(20, fusuario, [f_stop_usuario]).start()

########################################################################################

### Cuerpo del main

# Detección de red y dispositivos
f_stop = threading.Event()
fanomalia(f_stop)

# Comprobación de contraseñas vacías
f_stop_usuario = threading.Event()
fusuario(f_stop_usuario)
