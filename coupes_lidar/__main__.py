import sys
from os import path,access,W_OK
import PySimpleGUI as sg
import serial.tools.list_ports
from coupes_lidar.Lidar import Lidar
from time import sleep
from csv import writer
from math import cos,sin,pi
import win32gui
from PIL import ImageGrab

def create_circle(x, y, r, canvas,**kwargs):
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvas.create_oval(x0, y0, x1, y1,**kwargs)

def convertrCoordonesCanvas(x,y,hauteur=500,largeur=500,rMax=8,marge=20):
    l = largeur/2
    h = hauteur/2
    return (((x/rMax)*l)+l+marge,h-((y/rMax)*h)+marge)

def dessinerEchelle(canvas,grilleAngle=True,grilleDistance=False,sousGrille=False,hauteur=500,largeur=500,rMax=8,marge=20,decalageBas=0,decalageHaut=0,decalageTexte=0.07):
    if grilleAngle:
        #Fond
        X,Y = convertrCoordonesCanvas(0,0,hauteur,largeur,rMax,marge)
        create_circle(X,Y,min(hauteur,largeur)/2,canvas,width=0,fill="#eee")

        #Grille Angulaire
        for a in range(0,360,15):
            a_rad = a*pi/180
            m = rMax*decalageBas
            d = rMax*(1-decalageHaut)
            d2 = rMax*(1+decalageTexte)
            X1,Y1 = convertrCoordonesCanvas(m*cos(a_rad),m*sin(a_rad),hauteur,largeur,rMax,marge)
            X2,Y2 = convertrCoordonesCanvas(d*cos(a_rad),d*sin(a_rad),hauteur,largeur,rMax,marge)
            X3,Y3 = convertrCoordonesCanvas(d2*cos(a_rad),d2*sin(a_rad),hauteur,largeur,rMax,marge)
            canvas.create_line(X1,Y1,X2,Y2,fill='#ccc')
            canvas.create_text(X3,Y3, text=str(a)+"°", fill="#777",font=('Helvetica', '10'))
    
    elif grilleDistance:
        #Fond
        X1,Y1 = convertrCoordonesCanvas(-rMax,-rMax,hauteur,largeur,rMax,marge)
        X2,Y2 = convertrCoordonesCanvas(rMax,rMax,hauteur,largeur,rMax,marge)
        canvas.create_rectangle(X1,Y1,X2,Y2,width=0,fill="#eee")

        if sousGrille:
            for x in [_/sousGrille for _ in range(-rMax*sousGrille,rMax*sousGrille+1)]:
                X1,Y1 = convertrCoordonesCanvas(x,-rMax,hauteur,largeur,rMax,marge)
                X2,Y2 = convertrCoordonesCanvas(x,rMax,hauteur,largeur,rMax,marge)
                canvas.create_line(X1,Y1,X2,Y2,fill='#ccc',dash=(4, 1))
            for y in [_/sousGrille for _ in range(-rMax*sousGrille,rMax*sousGrille+1)]:
                X1,Y1 = convertrCoordonesCanvas(-rMax,y,hauteur,largeur,rMax,marge)
                X2,Y2 = convertrCoordonesCanvas(rMax,y,hauteur,largeur,rMax,marge)
                canvas.create_line(X1,Y1,X2,Y2,fill='#ccc',dash=(4, 1))

        for x in range(-rMax,rMax+1):
            X1,Y1 = convertrCoordonesCanvas(x,-rMax,hauteur,largeur,rMax,marge)
            X2,Y2 = convertrCoordonesCanvas(x,rMax,hauteur,largeur,rMax,marge)
            canvas.create_line(X1,Y1,X2,Y2,fill='#ccc')
        for y in range(-rMax,rMax+1):
            X1,Y1 = convertrCoordonesCanvas(-rMax,y,hauteur,largeur,rMax,marge)
            X2,Y2 = convertrCoordonesCanvas(rMax,y,hauteur,largeur,rMax,marge)
            canvas.create_line(X1,Y1,X2,Y2,fill='#ccc')
        
        
        

    #Axes
    X1,Y1 = convertrCoordonesCanvas(-rMax,0,hauteur,largeur,rMax,marge)
    X2,Y2 = convertrCoordonesCanvas(rMax,0,hauteur,largeur,rMax,marge)
    canvas.create_line(X1,Y1,X2,Y2,fill='#aaa')
    X1,Y1 = convertrCoordonesCanvas(0,-rMax,hauteur,largeur,rMax,marge)
    X2,Y2 = convertrCoordonesCanvas(0,rMax,hauteur,largeur,rMax,marge)
    canvas.create_line(X1,Y1,X2,Y2,fill='#aaa')

    #Graduations
    for x in range(-rMax,rMax+1):
        X1,Y1 = convertrCoordonesCanvas(x,-0.02*rMax,hauteur,largeur,rMax,marge)
        X2,Y2 = convertrCoordonesCanvas(x,0.02*rMax,hauteur,largeur,rMax,marge)
        canvas.create_line(X1,Y1,X2,Y2,fill='#aaa')
    for y in range(-rMax,rMax+1):
        X1,Y1 = convertrCoordonesCanvas(-0.02*rMax,y,hauteur,largeur,rMax,marge)
        X2,Y2 = convertrCoordonesCanvas(0.02*rMax,y,hauteur,largeur,rMax,marge)
        canvas.create_line(X1,Y1,X2,Y2,fill='#aaa')

    #Texte limmite axes
    X,Y = convertrCoordonesCanvas(0,rMax,hauteur,largeur,rMax,marge)
    canvas.create_text(X+12,Y, text=str(rMax)+" m", fill="#555",font=('Helvetica', '11'), anchor = 'w')
    X,Y = convertrCoordonesCanvas(rMax,0,hauteur,largeur,rMax,marge)
    canvas.create_text(X,Y-15, text=str(rMax)+" m", fill="#555",font=('Helvetica', '11'))


def dessinerPoints(canvas,angle,dist,grilleAngle=True,grilleDistance=False,largeur=500,hauteur=500,rMax=8,marge=20): 
    if grilleDistance:
        x = dist*cos(angle)
        y = dist*sin(angle)
        if x < rMax and y < rMax:
            X,Y = convertrCoordonesCanvas(x,y,hauteur,largeur,rMax,marge)
            create_circle(X,Y,1,canvas,width=0,fill="#0074e8")
    elif grilleAngle and dist < rMax:
        x = dist*cos(angle)
        y = dist*sin(angle)
        X,Y = convertrCoordonesCanvas(x,y,hauteur,largeur,rMax,marge)
        create_circle(X,Y,1,canvas,width=0,fill="#0074e8")



def main():
    sg.theme('LightGrey1')
    LARGEUR = 500
    HAUTEUR = 500
    RMAX = 8
    MARGE = 30

    while True: #Choix des paramètres du Lidar

        listeSerie = lambda: serial.tools.list_ports.comports()

        listePorts = listeSerie()

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
                sg.Input(size=(50, 1),key="dossier"),
                sg.FolderBrowse(size=(8,1),target="dossier",button_text="Naviguer",)
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

    parametres_eregistres = {"grille":None,"secondaire":None,"distance":None}
    
    while True:

        colOptions = [
                [sg.Text('Grille',size=(12,1)),sg.Combo(values=["Angulaire","Linéaire","Aucune"],default_value=("Angulaire",parametres_eregistres['grille'])[parametres_eregistres["grille"] != None],size=(10,1),key="grille")],
                [sg.Text('Grille secondaire',size=(12,1)),sg.Combo(values=["1/10","1/5","1/2","Aucune"],default_value=("Aucune",parametres_eregistres['secondaire'])[parametres_eregistres["secondaire"] != None],size=(10,1),key="sousGrille")],
                [sg.Text('Distance max',size=(12,1)),sg.Spin(values=[_+1 for _ in range(10)],initial_value=(RMAX,parametres_eregistres['distance'])[parametres_eregistres["distance"] != None],size=(10,1),key="max")]
                    ]

        layoutScan = [
                [sg.Canvas(size=(LARGEUR+2*MARGE, HAUTEUR+2*MARGE), key='canvas'),sg.VerticalSeparator(),sg.Column(colOptions,vertical_alignment='top')],
                [sg.Text('Nom du fichier :', size=(16, 1)),sg.Input(size=(30, 1),key="nomFichier")],
                [sg.Button('Enregistrer', size=(10, 1)),sg.Button('Annuler', size=(10, 1))]
                    ]
        

        windowScan = sg.Window('Scan Lidar', layoutScan)
        windowScan.Finalize()
        
        canvas_elem = windowScan['canvas']
        canvas = canvas_elem.TKCanvas
        canvas.delete("all")
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
            
            rMax = values['max']
            grilleAngle,grilleDistance = False,False
            grilleAngle = values['grille'] == "Angulaire"
            grilleDistance = values['grille'] == "Linéaire"
            corespondanceSousGrille = {'Aucune':False,'1/10':10,'1/5':5,'1/2':2}
            sousGrille = corespondanceSousGrille[values['sousGrille']]
                    
            canvas.delete("all")
            dessinerEchelle(canvas,grilleAngle=grilleAngle,grilleDistance=grilleDistance,sousGrille=sousGrille,largeur=LARGEUR,hauteur=HAUTEUR,rMax=rMax,marge=MARGE)
            for a,d in zip(data[0],data[1]):
                dessinerPoints(canvas,a,d,grilleAngle=grilleAngle,grilleDistance=grilleDistance,largeur=LARGEUR,hauteur=HAUTEUR,rMax=rMax,marge=MARGE)


        parametres_eregistres = {"grille":values['grille'],"secondaire":values['sousGrille'],"distance":values['max']}

        try:
            lidar.join()
        except Exception as e:
            print(e)

        HWND = canvas.winfo_id()
        rect = win32gui.GetWindowRect(HWND)
        im = ImageGrab.grab(rect)
        im.save(nomComplet[:-4]+".png")


        windowScan.close()


        sleep(5)

        with open(nomComplet, 'w',newline='') as fichierData:
            spamwriter = writer(fichierData, delimiter=',',dialect='excel')
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
    