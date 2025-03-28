# Geocaching-Journal
Generation of a journal of geocaching logs

(version française ci-dessous)

## Features

* generation of XML files containing logs and list of pictures
* download of a backup of the logs' web pages
* customization of HTML output with CSS styles or inside the scripts
* identification of logs without pictures
* generate additionnal list of selected pictures
* authentication to website to download logs (-u)
* exclude some types of cache or log (-x)
* requires no external modules

These scripts were tested on Python 3.11.

## Installation

* Make sure Python is available on you machine
* Use Git to get the source or extract an [archive](https://github.com/GarenKreiz/Geocaching-Journal/archive/master.zip)
* On Windows, one may extract a binary version of the program from a ZIP archive associated to the [latest release](https://github.com/GarenKreiz/Geocaching-Journal/releases/latest)
* To allow icons support in the logbook, download the following SVG files owned by Groundspeak in your working directory
  * http://www.geocaching.com/app/ui-icons/sprites/cache-types.svg
  * http://www.geocaching.com/images/icons/fave_fill_16.svg

## Usage

* On the geocaching web site, verify that your date format preferences are in numerical form ("MM/DD/YY" not supported)
* Logs : Save locally the content of the web page https://www.geocaching.com/my/logs.aspx?s=1 , for example in file **geocaching_logs.html**. Save it as a plain HTML file.
* Trackables : Save the page https://www.geocaching.com/my/logs.aspx?s=2
* Geocaches : on the cache webpage, scroll to the bottom to display all the logs, in the browser, use right-click on the page to inspect the source code, select the HTML tag and copy the outer content then paste it in a local file
* Run the [processLogs.py](processLogs.py) script to generate an XML file for example **logbook.xml**.
* It create a directory Logs to save the logs' HTML page before parsing them.
* Authentication to the geocaching website is necessary to download logs (first use of processLogs, new logs or -r option)
* Warning: the script may generate lots of accesses to www.geocaching.com without timeout. Check the License Agreement of this web site. It may be safe to run the program to get the log for small periods of time ("-s" and "-e" option)

```
$ python processLogs.py -u user/password geocaching_logs.html logbook.xml
```
* To avoid using the geocaching ids in the command line, they can be stored in a file  **~/.georc** (also used **geo-\***, line `USERNAME="pseudo"` and line `PASSWORD="mdp"`)

* Check the content of the file : the title and description can be directly edited in the file [logbook_header.xml](logbook_header.xml) 
* Run the [xml2print.py](xml2print.py) script to generate an HTML file **logbook.html**

```
$ python xml2print.py logbook.xml logbook.html
```

* Verify the result in any browser. Warning: it can take quite a long time depending on the number of logs and pictures and the speed of the Internet access!
* Click on images to display them or select them.

```
$  firefox logbook.html
```

* The two steps can be launched with a single command if the output file is an HTML file

```
$ python processLogs.py geocaching_logs.html logbook.html
```

* To generate a mosaic file **mosaic.html**

```
$ python xml2print.py -m mosaic.html logbook.xml logbook.html
```

* Before launching the executable versions, copy the files [logbook_header.xml](logbook_header.xml) and [logbook.css](logbook.css) to the working directory and customize them.

```
\ processLogs.exe geocaching_logs.html logbook.html
```
or 
```
\ processLogs.exe geocaching_logs.html logbook.xml
\ xml2print.exe logbook.xml logbook.html
```

* When the text of a log entry is change online or when pictures are added to a log, use the "--refresh" option to force the update of the cache of the log web pages. For example, for the logs on day AAAA/MM/DD, do

```
$ python processLogs.py -u user/password -s AAAA/MM/DD -e AAAA/MM/DD -r geocaching_logs.html logbook.html
```

## Generated web page

For each log, the cache page and the log page are directly accessible by clicking on the corresponding text. Clicking on a picture opens a new windows with the original bigger version of the picture. The picture can be selected, adding it to the selected pictures' list that appears at the end of the main page. 

## Help

```
$ python processLogs.py -h
$ python xml2print.py -h 
```

## Customization

In [processLogs.py](processLogs.py)

* string to match to classify a picture as a panorama (currently captions with "panoram")

In file [logbook_header.xml](logbook_header.xml)

* title of generated document and an optional URL to a web site
* description of the journal

In the generated XML file

* insertion of new page markers <page/> for improving the layout of the printing version

In [xml2print.py](xml2print.py) 

* max numbers of columns for pictures 
* options at execution : --groupPanoramas, --compactGallery, --mosaic mosaic_file.html

In [logbook.css](logbook.css)

* background images => url("remote or local image")
* colors
* sizes and indentations

<hr/>

# Geocaching-Journal
Generation d'un journal des notes de géocaching

## Caractéristiques

* génération d'un fichier XML  contenant le texte des notes et la liste des images
* téléchargement d'une sauvegarde locale des pages web des notes
* identification des notes sans photo
* génération d'une sélection de photos pendant la consultation
* authentification sur le site geocaching (-u)
* exclusion de certains types de cache ou de log (-x)
* paramétrisation du fichier HTML généré avec des styles CSS ou par modification des scripts

Ces scripts ont été testés avec Python 3.11

## Installation

* Vérifier que Python est bien installé sur votre machine
* Utiliser Git pour récupérer les sources ou  extraire une [archive](https://github.com/GarenKreiz/Geocaching-Journal/archive/master.zip)
* Sur Windows, il est possible d'utiliser une version binaire du programme en utilisant l'archive ZIP de la [dernière distribution](https://github.com/GarenKreiz/Geocaching-Journal/releases/latest)
* Pour avoir des icones dans le journal, télécharger les fichiers SVG suivants dans votre répertoire de travail :
  * http://www.geocaching.com/app/ui-icons/sprites/cache-types.svg
  * http://www.geocaching.com/images/icons/fave_fill_16.svg

## Utilisation

* Vérifier les préférences du site geocaching : le format des dates doit être numérique (à l'exception du format "mm/jj/aa")
* Logs : Faire une sauvegarde locale de la page contenant tous vos logs https://www.geocaching.com/my/logs.aspx?s=1 , par exemple dans le fichier **geocaching_logs.html**. Le format de la sauvegarde doit être de l'HTML simple.
* Trackables : Faire une sauvegarde de la page https://www.geocaching.com/my/logs.aspx?s=2
* Géocaches : Afficher la page de la cache, scroller pour faire apparaître tous les logs, inspecter le code source (click droit), selectionner le tag HTML global et le copier (copie externe), coller le contenu dans un fichier local
* Lancer le script [processLogs.py](processLogs.py) pour générer un fichier XML **logbook.xml**
* Cela crée un répertoire **Logs** contenant un cache local des descriptions HTML des notes
* La connexion au site Geocaching est nécessaire pour télécharger les notes (lancement initial, nouvelles notes ou option -r)
* Note: le script engrendre une rafale de requêtes vers www.geocaching.com sans temporisation. Vérifiez les clauses d'utilisation de ce site web. Il est recommandé de ne récupérer à chaque fois que les logs pour une courte période (options "-s" et "-e")

```
$ python processLogs.py -u user/password geocaching_logs.html logbook.xml
```

* Pour éviter de saisir les identifiants geocaching, il est possible de les mettre dans un fichier **~/.georc** (fichier utilisé aussi par **geo-\***, ligne `USERNAME="pseudo"` et ligne `PASSWORD="mdp"`)

* Vérifier le contenu du fichier : le titre et la description du journal peuvent être modifiés dans le fichier [logbook_header.xml](logbook_header.xml)
* Lancer le script [xml2print.py](xml2print.py) pour générer un fichier HHTML

```
$ python xml2print.py logbook.xml logbook.html
```

* Vérifier le résultat avec un navigateur web. Cela peut prendre un certain temps, en fonction du nombre de notes et de photos et en fonction du débit d'accès à l'Internet.
* Cliquer sur les images pour les visualiser ou les sélectionner.

```
$  firefox logbook.html
```

* Il est possible d'enchaîner les deux étapes en spécifiant un fichier de sortie en HTML.

```
$ python processLogs.py geocaching_logs.html logbook.html
```

* Pour générer une mosaïque des images **mosaic.html**

```
$ python xml2print.py -m mosaic.html logbook.xml logbook.html
```


* Avant d'exécuter les versions binaires des programmes (Windows), copier les fichiers [logbook_header.xml](logbook_header.xml) and [logbook.css](logbook.css) dans le répertoire de travail puis éventuellement en modifier le contenu pour paramétrer la génération.

```
\ processLogs.exe geocaching_logs.html logbook.html
```
ou
```
\ processLogs.exe geocaching_logs.html logbook.xml
\ xml2print.exe logbook.xml logbook.html
```

* Si le texte d'une entrée du journal a été modifié ou si des photos ont été ajoutées, il faut utiliser l'option "--refresh" pour forcer la mise à jour du cache local des pages web des logs. Par exemple, pour la journée AAAA/MM/JJ, faire

```
$ python processLogs.py -u user/password -s AAAA/MM/JJ -e AAAA/MM/JJ -r geocaching_logs.html logbook.html
```

## Page web générée

Pour chaque entrée du journal, le page de la cache courante et celle du log sont directement accessibles en cliquant sur le texte. En cliquant sur une photo, une nouvelle fenêtre s'ouvre qui l'affiche dans sa taille d'origine et permet de la sélectionner. La liste des photos sélectionnée apparaît à la fin de la page principale.

## Aide

```
$ python processLogs.py -h
$ python xml2print.py -h 
```

## Paramétrage

Dans le fichier [processLogs.py](processLogs.py)

* chaîne de caractère permettant de reconnaître les photos en mode panorama (actuellement "panoram" dans la légende)

Dans le fichier [logbook_header.xml](logbook_header.xml)

* titre du journal et éventuellement l'URL du lien vers un site web
* description ou introduction du journal

Dans le fichier XML généré

* insertion de sauts de page pour améliorer l'impression  <page/>
* modification du pied de page

Dans le fichier [xml2print.py](xml2print.py) 

* nombre maximum de colonnes des photos 
* options pour l'exécution : --groupPanoramas, --compactGallery, --mosaic fichier_mosaic.html

Dans le fichier [logbook.css](logbook.css)

* image de fond : option url("image distante ou sur le web")
* couleurs
* tailles et indentations

# Samples - Echantillons

* [Geocaching USA 2012](http://www.garenkreiz.net/Geocaching-Journal/logbook_USA_2012.html)
* [Geocaching journal 2001-2010](http://www.garenkreiz.net/Geocaching-Journal/Journal_2001-2010.html)
* [Geocaching journal 2011-2016](http://www.garenkreiz.net/Geocaching-Journal/Journal_2011-2016.html)
* [Cache journal "Following the furrow"](http://www.garenkreiz.net/Geocaching-Journal/Journal_Following_the_furrow_202404.html)
  
![Customized example](https://raw.githubusercontent.com/GarenKreiz/Geocaching-Journal/master/logbook_example.jpg)


# Releases - Versions

* 1.6.0 : changes for log ids on the geocaching website
* 1.5.0 : geocaching id and password stored in ~/.georc file
* 1.4.0 : button to select some images that will be displayed as a list at the end of the page
* 1.3.0 : popup window for images, mosaic of images
* 1.2.0 : journal for trackables, option to exclude some types of logs, option for galleries presentation
* 1.1.0 : generation of a journal between two dates
* 1.0.0 : initial release

# Credits - Remerciements

Merci aux testeurs Ato-Club et TofLaBeuze.

Merci au contributeur Mides pour la simplification du code Python.
