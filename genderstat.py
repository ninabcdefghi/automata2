import requests
from bs4 import BeautifulSoup
import re
import gender_guesser.detector as gender
import pandas as pd
import time
import csv

homepage = "https://www.tagesspiegel.de"
d = gender.Detector()


def get_autorzeilen_from(ressort):
	website_text = BeautifulSoup(requests.get(ressort).text, "html.parser").body # das jede stunde neu
	spans = website_text.find_all("span", {"class" : "hcf-editor"})
	all_autorzeilen = [span.get_text() for span in spans]
	all_autorzeilen = "".join(map(str, all_autorzeilen))
	return all_autorzeilen


def get_firstnames_from(ressort):
	autorzeilen = get_autorzeilen_from(ressort)
	return ["".join(x) for x in re.findall("Von\s+(\w+)|,\s+(\w+)*", autorzeilen)]


def get_genders_in(ressort):

	firstnames = get_firstnames_from(ressort)
	genders = []
    
	for i in firstnames:
		if i == "Anima" or i == "Ning":
			genders.append("female")
			continue
		if i == "Gerrit" or i == "Sascha":
			genders.append("male")
			continue
		if i == "Tagesspiegel":
			continue
            
		gender = d.get_gender(i)
		if gender == "unknown":
			continue
            
		genders.append(gender)

	aufmacher_gender = d.get_gender(firstnames[0])
	if aufmacher_gender == "male":
		aufmacher = 0
	else:
		aufmacher = 1

	return genders, aufmacher


def get_gender_count_and_aufmacher(ressort):
	unix_time = time.time()
	genders, aufmacher = get_genders_in(ressort)

	male = genders.count("male")
	female = genders.count("female")

	return [unix_time, male, female, aufmacher]


def main():
	result = get_gender_count_and_aufmacher(homepage)

	with open("homepage.csv", "a", newline="") as f:
		writer = csv.writer(f)
		writer.writerow(result)


if __name__ == "__main__":
	main() 