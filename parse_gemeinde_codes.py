import typer
import json
import csv
import re


# See https://www.wikidata.org/wiki/Property:P964
def validate_code(code: str) -> bool:
	return re.match(r"\d{5}", code)


def main(filename: str, output_filename: str):
	output_file = open(output_filename, "w")
	gemeinde_information = {}

	with open(filename) as csvfile:
		csv_reader = csv.reader(csvfile, delimiter=";")
		for row in csv_reader:
			code = re.search(r"<(\d+)>", row[1])
			if not code:
				continue
			code = code.group(1)
			if not validate_code(code):
				continue
			name = row[1].replace(f" <{code}>", "")
			gemeinde_information[row[0]] = {
				"code": code,
				"name": name
			}
		output_file.write(json.dumps(gemeinde_information))


if __name__ == "__main__":
	typer.run(main)