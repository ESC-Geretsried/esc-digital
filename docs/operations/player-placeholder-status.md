# Spielerbild-Placeholder

Status: **OPEN**

Im übergebenen Arbeitskontext war keine kanonische Placeholder-Binärdatei
enthalten. Deshalb wurde kein Ersatzbild erzeugt, heruntergeladen oder als
vermeintlich kanonisch eingecheckt. Die Spielerkomponente reserviert den
Bild-Slot weiterhin deterministisch und kennzeichnet den offenen Asset-Stand.

Abschlusskriterium: Die ausdrücklich freigegebene Binärdatei wird unter einem
kanonischen Assetpfad persistiert, ihr SHA-256 im Validator fest gebunden und
für alle Spieler ohne eigenes Foto verwendet.
