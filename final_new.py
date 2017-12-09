import requests
import csv
import re
import flask
import json
from bs4 import BeautifulSoup
from datetime import datetime

# nytimes.py

################ CACHING ###################
# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
CACHE_FNAME = 'cache_file.json'
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = True


# -----------------------------------------------------------------------------
# Load cache file
# -----------------------------------------------------------------------------
try:
    with open(CACHE_FNAME, 'r') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICTION = json.loads(cache_json)
except:
    CACHE_DICTION = {}


def has_cache_expired(timestamp_str, expire_in_days): # BUG 1
    """Check if cache timestamp is over expire_in_days old"""
    # gives current datetime
    now = datetime.now()

    # datetime.strptime converts a formatted string into datetime object
    cache_timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)

    # subtracting two datetime objects gives you a timedelta object
    delta = now - cache_timestamp
    delta_in_days = delta.days

    # now that we have days as integers, we can just use comparison
    # and decide if cache has expired or not
    if delta_in_days < expire_in_days: #BUG 2
        return False
    else:
        return True

def params_unique_combination(baseurl, params_d, private_keys=["api_key"]):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_d[k]))
    return baseurl + "_".join(res)

# Add params_d
# Find regular caching method and separate key with params_d
def get_from_cache(url, params_d):
    """If URL exists in cache and has not expired, return the html, else return None"""
    cache_key = params_unique_combination(url, params_d)
    if cache_key in CACHE_DICTION:
        url_dict = CACHE_DICTION[cache_key]
 #       html = CACHE_DICTION[url]['html']
        if has_cache_expired(url_dict['timestamp'], url_dict['expire_in_days']):
            # also remove old copy from cache
            del CACHE_DICTION[cache_key]
            html = None
        else:
            html = CACHE_DICTION[cache_key]['html']
    else:
        html = None

    return html


def set_in_cache(url, params_d, html, expire_in_days):
    """Add URL and html to the cache dictionary, and save the whole dictionary to a file as json"""
    cache_key = params_unique_combination(url, params_d)
    print(cache_key)
    CACHE_DICTION[cache_key] = {
        'html': html,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT),
        'expire_in_days': expire_in_days
    }

    with open(CACHE_FNAME, 'w') as cache_file:
        cache_json = json.dumps(CACHE_DICTION)
        cache_file.write(cache_json)


def get_html_from_url(url, params_d, expire_in_days=7): #Added params_d
    """Check in cache, if not found, load html, save in cache and then return that html"""
    # check in cache
    html = get_from_cache(url, params_d)
 #   print(html)
    if html != None:
 #       if DEBUG:
        print('Loading from cache: {0}'.format(url))
        print()
    else:
 #       if DEBUG:
        print('Fetching a fresh copy: {0}'.format(url))
 #       print()

        # fetch fresh
        response = requests.get(url, params=params_d)

        # this prevented encoding artifacts like
        # "Trumpâs Tough Talk" that should have been "Trump's Tough Talk"
        response.encoding = 'utf-8'

        html = response.text

        # cache it
        set_in_cache(url, params_d, html, expire_in_days)

    return html

################################################################

def search_google_scholar(search_term):
	baseurl = "https://scholar.google.com/scholar"
	params_d = {}
	params_d['q'] = search_term
	google_results = get_html_from_url(baseurl, params_d, expire_in_days=1)
	google_soup = BeautifulSoup(google_results, 'html.parser')

	# makes request for google scholar search term
	# add pages later

	#return soup.prettify()

	# returns list of paper htmls for processing by class Paper
	return google_soup.find_all('div',{'class':'gs_r gs_or gs_scl'})

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
		print(a.no_citations)
		outlist.append(a.package())
		cite_list.append(a.no_citations)

	# take average number of citations
	
	write_to_csv(search_term, outlist)


#search_google_scholar('a')

wrapper_call('apples')
wrapper_call('hepatocellular carcinoma')