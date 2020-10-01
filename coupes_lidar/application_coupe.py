import sys
from os import path,access,W_OK
import PySimpleGUI as sg
import numpy as np
import serial.tools.list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure
from Lidar import Lidar
import time
import csv

listeSerie = lambda: serial.tools.list_ports.comports()

listePorts = listeSerie()


def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


if __name__ == "__main__":
    sg.theme('LightGrey1')
    while True: #Choix des paramètres du Lidar

        layoutParam = [
            [
                sg.Text('Port :', size=(16, 1)),
                sg.Combo(values=listePorts, size=(60, 1), key="com")
            ],
            [
                sg.Text('Baud :', size=(16, 1)),
                sg.Combo(values=[115200, 256000], default_value=115200, size=(60, 1), key="baud")
            ],
             [
                sg.Text('Nombre de points :', size=(16, 1)),
                sg.Spin(values=[_+1 for _ in range(10000)], initial_value=500, size=(60, 1), key="nbr")
            ],
            [
                sg.Text('Dossier cible :', size=(16, 1)),
                sg.Input(size=(52, 1),key="dossier"),
                sg.FolderBrowse(size=(6,1),target="dossier")
            ],
            [
                sg.Button('Ok',size=(10, 1)),sg.Button('Annuler',size=(10, 1))
            ]
                ]

        windowParam = sg.Window('Connexion Lidar', layoutParam)
        baud,port,dossier = None,None,""
        while True:
            event, values = windowParam.Read()
            if event == sg.WIN_CLOSED or event == "Annuler":
                sys.exit()
            try:
                baud = values['baud']
                port = values['com'].device
                dossier = values['dossier']
                nbr = values['nbr']
            except:
                pass


            if port == None:
                sg.Popup("Choisir un port")
            elif baud not in [115200, 256000]:
                sg.Popup("Mauvaise valeur de baud")
            elif not path.isdir(dossier):
                sg.Popup("Choisir un dossier valide")
            elif type(nbr) != int or nbr not in range(1,10000):
                sg.Popup("Choisir un nombre de points valide")
            else: 
                break
                
            
        windowParam.close()

        angle = []
        dist = []
        data = (angle,dist)

        try:
            lidar = Lidar(port,baud,data,limit=nbr)
            break
        except Exception as error:
            print(error)

    
    while True:
        layoutScan = [
                [sg.Canvas(size=(640, 480), key='canvas')],
                [sg.Text('Nom du fichier :', size=(16, 1)),sg.Input(size=(30, 1),key="nomFichier")],
                [sg.Button('Enregistrer', size=(10, 1)),sg.Button('Annuler', size=(10, 1))]
                    ]
        

        windowScan = sg.Window('Scan Lidar', layoutScan)
        windowScan.Finalize()
        
        canvas_elem = windowScan['canvas']
        canvas = canvas_elem.TKCanvas

        fig = Figure()
        ax = fig.add_subplot(111, projection='polar')
        ax.set_rlim(0,8)
        fig_agg = draw_figure(canvas, fig)
        
        lidar.start()

        while True:
            event, values = windowScan.read(timeout=5)
            if event == 'Annuler' or event == sg.WIN_CLOSED:
                lidar.join()
                sys.exit()
            elif event == "Enregistrer":
                nomFichier = values['nomFichier']

                if nomFichier == "" or nomFichier == None:
                    sg.Popup("Entrer un nom de ficher")
                else:
                    nomComplet = path.join(dossier,nomFichier+'.csv').replace('/','\\')
                    if path.exists(nomComplet):
                        sg.Popup("Le fichier existe déjà")
                    else:
                        try:
                            with open(nomComplet, 'x') as tempfile:
                                pass
                            break
                        except OSError:
                                sg.Popup("Le fichier ne peut pas être créé à cet emplacement.\nPermissions non accordées ou nom non valide")
                    

            ax.cla()
            ax.set_rlim(0,8)

            ax.plot(data[0],data[1],'o',markersize=1)
            fig_agg.draw()

        try:
            lidar.join()
        except Exception as e:
            print(e)

        windowScan.close()


        time.sleep(5)

        with open(nomComplet, 'w',newline='') as fichierData:
            spamwriter = csv.writer(fichierData, delimiter=',',dialect='excel')
            spamwriter.writerow(['Angle']+ ['Distance'])
            for j in range(len(data[0])):
                spamwriter.writerow([data[0][j],data[1][j]])

        if sg.PopupOKCancel("Nouvelle mesure ?") != "OK":
            sys.exit()

        try:
            lidar = Lidar(port,baud,data,limit=nbr)
        except Exception as error:
            print(error)
            sys.exit()
    