# Retail Radar Deutschland

Eine mobile Web-App mit täglichen Top-10-Nachrichten aus den letzten sieben Tagen.

## Einrichtung ohne Programmierung

1. Auf github.com ein öffentliches Repository `retail-radar` anlegen (ohne README-Vorlage).
2. Alle Dateien und Ordner dieses ZIP-Pakets in den Hauptordner des Repositorys hochladen. Wichtig: `.github/workflows/update.yml` muss mit hochgeladen werden. GitHub erlaubt das Hochladen ganzer Ordner über die Weboberfläche per Drag & Drop; andernfalls den GitHub-Desktop-Client nutzen.
3. Unter **Settings → Pages → Build and deployment → Source** die Option **GitHub Actions** wählen.
4. Unter **Actions → Daily Retail Radar → Run workflow** einmal manuell starten. Der Workflow holt RSS-Meldungen und veröffentlicht die App.
5. Unter **Settings → Pages** die Adresse öffnen: `https://DEIN-NAME.github.io/retail-radar/`.
6. Auf Android in Chrome die Seite öffnen und im Menü **Zum Startbildschirm hinzufügen** oder **App installieren** auswählen.

## Betrieb

Automatische Aktualisierung täglich 07:30 Uhr Europe/Berlin (GitHub Actions kann sich verzögern). Die App ruft bei jedem Öffnen die zuletzt veröffentlichte `news.json` ab. Wenn alle Quellen ausfallen, schlägt der Workflow fehl und die zuletzt veröffentlichte Version bleibt sichtbar. Eine Aktualitätskontrolle ist anhand des Datums möglich.

## Einschränkungen

Google News RSS ist nicht garantiert vollständig und primär für persönliche, nichtkommerzielle Nutzung vorgesehen. Die zehn Meldungen werden nach Titelheuristik und nicht nach einer tiefen KI-Analyse sortiert. Quellen können Paywalls haben. Google News Links können auf Zwischenseiten führen. Ähnliche Artikel werden anhand von Titelähnlichkeit zusammengeführt, nicht durch semantische Clusterbildung. GitHub Pages ist öffentlich erreichbar. Keine API-Schlüssel oder personenbezogenen Daten in das Repository einfügen.

## Anpassung

`collect.py`: `SOURCES`, `TOPICS`, `QUERIES` und die Funktion `rank` ändern. Danach committen und den Workflow manuell starten. Für ein echtes LLM-Ranking kann später ein gesicherter serverseitiger API-Aufruf ergänzt werden.
