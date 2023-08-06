# camera-server
Macht rohe Bayer-Frames über HTTP verfügbar

## Argumente und Benutzung
```
pi@raspberrypi:~/camera-server $ python3 camserver.py --help
usage: camserver.py [-h] [--address ADDRESS] [--port PORT]

Capture bayer frames and serve them over HTTP

optional arguments:
  -h, --help         show this help message and exit
  --address ADDRESS  Binding address for the HTTP server
  --port PORT        Port the HTTP server will listen on
```

Nachdem der Webserver gestartet wurde, stehen zwei mögliche URLs zum Aufruf bereit:

`http://127.0.0.1:3000/raw` gibt das Rohbild als Numpy-Array zurück und schreibt in folgende HTTP-Headers:

  * `X-Array-Width`: Breite des Arrays
  * `X-Array-Height`: Höhe des Arrays
  * `X-Array-Channels`: Anzahl der Kanäle des Arrays
  * `X-Array-Type`: NumPy Datentyp des Arrays

`http://127.0.0.1:3000/red` verhält sich gleich wie `/raw`, gibt aber nur den Rot-Kanal des Bildes zurück, um die Übertragungszeit zu verkürzen.

Zum Beenden des laufenden Servers reicht ein einfaches `Ctrl-C`.

## Dummy-Server
Um die Software ohne Kamera testen zu können, ist in diesem Repo eine `dummy_camserver.py`. Ihr kann zusätzlich ein Bild angegeben werden, dass dann über HTTP verbreitet wird, ohne die Raspberry Pi Camera benutzen zu müssen.
