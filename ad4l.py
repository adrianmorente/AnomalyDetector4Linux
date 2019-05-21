#!/usr/bin/python3
import subprocess

procesos = {}

def top():
    cabeceras = ["pid", "user", "pr", "ni", "virt", "res", "shr", "s" "cpu", "mem", "time"]
    top = subprocess.run(['top', '-n 1', '-b'], stdout=subprocess.PIPE)
    lineas = top.stdout.split(b"\n")
    for linea in lineas[7:]:
        campos = linea.split()
        campos = list(map(lambda x: x.decode('ascii'), campos))
        if campos[11] not in procesos:
            procesos[campos[11]] = dict(zip(cabeceras, campos[0:10]))
        print(procesos)
        exit()

top()