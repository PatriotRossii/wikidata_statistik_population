import typer
import json
import csv


def main(filename: str, output_filename: str):
	output_file = open(output_filename, "w")
	population_information = {}

	with open(filename) as csvfile:
		csv_reader = csv.reader(csvfile, delimiter=";")
		next(csv_reader, None) # skip the headers
		for row in csv_reader:
			gemeinde_code, census_code, population = row
			if gemeinde_code not in population_information:
				population_information[gemeinde_code] = {}
			population_information[gemeinde_code][census_code] = int(population)
		output_file.write(json.dumps(population_information))


if __name__ == "__main__":
	typer.run(main)