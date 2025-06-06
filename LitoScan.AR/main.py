
import sys
import serial
import time
import os
import picamerax as picamera
from fractions import Fraction

##############################################################################
################################ USER INPUTS #################################
##############################################################################

# Parametros obtenidos
x_home = int(sys.argv[1])
y_home = int(sys.argv[2])
num_x = int(sys.argv[3])
num_y = int(sys.argv[4])
x_ini = int(sys.argv[5])
x_max = int(sys.argv[6])
y_ini = int(sys.argv[7])
y_max = int(sys.argv[8])
focus_pos = str(sys.argv[9])

isx = int(sys.argv[10])
res_x = int(sys.argv[11])
res_y = int(sys.argv[12])
carpeta = str(sys.argv[13])

# Image capture resolution
res = (res_x, res_y)

# SE ESTABLECE EL DIRECTORIO DONDE SE GUARDAN LAS CAPTURAS
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
output_dir = os.path.join(desktop_path, carpeta)

if not os.path.exists(output_dir):
    print(f"La carpeta {output_dir} no existe. Por favor, créala antes de continuar.")
    exit()

##############################################################################
############################ END OF USER INPUTS ##############################
##############################################################################

####  Initialize Serial Port and Baude Rate  ####
ser = serial.Serial('/dev/ttyUSB0', 9600)
print('\n\nPuerto serial inicializado: retraso de 5 segundos.\n')
#### Gives the Arduino time to intitialize ####
time.sleep(4)
#### sends the GoCode to attach the Arduino Pins to the Servos ####
go = '55551500'
ser.write(go.encode())
time.sleep(1)

print('Arduino listo para recibir instrucciones.\n')
time.sleep(1)

## NUMBER OF STEPS AND STEP SIZE CALCUALTED ##

gridX = num_x + 1
gridY = num_y + 1

x_step = abs(int((x_max - x_ini) / num_x))
y_step = abs(int((y_max - y_ini) / num_y))

i = 0

print("Número de columnas/X: " + str(num_x+1)+ "\n")
time.sleep(1)
print("Número de filas/Y: " + str(num_y+1)+ "\n")
time.sleep(1)
print("Número total de fotos: " + str((num_x+1)*(num_y+1))+ "\n")
time.sleep(1)

######## FOCUS AND IMAGE PARAMETER SEQUENCE STARTS HERE ########
###### IMAGE CAPTURE PARAMETERS ARE AUTOMATICALLY SET HERE ######

print('Iniciando secuencia de enfoque y parámetros de imagen.. \n')
print('Moviéndose a la posición de enfoque en: ' + focus_pos + "\n")
ser.write(focus_pos.encode())

with picamera.PiCamera() as camera:
            camera.resolution = res
            camera.iso = isx
            camera.start_preview()
            time.sleep(15)
            q1 = camera.exposure_speed
            g1 = camera.awb_gains
            camera.stop_preview()

q = q1
print("Velocidad de exposición: " + str(q1) + "\n")

g = g1
print("Ganancia de balance de blancos (AWB): ")
g_rojo,g_azul = g
print("Ganancia para el canal rojo: " + str(g_rojo))
print("Ganancia para el canal azul: " + str(g_azul) + "\n")

print("Valor de ISO de la cámara configurado: " + str(isx) + "\n")

###### IMAGE CAPTURE SEQUENCE STARTS HERE #####

print('\nInicia la adquisición de fotos \nNúmero de fotos que se están recopilando: '+ str((num_x+1)*(num_y+1)))
x1 = str(x_ini)
x = x_ini
time.sleep(0.5)

while i <= num_x:
    print('\nColumna: ' + str(i+1) + ' de ' + str(num_x+1))
    y = y_max
    j = 0

    if x < 1000:
        x1 = '0' + str(x)
    else:
        x1 = str(x)
    y1 = '1700'
    coord1 = x1 + y1
    ser.write(coord1.encode())
    
    while j <= num_y:
        time.sleep(0.5)
        if x < 1000:
            x1 = '0' + str(x)
        else:
            x1 = str(x)
        if y < 1000:
            y1 = '0' + str(y)
        else:
            y1 = str(y)
        coord1 = x1 + y1
        print(coord1)
        toma = "X" + str(i) + "_" + "Y"+ str(j)
        ser.write(coord1.encode())
        with picamera.PiCamera() as camera:
            camera.iso = isx
            camera.resolution = res
            camera.shutter_speed = q
            camera.exposure_mode = 'off'
            camera.awb_mode = 'off'
            camera.awb_gains = g
            filename = os.path.join(output_dir, f"{toma}.jpg")
            time.sleep(4)
            camera.capture(filename)
        y = y - y_step
        j = j + 1


    time.sleep(1)
    # Devolver el carro suavemente a su posición inicial en Y
    while j > 0:
        time.sleep(0.5)  # Mantener el mismo intervalo de tiempo
        if x < 1000:
            x1 = '0' + str(x)
        else:
            x1 = str(x)
        if y < 1000:
            y1 = '0' + str(y)
        else:
            y1 = str(y)
        coord1 = x1 + y1
        print(coord1)
        ser.write(coord1.encode())  # Enviar la nueva posición
        y = y + y_step  # Mover en la dirección opuesta
        j = j - 1  # Reducir el contador
        time.sleep(1)
    
    x = x + x_step
    i = i + 1

a = x_home
b = y_home

if a < 1000:
    a1 = '0' + str(a)
else:
    a1 = str(a)
if b < 1000:
    b1 = '0' + str(b)
else:
    b1 = str(b)
coord = a1 + b1
print(coord)
ser.write(coord.encode())

ser.close()
