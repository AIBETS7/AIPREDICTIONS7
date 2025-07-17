# Automatización local de scraping y push automático

Este proyecto incluye un script maestro para automatizar el scraping de todas las fuentes principales y subir los datos al repositorio automáticamente.

## ¿Qué hace el script?
- Ejecuta todos los scrapers principales del backend (Sofascore, Flashscore, BetsAPI, Promiedos, LaLiga, Transfermarkt, Understat, Odds API, Sportmonks...)
- Hace `git add`, `commit` y `push` automático de los archivos de datos generados si hay cambios.
- Es seguro para ejecutarse varias veces al día.

## Uso manual

Desde la terminal:
```bash
cd backend
./all_scrapers_local_automation.sh
```

## Automatización con cron (Mac/Linux)
Puedes programar el scraping y push automático con cron. Ejemplo para ejecutarlo cada día a las 7:00:

1. Abre el editor de cron:
   ```bash
   crontab -e
   ```
2. Añade la siguiente línea (ajusta la ruta a tu proyecto):
   ```
   0 7 * * * cd /Users/willymartinez/my-football-predictions/backend && ./all_scrapers_local_automation.sh >> scraping.log 2>&1
   ```
   Esto ejecutará el script cada día a las 7:00 y guardará el log en `scraping.log`.

## Notas
- El script activa el entorno virtual automáticamente si existe.
- Si algún scraper falla, el proceso sigue con los demás y muestra un mensaje en consola/log.
- Si no hay cambios en los datos, no hace push.

---
¿Dudas? Puedes personalizar el script para añadir/quitar scrapers según tus necesidades. 