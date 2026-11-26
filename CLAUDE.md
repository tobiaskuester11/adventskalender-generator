# Adventskalender

Adventskalender aus 24 privaten Fotos: ein Foto-Collagenblatt zum Bedrucken plus
ein zweites Blatt mit goldenen Türchen, das exakt darüber gelegt werden kann. Die
Türchen werden aufgeschnitten und zur Seite aufgeklappt, um darunter jeweils ein
Foto freizulegen.

## Ergebnis (Soll-Zustand)

Im Projektordner liegen genau diese drei Dateien (fertige Druckvorlagen):

- `Adventskalender_Fotos.png` – Foto-Collage, 30 × 20 cm (Querformat), 300 dpi.
- `Adventskalender_Tuerchen.png` – Türchen-Overlay, exakt gleiche Pixel-/Bodenmaße,
  liegt deckungsgleich über dem Fotoblatt.
- `Hintegrund.jpg` – Hintergrundbild für das Türchen-Blatt (kein Kalenderfoto!).

Dazu:

- `Quellfotos/` – die 24 Original-Fotos, umbenannt in `Foto_01.<ext>` …
  `Foto_24.<ext>` in genau der Reihenfolge, in der sie im Raster erscheinen
  (Leserichtung: oben links → unten rechts). Originalformat/-qualität
  unverändert, nur umbenannt und einsortiert.
- `scripts/build_calendar.py` – erzeugt Blatt 1 aus `Quellfotos/`.
- `scripts/build_doors.py` – erzeugt Blatt 2 aus `scripts/layout.json`
  (von Schritt 1) und `Hintegrund.jpg`.
- `scripts/layout.json`, `scripts/numbers.json` – Zwischenstände (Rasterkoordinaten,
  Zahlen-/Scharnier-Zuordnung), werden bei jedem Lauf neu geschrieben.

## Reproduzieren

```
cd scripts
python build_calendar.py
python build_doors.py
```

Erwartet `pillow`, `pillow-heif` (für `.heic`-Dateien). Beide Skripte sind
self-contained und finden ihre Pfade relativ zu ihrem eigenen Speicherort
(`PROJECT_DIR = Elternordner von scripts/`), funktionieren also auch nach
Verschieben/Umbenennen des Projektordners.

Beim erneuten Lauf entsteht exakt dasselbe Ergebnis (fester `RANDOM_SEED = 42`
in `build_doors.py` für Zahlen-Shuffle und Scharnier-Seite). Für eine neue
zufällige Mischung: `RANDOM_SEED` in `build_doors.py` ändern.

## Spezifikation

**Blatt 1 – Foto-Collage**
- Canvas 30 × 20 cm @ 300 dpi, Querformat.
- Raster: `cols × rows` = Teiler von 24, dessen Zellen-Seitenverhältnis dem
  geometrischen Mittel der 24 Foto-Seitenverhältnisse am nächsten kommt
  (aktuell 6 × 4, da Fotos im Schnitt eher hochformatig sind, Ø-Verhältnis ≈ 0,77).
- Rand zum Blattrand und Abstand zwischen allen Zellen: exakt 1 cm (kein
  Mindestwert nötig, ergibt sich exakt aus der Rasterkonstruktion).
- Jedes Foto wird unverzerrt und ohne Beschnitt in seine Zelle eingepasst
  ("contain"-Skalierung, zentriert). Dadurch sind die Fotos **ungefähr**
  gleich groß (gebunden durch die einheitliche Zellgröße), aber nicht exakt
  gleich groß, da die Seitenverhältnisse variieren.

**Blatt 2 – Türchen**
- Gleiche Canvas-Maße wie Blatt 1, exakte Pixeldeckung.
- Hintergrund: `Hintegrund.jpg` wird **nicht** zugeschnitten oder gedreht,
  sondern direkt (ggf. nicht-uniform gestreckt) auf die volle Canvas-Größe
  skaliert, dann leicht abgedunkelt (40 % Schwarzanteil) und leicht weich-
  gezeichnet, damit die goldenen Linien/Zahlen lesbar bleiben.
- Jedes Türchen bekommt einen goldenen Rahmen, der **exakt der gerenderten
  Fotogröße** entspricht (nicht der Rasterzelle!) – also oben/unten/links/rechts
  identisch mit der Bounding-Box des jeweiligen Fotos aus Blatt 1.
- Rahmenlinien: oben und unten immer gezeichnet; links **oder** rechts
  genau eine der beiden, **zufällig pro Türchen gewählt** (keine Musterbildung
  nach Spalte/Reihe) – die nicht gezeichnete Seite ist implizit die
  Öffnungs-/Scharnierseite beim Aufschneiden.
- Linienstärke: dünn (bewusst 20 % der ursprünglich getesteten, dickeren Linie).
- Zahlen 1–24: zufällig auf die 24 Türchen gemischt, einheitliche (nicht pro
  Zelle skalierte), eher kleine Schriftgröße, Schriftart **Old English Text MT**
  (Gold, mit leichtem Schlagschatten), immer mittig auf dem jeweiligen Foto
  zentriert (nicht auf der Rasterzelle).

**Druck:** beide Blätter bei 100 % Skalierung (nicht „an Seite anpassen")
auf gleich großes Papier drucken, exakt übereinanderlegen; Türchen an den
gezeichneten Goldlinien aufschneiden, an der linien-losen Seite aufklappen.

## Entscheidungen & Missverständnisse unterwegs

Festgehalten, damit der Prozess nachvollziehbar bleibt und nicht wiederholt
missverstanden wird:

1. **"Bereits zugeschnitten" ≠ einheitliches Seitenverhältnis.** Die 24
   Ursprungsfotos hatten stark unterschiedliche Formate (16:9 bis extrem
   hochformatig). Nutzer-Entscheidung: Seitenverhältnisse **nicht** antasten
   (kein Zuschneiden, kein Verzerren) – stattdessen Fotos in ihre Zelle
   einpassen ("contain").
2. **2 Screenshots im Ordner** wurden auf Nachfrage bewusst als 2 der 24
   Kalenderbilder bestätigt (nicht aussortiert).
3. **`Hintegrund.jpg` ist kein Kalenderfoto**, sondern explizit das
   Hintergrundbild für Blatt 2. Wurde im Gespräch zweimal ersetzt: zunächst
   ein als `.jpg` fehlbenanntes AVIF-Foto (Weihnachtsmarkt, 2000×1000), dann
   vom Nutzer durch ein neues JPEG ersetzt (1771×1181 ≈ exakt 3:2, passt
   genau auf 30×20 cm, daher keine Verzerrung mehr nötig).
4. **Erster Layout-Ansatz (verworfen):** ein zeilenbasiertes "justified
   gallery"-Layout, bei dem jede Zeile exakt auf die Blattbreite skaliert
   wurde. Nachteil: Zeilen mit wenigen Bildern wurden unverhältnismäßig groß
   (z. B. 2 Bilder, die eine ganze Zeile füllen mussten). Nutzer wollte
   stattdessen ungefähr gleich große Bilder → Umstieg auf einheitliches
   Raster mit "contain"-Einpassung (siehe oben).
5. **Erstes Türchen-Design (verworfen):** bunte, gefüllte Türchen
   (Rot/Grün/Gold) mit abgerundeten Ecken, Sternchen-Dekor und getrennter
   Schnitt-/Falzlinien-Symbolik (durchgezogen vs. gestrichelt) wirkte zu
   unruhig ("sieht schlecht aus"). Vereinfacht auf reine goldene
   Rahmenlinien ohne Füllung.
6. **Seitenformat gewechselt:** Canvas war zunächst Hochformat (20 cm breit ×
   30 cm hoch), auf Wunsch auf Querformat gedreht (30 cm breit × 20 cm hoch).
7. **Schriftart "Chaucer" existiert nicht** unter Windows. Nach Rückfrage
   als thematisch passendster verfügbarer Ersatz **Old English Text MT**
   gewählt (Alternativen wären Vivaldi, Lucida Calligraphy, French Script MT
   gewesen).
8. **Türchengröße:** zunächst an der Rasterzelle orientiert (einheitlich),
   dann auf Wunsch geändert auf die **exakte Fotogröße** (Bounding-Box des
   jeweiligen Bildes), da die Rasterzelle wegen "contain"-Einpassung größer
   sein kann als das sichtbare Foto.
9. **Öffnungsseite der Türchen:** zunächst nach Spaltenparität alternierend
   (links/rechts je nach Spalte), auf Wunsch durch echte Zufallsmischung
   pro Türchen ersetzt.
