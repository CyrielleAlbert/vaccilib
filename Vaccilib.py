# coding: utf-8

# Imports


import requests
import datetime
from datetime import date, datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import json
import schedule 
import time

global bot_token, bot, user_id

# Config
with open('tokens.txt', 'r') as tokens_file:
    tokens = json.load(tokens_file)
bot_token = tokens["Bot Token"]
user_id = tokens["chat_id"]


doctolib_lookup = [
    {
        "url": "https://www.doctolib.fr/centre-de-sante/angers/centre-de-vaccination-covid-19-angers-parc-des-expositions",
        "agenda_ids": "450938-449907-450944-450408-449908-450940-450936-450946-450932-450929-450934-449903-449906-449905-449904-450943-450931-449911-471925-450945-449901-449902-449910-450937-449918",
        "practice_ids": "180770",
        "visit_motive_ids": "2746356",
    },
    {
        "url": "https://www.doctolib.fr/centre-de-sante/brissac-loire-aubance/centre-de-vaccination-covid-19-brissac?highlight%5Bspeciality_ids%5D%5B%5D=5494",
        "agenda_ids": "470281-470945-459910",
        "practice_ids": "180768",
        "visit_motive_ids": "2747187",
    },
    {
        "url": "https://www.doctolib.fr/etablissement-de-prevention/seiches-sur-le-loir/centre-de-vaccination-covid-de-seiches-sur-le-loir",
        "agenda_ids": "456241-451902-451924-451925-451945-456239",
        "practice_ids": "181252",
        "visit_motive_ids": "2855716",
    },
    {
        "url": "https://www.doctolib.fr/centre-de-sante/bauge-en-anjou/centre-de-vaccination-bauge-en-anjou?highlight%5Bspeciality_ids%5D%5B%5D=5494",
        "agenda_ids": "409221-409825-451691-449701-437132-470994-430937-409826-423946-439977-443920",
        "practice_ids": "163993",
        "visit_motive_ids": "2543815",
    },
    {
        "url": "https://www.doctolib.fr/centre-de-vaccinations-internationales/le-pin-en-mauges/centre-vaccination-covid-19des-mauges-49?highlight%5Bspeciality_ids%5D%5B%5D=5494",
        "agenda_ids": "469708-459698-472333-466771-475000-410859",
        "practice_ids": "164698",
        "visit_motive_ids": "2548662",
    },
    {
        "url": " https://www.doctolib.fr/centre-depistage-covid/chateau-gontier-sur-mayenne/chateaugontier-centre-de-vaccination?highlight%5Bspeciality_ids%5D%5B%5D=5494",
        "agenda_ids": "466751-407272-426239-446955-425187-426241-443550-412153-425189-410872-412152",
        "practice_ids": "162998",
        "visit_motive_ids": "2534276",
    }
]

console_prints = True


# Doctolib API


def check_availabilities(dc_item):
    headers = {
        "authority": "www.doctolib.fr",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        "accept": "application/json",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "content-type": "application/json; charset=utf-8",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.doctolib.fr/centre-de-sante/",
        "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    params = (
        ("start_date", date.today().strftime("%Y-%m-%d")),
        ("visit_motive_ids", dc_item["visit_motive_ids"]),
        ("agenda_ids", dc_item["agenda_ids"]),
        ("insurance_sector", "public"),
        ("practice_ids", dc_item["practice_ids"]),
        ("destroy_temporary", "true"),
        ("limit", "4"),
    )
    response = requests.get(
        "https://www.doctolib.fr/availabilities.json", headers=headers, params=params
    )
    slots = response.json()
    return slots


# Telegram alert


def send_alert(content, e_title, e_desc, e_url):
    message = "content: "+ content+" \ntitle: "+e_title+"\ndescription: "+ e_desc+"\nurl: "+e_url+""
    bot.sendMessage(chat_id=user_id, text=message)
    print("Message sent")


# Main run

def loop_get_slots():
    print("Im here")
    end_date = date.today() + timedelta(days=2)

    for dc_item in doctolib_lookup:
        slots = check_availabilities(dc_item)
        if slots["total"] > 0:
            if console_prints:
                print("Slots available")
            for dates in slots["availabilities"]:
                if len(dates["slots"]) > 0:
                    slot_times = [
                        str(
                            datetime.strptime(
                                stime["start_date"].split("+")[0], "%Y-%m-%dT%H:%M:%S.%f"
                            ).time()
                        )
                        for stime in dates["slots"]
                    ]
                    if end_date> datetime.strptime(dates["date"],'%Y-%m-%d').date():
                        send_alert(
                            content="Dose de vaccin disponible",
                            e_title=str(dates["date"]),
                            e_desc="\n".join(slot_times),
                            e_url=dc_item["url"],
                        )
        else:
            if console_prints:
                print("No slots")


def main():
    global bot
    bot = Bot(token=bot_token)
    schedule.every(15).seconds.do(loop_get_slots)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
