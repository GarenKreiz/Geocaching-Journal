# Geocaching-Journal
Generation of a journal of geocaching logs

(version française ci-dessous)

## Features

* generation of XML files containing logs and list of pictures
* download a backup of the logs' web pages
* customization of HTML output with CSS styles or inside the scripts
* identification of logs without pictures
* requires no external modules

These scripts were tested on Python 2.7.

## Usage

* On the geocaching web site, verify that your date format preferences are in numerical form ("MM/DD/YY" not supported)
* Save locally the content of the web page https://www.geocaching.com/my/logs.aspx?s=1 , for example in file **geocaching_logs.html**. Save it as a plain HTML file.
* Run the [processLogs.py](processLogs.py) script to generate an XML file for example **logbook.xml**.
* It create a directory Logs to save the logs' HTML page before parsing them.
* Warning: the script may generate lots of access to www.geocaching.com without timeout. Check the License Agreement of this web site.

```
$ python processLogs.py geocaching_logs.html logbook.xml
```

* Check the content of the file : the title and description can be directly edited in the file or in [processLogs.py](processLogs.py) 
* Run the [xml2print.py](xml2print.py) script to generate an HTML file **logbook.html**

```
$ python xml2print.py logbook.xml logbook.html
```

* Verify the result in any browser. Warning: it can take quite a long time depending on the number of logs and pictures and the speed of the Internet access!

```
$  firefox logbook.html
```

* The two steps can be launched with a single command if the output file is an HTML file

```
$ python processLogs.py geocaching_logs.html logbook.html
```

## Customization

In [processLogs.py](processLogs.py)

* title of the output page
* description of the journal
* string to match to classify a picture as a panorama (currently captions with "panoram")

In XML file

* insertion of new page markers <page/> for improving the layout of the printing version

In [xml2print.py](xml2print.py) 

* numbers of columns for pictures

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
* paramétrisation du fichier HTML généré avec des styles CSS ou par modification des scripts

Ces scripts ont été testé avec Python 2.7

## Usage

* Vérifier les préférences du site geocaching : le format des dates doit être numérique (à l'exception du format "mm/jj/aa")
* Faire une sauvegarde locale de la page contenant tous vos logs https://www.geocaching.com/my/logs.aspx?s=1 , par exemple dans le fichier **geocaching_logs.html**. Le format de la sauvegarde doit être de l'HTML simple.
* Lancer le script [processLogs.py](processLogs.py) pour généré un fichier XML **logbook.xml**
* Cela crée un répertoire **Logs** contenant un cache local des descriptions HTML des notes
* Note: le script engrendre une rafale de requêtes vers www.geocaching.com sans temporisation. Vérifiez les clauses d'utilisation de ce site web.
```
$ python processLogs.py geocaching_logs.html logbook.xml
```

* Vérifier le contenu du fichier : le titre et la description du journal peuvent être modifiés dans le fichier ou au début du fichier [processLogs.py](processLogs.py)
* Run the [xml2print.py](xml2print.py)  script to generate an HTML file

```
$ python xml2print.py logbook.xml logbook.html
```

* Vérifier le résultat avec un navigateur web. Cela peut prendre un certain temps, en fonction du nombre de notes et de photos et en fonction du débit d'accès à l'Internet.

```
$  firefox logbook.html
```

## Paramétrage

In [processLogs.py](processLogs.py)

* titre du journal
* description ou introduction du journal
* chaîne de caractère permettant de reconnaître les photos en mode panorama (actuellement "panoram" dans la légende)

In XML file

* insertion de sauts de page pour améliorer l'impression  <page/>

In [xml2print.py](xml2print.py) 

* disposition en colonnes des photos

In [logbook.css](logbook.css) logbook.css

* image de fond : option url("image distante ou sur le web")
* couleurs
* tailles et indentations

# Sample - Echantillon

![Example](https://raw.githubusercontent.com/GarenKreiz/Geocaching-Journal/master/logbook_example.jpg)
