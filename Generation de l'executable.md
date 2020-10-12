# Génération de l'exécutable à partir du code source

Le script est écrit en Python 3, il faut donc avoir une version de python 3 installée pour pouvoir générer un exécutable.
Il a été testé sous python 3.8, c'est possible que des versions antérieures posent problème.

## Exécution à partir du code

Le programme doit pouvoir fonctionner depuis le code avant de générer l'exécutable Windows.

Il faut installer certaines bibliothèques à l'aide de `pip` en se plaçant dans le dossier racine :

    pip install -r requirements.txt

Le code peut ensuite être executé :

    python appLidar.py

## Génération de l'exécutable

On utilise `cx_Freeze` pour conditionner le code.
Le paquet doit être installé en version 6.1, la version actuelle (6.3) ne parvenant pas à générer le _.exe_. Si les dépendances ont été installées via le fichier _requirements.txt_, le paquet devrait être présent dans la version requise.

Le ficher _setup<span/>.py_ contient les instructions nécessaires à la création de l'exécutable.

**Attention :** Le fichier ne peut pas être exécuté tel quel, certaines modifications sont nécessaires en fonction de l'installation locale de python :

- Le champ `include_files` de `build_exe_options` doit être modifié avec les chemins locaux de _tcl86t.dll_ et _tk86t.dll_. Ces ficiers se trouvent dans le dossier DLLs du répertoire d'installation de python.

  ```python
  "include_files":[
      "répertoire_d'instalation_de_python/DLLs/tcl86t.dll",
      "répertoire_d'instalation_de_python/DLLs/tk86t.dll",
      ]
  ```

- Il faut également renseigner les variables d'environnement _TCL_LIBRARY_ et _TK_LIBRARY_ :

  ```python
  os.environ['TCL_LIBRARY'] = "répertoire_d'instalation_de_python/tcl/tcl8.6"
  os.environ['TK_LIBRARY'] = "répertoire_d'instalation_de_python/tcl/tk8.6"
  ```

On peut ensuite exécuter le script :


    python setup.py build


Le script génère un dossier _build_ contenant le _.exe_ et les fichiers dont il a besoin.
