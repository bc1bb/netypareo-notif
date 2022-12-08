#!/usr/bin/env python3
# PLANNING NETYPAREO BOT
import os
from urllib.request import urlretrieve
from icalendar import Calendar
from datetime import datetime, timezone
import pytz
import requests

webhook_url = open("credits").readlines()[0].split("\n")[0]
ical_link = open("credits").readlines()[1].split("\n")[0]
netypareo_url = open("credits").readlines()[1].split("planning")[0]
logo_url = open("credits").readlines()[2].split("\n")[0]
school_name = open("credits").readlines()[3].split("\n")[0]

cal = Calendar()
urlretrieve(ical_link, "ical.ical")

today = []

# each item = [summary, dtstart, dtend], pytz set to Paris

def get_pause(debut, fin):
    # cour commence 9h*
    if debut.hour == 9:
        # fini 12h45, pause = 10h30
        if fin.hour == 12 and fin.minute == 45:
            return "10:30"

        # fini 13h*, pause = 11h
        if fin.hour == 13:
            return "11:00"

    # cour commence 13h30 fini 17h30, pause = 15h30
    elif debut.hour == 13 and debut.minute == 30:
        if fin.hour == 17 and fin.minute == 30:
            return "15:30"


with open("ical.ical", "r") as f:
    ecal = Calendar.from_ical(f.read())
    # pour chaque evenement dans le iCalendar
    for component in ecal.walk():
        if component.name == "VEVENT":
            ## PROD
            morning = datetime.now().replace(hour=8, minute=0, tzinfo=timezone.utc)
            evening = datetime.now().replace(hour=20, minute=0, tzinfo=timezone.utc)

            ## DEBUG
            # morning = datetime.fromtimestamp(1670492182).replace(hour=8, minute=0, tzinfo=timezone.utc)
            # evening = datetime.fromtimestamp(1670492182).replace(hour=20, minute=0, tzinfo=timezone.utc)

            # Si l'element est inclut entre ce matin et ce soir
            if morning < component.decoded("dtend").replace(tzinfo=timezone.utc) < evening:
                today.append([component.get("summary"),
                              pytz.utc.localize(component.decoded("dtstart").replace(tzinfo=None)).astimezone(
                                  pytz.timezone("Europe/Paris")),
                              pytz.utc.localize(component.decoded("dtend").replace(tzinfo=None)).astimezone(
                                  pytz.timezone("Europe/Paris"))])

# Si il y a des occurences aujourd'hui
if len(today) != 0:
    open("ok", "w").write("")

    # date du jour en titre
    # heure début et fin des cours en description
    auj = datetime.strftime(datetime.now(), "%d/%m/%Y")
    desc = "Les cours commencent à " + datetime.strftime(today[0][1], "%H:%M") + " et terminent à " + datetime.strftime(
        today[len(today) - 1][2], "%H:%M")

    message = {
        "content": "",
        "embeds": [
            {
                "title": auj,
                "description": desc,
                "fields": [],
                "author": {
                    "name": school_name,
                    "url": netypareo_url,
                    "icon_url": logo_url
                },
                "footer": {
                    "text": "Netyparéo Notif 1.1"
                }
            }
        ],
        "attachments": []
    }

    # pour chaque evenement ce jour
    for i in today:
        # le sujet du cours est a trouver dans la deuxieme partie d'un string tel que "classe - matiere - prof"
        j = i[0].split("-")

        pause = get_pause(i[1], i[2])

        if len(j) == 3:
            name = j[1]

            val = "Prof: " + j[2] + "\n" + \
                  datetime.strftime(i[1], "%H:%M") + "-" + datetime.strftime(i[2], "%H:%M") + "\n" \
                  + "Pause: " + pause

            message["embeds"][0]["fields"].append({
                "name": name,
                "value": val,
                "inline": True
            })
        else:
            name = i[0]
            val = datetime.strftime(i[1], "%H:%M") + "-" + datetime.strftime(i[2], "%H:%M") + "\n" \
                  + "Pause: " + pause

            message["embeds"][0]["fields"].append({
                "name": name,
                "value": val,
                "inline": True
            })

    r = requests.post(webhook_url, json=message)
    r.raise_for_status()
else:
    try:
        os.remove("ok")
    except:
        exit()
