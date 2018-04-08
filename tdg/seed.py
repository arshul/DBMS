# -*- coding: utf-8 -*-
from flask_script import Command
from tdg.constants.constants import *
from bs4 import BeautifulSoup
from tdg.model.model import Route, Location
import requests
import time
import re
from selenium import webdriver
from tdg.constants.constants import URL


class SeedData(Command):
    def run(self):
        self.add_data()

    def add_data(self):
        for url in URL:
            data = []
            sub_type_enum = {
                "ritz": "hatchback",
                "etios": "sedan",
                "innova": "suv"
            }
            soup = BeautifulSoup(requests.get(url).content, 'lxml')
            route = soup.find('h1', class_='trip-route').text.split(" to ")
            src = Location.query.filter_by(name=route[0].lower().strip()).first()
            if not src:
                src = Location(name=route[0].lower().strip())
                src.save()
            dest = Location.query.filter_by(name=route[1][:-10].lower().strip()).first()
            if not dest:
                dest = Location(name=route[1][:-10].lower().strip())
                dest.save()
            taxes = soup.find_all("div", class_='col-lg-4 col-sm-4 taxi_category res_design_diff')
            for taxi in taxes:
                fare = taxi.find('span', class_='taxiRates ').text
                fare = re.findall('\d+', fare)[0]
                name = taxi.find('span', class_='bold').text.split("/")[0]
                sub_type = sub_type_enum[str(name).lower().strip()]
                data.append(
                    {"name": name.strip(), "fare": fare, "source": route[0].lower().strip(),
                     "destination": route[1][:-10].lower().strip(),
                     "sub_type": sub_type, "transport_type": 2})
                obj = Route(price=int(fare),
                            source_id=src.id,
                            destination_id=dest.id,
                            cab_category=sub_type)
                Route.merge(obj)