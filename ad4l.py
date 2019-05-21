#!/usr/bin/python3
import subprocess
import json

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

procesos_actuales = top()
print(json.dumps(procesos_actuales, sort_keys=True, indent=4))

import psutil

PROCNAME = "firefox"
p = None
for proc in psutil.process_iter():
    if proc.name() == PROCNAME:
        print(proc)
        p = proc

p.cpu_percent()
p.memory_full_info()
p.io_counters()
psutil.net_io_counters()


import subprocess
df = subprocess.check_output("lsusb")
df
# split por \n

#dict de procesos 
# historico cpu, mem, io

# historico de net

# alerta cuando algo cambia drásticamente sin sentido notify-send "hola cara bola"