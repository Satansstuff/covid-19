#!/usr/bin/env python
# encoding: utf-8
import requests
import urwid
from bs4 import BeautifulSoup
import json
from decimal import Decimal
def refresh(_loop, _data):
    main_loop.draw_screen()
    quote_box.base_widget.set_text(get_update())
    main_loop.set_alarm_in(10, refresh)

def refresh():
    delim = ','
    page = requests.get('https://www.worldometers.info/coronavirus/').text
    soup = BeautifulSoup(page, 'html.parser')
    infected = soup.select(".content-inner > div:nth-child(7) > div:nth-child(2) > span:nth-child(1)")[0].string.extract().replace(',', ' ', 1)
    dead = soup.select(".content-inner > div:nth-child(9) > div:nth-child(2) > span:nth-child(1)")[0].string.extract().replace(',', ' ', 1)
    recovered = soup.select(".content-inner > div:nth-child(10) > div:nth-child(2) > span:nth-child(1)")[0].string.extract().replace(',', ' ', 1)
    data = soup.select("#main_table_countries_today > tbody:nth-child(2)")[0]
    statistics = {}
    country_labels = []
    country_labels.append("Global")
    g = [infected, "N/A", dead, "N/A", recovered, "N/A", "N/A", "N/A", "N/A"]
    statistics["Global"] = g
    for a in data:
        if(len(a) == 1):
            continue
        countries = a.find_all("td")
        
        name = "N/A" if countries[0].string is None else countries[0].string.extract()
        total = "N/A" if countries[1].string is None else countries[1].string.extract()
        new = "N/A" if countries[2].string is None else countries[2].string.extract()
        total_death = "N/A" if countries[3].string is None else countries[3].string.extract()
        new_death = "N/A" if countries[4].string is None else countries[4].string
        total_recvered = "N/A" if countries[5].string is None else countries[5].string.extract()
        active = "N/A" if countries[6].string is None else countries[6].string
        serious = "N/A" if countries[7].string is None else countries[7].string
        totcm = "N/A" if countries[8].string is None else countries[8].string
        totdm = "N/A" if countries[9].string is None else countries[9].string
        c = [total, new, total_death, new_death, total_recvered, active, serious, totcm, totdm]
        statistics[name] = c
        country_labels.append(name)
           
    return country_labels, statistics


choices = refresh()

def menu(title = "boi"):
    body = [urwid.Text(title), urwid.Divider()]
    for c in choices[0]:
        button = urwid.Button(c)
        urwid.connect_signal(button, 'click', item_chosen, c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def item_chosen(button, choice):
    req = requests.get("https://restcountries.eu/rest/v2/name/" + choice)
    pop = json.loads(req.text)
    infected = "\nTotal infected: " + choices[1][choice][0] + " | " + choices[1][choice][1] + "\n"
    dead = "Total deaths: " + choices[1][choice][2] + " | " + choices[1][choice][3] + "\n"
    recovered = "Total recovered: " + choices[1][choice][4] + "\n"
    active = "Active cases: " + choices[1][choice][5] + "\n"
    serious = "Serious cases: " + choices[1][choice][6] + "\n"
    if(req.status_code != 404):
        dead_int = int(choices[1][choice][2].replace(",", "", 1))
        death_percentage = round(Decimal(dead_int / pop[0]["population"]),8)
        death_str = "Death percentage: " + str(death_percentage) + "%" + "\n"
    else:
        death_str = "Death percentage: " + "Not available" + "\n"
    pstring = infected + dead + death_str + recovered + active + serious
    response = urwid.Text([pstring])
    done = urwid.Button(u'Ok')
    urwid.connect_signal(done, 'click', exit_program)
    main.original_widget = urwid.Filler(urwid.Pile([response,
        urwid.AttrMap(done, None, focus_map='reversed')]))

def exit_program(button):
    raise urwid.ExitMainLoop()

main = urwid.Padding(menu(u'Pick a country'), left=2, right=2)
top = urwid.Overlay(main, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
    align='center', width=('relative', 60),
    valign='middle', height=('relative', 60),
    min_width=20, min_height=9)
urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()

