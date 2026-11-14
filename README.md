# WÖk-Wirkungsportal Parlament

Dieses Repository veröffentlicht das Wirkungsportal als vollständig statische
GitHub-Pages-Site. Es enthält keine Vercel-Runtime, keine API-Secrets und keine
persistenten Nutzerdaten.

Produktionsstände werden als unveränderliche Release-Artefakte bereitgestellt
und über den manuellen Pages-Workflow veröffentlicht. Die fachlichen Quellen
und der reproduzierbare Build liegen im Produktionsrepository.

## Geprüftes Produktionsartefakt veröffentlichen

Quellrepository ist `sustynats/wirkungsoekonomie-produktiv`. Der Workflow
liest daraus keine privaten Zugangsdaten. Er veröffentlicht nur ein manuell
gewähltes Archiv aus einem GitHub Release dieses Publishing-Repositories.
Der Zeitplan überwacht den eingefrorenen historischen Stand und kann keine
Seite veröffentlichen.

1. Auf dem freigegebenen Quellcommit den unveränderten statischen Export
   bauen und prüfen. `WOEK_SOURCE_COMMIT` ist der vollständige Quellcommit.
   `WOEK_SOURCE_FINGERPRINT` ist der mit
   `npm run static-release:update-trigger` aus genau diesem Baum gebildete
   Fingerprint. Die beiden Werte werden im Build-Manifest festgehalten.
2. Aus dem öffentlichen Export das Archiv bilden. Die Dateien des Exports
   liegen direkt im Archiv, einschließlich `.nojekyll` und `CNAME`, zum
   Beispiel `tar -C _static-public-site -czf /tmp/woek-parlament-site.tar.gz .`.
   Den SHA-256 lokal ermitteln und die Datei als Release-Asset hochladen.
3. Den Workflow **Deploy verified Parliament snapshot** auf `main` starten.
   Eingaben sind die numerische `asset_id`, der lokal geprüfte
   `archive_sha256`, `source_commit`, `source_fingerprint` und der aktuelle
   Live-Fingerprint aus `/_woek-build-manifest.json` als
   `previous_fingerprint`. Dieselben Eingaben mit einem aufbewahrten
   geprüften Archiv ermöglichen den manuellen Rückwechsel.
