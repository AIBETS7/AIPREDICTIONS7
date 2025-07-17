#!/bin/bash
# Añade una tarea cron para ejecutar el scraper de notbetting todos los días a las 12:00
CRON_JOB="0 12 * * * cd $(dirname "$0") && /usr/bin/python3 notbetting_scraper.py >> logs/notbetting_cron.log 2>&1"
# Evitar duplicados
(crontab -l | grep -v 'notbetting_scraper.py'; echo "$CRON_JOB") | crontab -
echo "Tarea cron programada para ejecutar notbetting_scraper.py todos los días a las 12:00" 