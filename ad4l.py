#!/usr/bin/python3
# import subprocess
# import json

# def top():
#     procesos = {}
#     cabeceras = ["pid", "user", "pr", "ni", "virt", "res", "shr", "s" "cpu", "mem", "time"]
#     top = subprocess.run(['top', '-n 1', '-b'], stdout=subprocess.PIPE)
#     lineas = top.stdout.split(b"\n")
#     for linea in lineas[7:]:
#         campos = linea.split()
#         if len(campos) == 12:
#             campos = list(map(lambda x: x.decode('ascii'), campos))
#             valor = [[c] for c in campos[0:10]]
#             dicValor = dict(zip(cabeceras, valor))
#             if campos[11] not in procesos:
#                 procesos[campos[11]] = dicValor
#             else:
#                 for c in cabeceras:
#                     procesos[campos[11]][c] = procesos[campos[11]][c] + dicValor[c]
#             # print(procesos)
#             # exit()
#     return procesos

# procesos_actuales = top()
# print(json.dumps(procesos_actuales, sort_keys=True, indent=4))

import psutil, statistics, time
procesos = {}

#inicializar
for proc in psutil.process_iter():
    procesos[proc.pid] = {
    "name": proc.name(),
    "cpu": [proc.cpu_percent()],
    "mem": [proc.memory_full_info().vms], 
    "ior": [proc.io_counters().read_bytes], 
    "iow": [proc.io_counters().write_bytes]
    }

# for _ in range(2):
#     time.sleep(5)

#funcion
for proc in psutil.process_iter():
    procesos[proc.pid]["cpu"] += [proc.cpu_percent()]
    procesos[proc.pid]["mem"] += [proc.memory_full_info().vms]
    procesos[proc.pid]["ior"] += [proc.io_counters().read_bytes]
    procesos[proc.pid]["iow"] += [proc.io_counters().write_bytes]
    procesos[proc.pid]["cpu"] = procesos[proc.pid]["cpu"][-5:]
    procesos[proc.pid]["mem"] = procesos[proc.pid]["mem"][-5:]
    procesos[proc.pid]["ior"] = procesos[proc.pid]["ior"][-5:]
    procesos[proc.pid]["iow"] = procesos[proc.pid]["iow"][-5:]

for key in procesos:
    print(statistics.variance(procesos[key]["cpu"]))
    print(statistics.variance(procesos[key]["mem"]))
    print(statistics.variance(procesos[key]["ior"]))
    print(statistics.variance(procesos[key]["iow"]))
    # si alguno de esos prints es > que 40, alert  key es el pid y el nombre es procesos[key]["name"]


# p.cpu_percent()
# p.memory_full_info()
# p.io_counters()
# psutil.net_io_counters()


# import subprocess
# df = subprocess.check_output("lsusb")
# df
# split por \n

#dict de procesos 
# historico cpu, mem, io

# historico de net

# alerta cuando algo cambia drásticamente sin sentido notify-send "hola cara bola"