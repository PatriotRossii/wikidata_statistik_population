from wikibaseintegrator import wbi_login, WikibaseIntegrator
from wikibaseintegrator.datatypes import String, Quantity, Time, Item, MonolingualText
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator.wbi_helpers import execute_sparql_query
from wikibaseintegrator.wbi_enums import WikibaseDatePrecision

from datetime import datetime
import typer
import json
import re


wbi_config['USER_AGENT'] = 'EoanErmineBot/1.0 (https://www.wikidata.org/wiki/User:EoanErmineBot)'


# See OGD_f0743_VZ_HIS_GEM_1_C-H88-0.csv at
# https://data.statistik.gv.at/web/meta.jsp?dataset=OGD_f0743_VZ_HIS_GEM_1
census_codes = {
	"H88-1": datetime(year=1869, month=12, day=31), "H88-2": datetime(year=1880, month=12, day=31),
	"H88-3": datetime(year=1890, month=12, day=31), "H88-4": datetime(year=1890, month=12, day=31),
	"H88-5": datetime(year=1900, month=12, day=31), "H88-6": datetime(year=1923, month=3, day=7),
	"H88-7": datetime(year=1934, month=3, day=22), "H88-8": datetime(year=1939, month=5, day=17),
	"H88-9": datetime(year=1951, month=6, day=1), "H88-10": datetime(year=1961, month=3, day=21),
	"H88-11": datetime(year=1971, month=5, day=12), "H88-12": datetime(year=1981, month=5, day=12),
	"H88-13": datetime(year=1991, month=5, day=15), "H88-14": datetime(year=2001, month=5, day=15),
	"H88-15": datetime(year=2011, month=10, day=31)
}


def get_query(gemeinde_code: str):
    query = """SELECT ?item WHERE { ?item wdt:P964 "{}" }"""
    return query.replace("{}", gemeinde_code)


def main(population_info_filename: str, gemeinde_info_filename: str,
	     bot_username: str = typer.Option(...), bot_password: str = typer.Option(...)):
	population_data = json.load(open(population_info_filename))
	gemeinde_data = json.load(open(gemeinde_info_filename))

	login_instance = wbi_login.Login(
		user=bot_username, password=bot_password
	)
	wbi = WikibaseIntegrator(login=login_instance)

	for code, population_information in population_data.items():
		if code not in gemeinde_data:
			continue
		gemeinde_code = gemeinde_data[code]["code"]
		
		entity_id = re.search(
			r"(Q\d+)",
			str(execute_sparql_query(get_query(gemeinde_code)))
		)
		if not entity_id:
			continue
		entity_id = entity_id.group(1)

		item = wbi.item.get(entity_id=entity_id)
		claims = []
		for census_code, count in population_information.items():
			date = census_codes[census_code]
			claims.append(Quantity(prop_nr="P1082", amount=int(count), qualifiers=[
				Time(prop_nr="P585", time=date.strftime("+%Y-%m-%dT00:00:00Z"), precision=WikibaseDatePrecision.DAY),
				Item(prop_nr="P459", value="Q39825")
			], references=[
				[
					String(prop_nr="P854", value="https://data.statistik.gv.at/web/meta.jsp?dataset=OGD_f0743_VZ_HIS_GEM_1"),
					MonolingualText(prop_nr="P1476", text="Population census data since 1869 for communes", language="en"),
					Time(prop_nr="P813", time=datetime(year=2023, month=1, day=24), precision=WikibaseDatePrecision.DAY),
					Item(prop_nr="P123", value="Q358870")
				]
			]))
		item.claims.add(claims)
		item.write()


if __name__ == "__main__":
	typer.run(main)