import sys
import PySimpleGUI as sg
import numpy as np
import serial.tools.list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure
from Lidar import Lidar

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
                sg.Spin(values=[_+1 for _ in range(10000)], initial_value=1000, size=(60, 1), key="nbr")
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


            if baud != None and port != None and dossier != "" and nbr != None:
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

    

    layoutScan = [
            [sg.Canvas(size=(640, 480), key='canvas')],
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
        event, values = windowScan.read(timeout=1)
        if event == 'Annuler' or event == sg.WIN_CLOSED:
            lidar.join()
            sys.exit()
        ax.cla()
        ax.set_rlim(0,8)

        ax.plot(data[0],data[1],'o',markersize=1)
        fig_agg.draw()

