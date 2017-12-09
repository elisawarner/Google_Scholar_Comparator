import requests
import csv
import re
import flask
from bs4 import BeautifulSoup


# makes request for google scholar search term
# add pages later
def search_google_scholar(search_term):
	file_name = "google_" + search_term
	try:
		fhnd = open(file_name + '.html',"r")
		search_data = fhnd.read()
		print("Found in cache")
	except:
		print("Sent a new request")
		baseurl = "https://scholar.google.com/scholar"
		params_d = {}
		params_d['q'] = search_term
		search_data = requests.get(baseurl, params=params_d).text
		f = open(file_name + '.html',"w")
		f.write(search_data)
		f.close()
	
	soup = BeautifulSoup(search_data, 'html.parser')
	#return soup.prettify()

	# returns list of paper htmls for processing by class Paper
	return soup.find_all('div',{'class':'gs_r gs_or gs_scl'})

class Paper(object):
	def __init__(self, data):
		self.title = data.find('h3',{'class':'gs_rt'}).text.strip(' .')
		self.link = data.find('h3',{'class':'gs_rt'}).find('a')['href']
		try:
			results_list = data.find_all('div',{'class':'gs_fl'})
			for x in results_list:
				try:
					self.no_citations = re.search('(?<=Cited by )....', x.text).group(0).strip(' R')
				except:
					pass
		except:
			self.no_citations = 0

		author_line_pre = data.find('div',{'class':'gs_a'}).text
		author_line = re.split('\s\-\s', author_line_pre)
		self.authors = [x.strip() for x in author_line[0].split(',')]
		self.year = author_line[1].split(',')[-1].strip()

	def package(self):
		return [self.title, self.authors, self.year, self.no_citations, self.link]

	def __str__(self):
		return "{0} by {1}".format(self.title, ' '.join(self.authors))

	# FILL THIS OUT
	def __repr__(self):
		pass

	# FILL THIS OUT
	def __contains__(self):
		pass

def write_to_csv(name, input_list):
	fhnd = open(name + '.csv','w')

	fhnd.write('Title,Authors,Year,Citations,Link\n')
	outfile = csv.writer(fhnd, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

	for row in input_list:
		outfile.writerow(row)

	fhnd.close()


def wrapper_call(search_term):
	outlist = []
	cite_list = []
	for entry in search_google_scholar(search_term):
		a = Paper(entry)
		print(a)
		outlist.append(a.package())
		cite_list.append(a.no_citations)

	# take average number of citations
	
	write_to_csv(search_term, outlist)


#search_google_scholar('a')

wrapper_call('apples')