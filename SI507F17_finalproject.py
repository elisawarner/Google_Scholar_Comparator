import requests
import csv
import re
import flask
import json
import numpy as np
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

# database stuff
import psycopg2
import psycopg2.extras
import sys
import csv
from psycopg2 import sql
from config import *

from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask, render_template, request
from flask_script import Manager


# nytimes.py

################ CACHING & DATA RETRIEVAL ###################
# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
CACHE_FNAME = 'cache_file.json'
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = False
# MAKE SURE TO DROP TABLE EVEN WITHOUT DEBUG, BEFORE YOU RERUN IT


# -----------------------------------------------------------------------------
# Load cache file
# -----------------------------------------------------------------------------
try:
    with open(CACHE_FNAME, 'r') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICTION = json.loads(cache_json)
except:
    CACHE_DICTION = {}


# CITE: Anand Doshi, nytimes.py
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

# CITE: Jackie Cohen, Runestone Virtual Textbook
def params_unique_combination(baseurl, params_d, private_keys=["api_key"]):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_d[k]))
    return baseurl + "_".join(res)

# CITE: Anand Doshi, nytimes.py
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

# CITE: Anand Doshi, nytimes.py
def set_in_cache(url, params_d, html, expire_in_days):
    """Add URL and html to the cache dictionary, and save the whole dictionary to a file as json"""
    cache_key = params_unique_combination(url, params_d)
    
    CACHE_DICTION[cache_key] = {
        'html': html,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT),
        'expire_in_days': expire_in_days
    }

    with open(CACHE_FNAME, 'w') as cache_file:
        cache_json = json.dumps(CACHE_DICTION)
        cache_file.write(cache_json)

# CITE: Anand Doshi, nytimes.py
def get_html_from_url(url, params_d, expire_in_days=7): #Added params_d
    """Check in cache, if not found, load html, save in cache and then return that html"""
    # check in cache
    html = get_from_cache(url, params_d)
 #   print(html)
    if html != None:
        if DEBUG:
            print('Loading from cache: {0}'.format(url))
    else:
 #       if DEBUG:
        print('Fetching a fresh copy: {0}'.format(url))
 #       print()

        # fetch fresh
        response = requests.get(url, params=params_d)

        # Deleted line about encoding because it was messing up my shit

        html = response.text

        # cache it
        set_in_cache(url, params_d, html, expire_in_days)

    return html

def search_google_scholar(search_term, params_d = {}):
	baseurl = "https://scholar.google.com/scholar"
	params_d['q'] = search_term
	
	google_results = get_html_from_url(baseurl, params_d, expire_in_days=1)
	google_soup = BeautifulSoup(google_results, 'html.parser')

	#return soup.prettify()

	# returns list of paper htmls for processing by class Paper
	return google_soup.find_all('div',{'class':'gs_r gs_or gs_scl'})


######################## END CACHING #############################################

########################### DATABASE FILES #######################################
############ CITE: SI507_project6.py, Jackie Cohen, Anand Doshi ##################

# CITE: Jackie Cohen, project-6
def get_connection_and_cursor():
    try:
        if db_password != "":
            db_connection = psycopg2.connect("dbname='{0}' user='{1}' password='{2}'".format(db_name, db_user, db_password))
            print("Success connecting to database")
        else:
            db_connection = psycopg2.connect("dbname='{0}' user='{1}'".format(db_name, db_user))
    except:
        print("Unable to connect to the database. Check server and credentials.")
        sys.exit(1) # Stop running program if there's no db connection.

    db_cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    return db_connection, db_cursor

conn, cur = get_connection_and_cursor()


# Write code / functions to create tables with the columns you want and all database setup here.
# CITE: inspired by project6
def setup_database():
    # Invovles DDL commands
    # DDL --> Data Definition Language
    # CREATE, DROP, ALTER, RENAME, TRUNCATE

    conn, cur = get_connection_and_cursor()

    if DEBUG == True:
	    # starts new tables every time you run
    	cur.execute("""DROP TABLE IF EXISTS "Publications" """)
    	cur.execute("""DROP TABLE IF EXISTS "Subjects" """)

    #### CREATE SITES TABLE ###
    cur.execute("""CREATE TABLE IF NOT EXISTS "Subjects"(
        "ID" SERIAL PRIMARY KEY,
        "Name" VARCHAR(500) UNIQUE NOT NULL
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS "Publications"(
        "ID" SERIAL PRIMARY KEY,
        "Title" VARCHAR(500) UNIQUE NOT NULL,
        "Authors" TEXT,
        "Year" INTEGER,
        "Citations" INTEGER,
        "Journal" VARCHAR(255),
        "Link" VARCHAR(500),
        "Topic_ID" INTEGER, FOREIGN KEY ("Topic_ID") REFERENCES "Subjects"("ID")
    )""")

    # Save changes
    conn.commit()

    print('Setup database complete')

# inserts a column into the table
# CITE: Anand Doshi, section-week-11
def insert(conn, cur, table, data_dict):
    column_names = data_dict.keys()
    # print(column_names)

    # generate insert into query string
    query = sql.SQL('INSERT INTO "{0}"({1}) VALUES({2}) ON CONFLICT DO NOTHING').format(
        sql.SQL(table),
        sql.SQL(', ').join(map(sql.Identifier, column_names)),
        sql.SQL(', ').join(map(sql.Placeholder, column_names))
    )
    query_string = query.as_string(conn)
    cur.execute(query_string, data_dict)


########################## CLASS AND CSV FILES ###################################

class Paper(object):
    def __init__(self, data, search_term):
        self.search_term = search_term

        self.title = data.find('h3',{'class':'gs_rt'}).text.replace('[HTML]','').replace('[DOC]','').replace('[RTF]','').replace('[PDF]','').replace('[CITATION][C]','').replace('[BOOK][B]','').strip(' .').encode('utf-8').decode('ascii','ignore')
        try:
            self.link = data.find('h3',{'class':'gs_rt'}).find('a')['href']
        except:
            self.link = None

        results_list = data.find_all('div',{'class':'gs_fl'})
        self.no_citations = 0
        for x in results_list:
            try:
                self.no_citations = int(re.search('(?<=Cited by )....', x.text).group(0).strip(' R'))
            except:
                pass

        author_line_pre = data.find('div',{'class':'gs_a'}).text
        if author_line_pre.startswith('US Patent'):
            author_line = re.split('\d\,\s', author_line_pre)
            # print(author_line)
            self.authors = [author_line[0]]
            self.year = author_line[1].split('-')[0].strip()
            self.journal = author_line[1].split('-')[1].strip()
        else:
            author_line = re.split('\s\-\s', author_line_pre)
            self.authors = [x.strip(' ').encode('utf-8').decode('ascii','ignore') for x in author_line[0].split(',')]
            self.year = author_line[1].split(',')[-1].strip()

            try:
                self.journal = author_line[1].split(',')[0].strip().encode('utf-8').decode('ascii','ignore')
            except:
                self.journal = None
            if self.journal.isdigit():
                self.journal = None

    def package(self):
        return [self.title, self.authors, self.year, self.no_citations, self.journal, self.link, self.search_term]

    def package_html(self):
        return [self.title, self.authors, self.year, self.journal, self.no_citations]

    def __str__(self):
        return "{0} by {1}".format(self.title, ', '.join(self.authors))

    def __repr__(self):
        return self.no_citations

    def __contains__(self, value):
        return value in self.title

def write_to_csv(name, input_list):
	fhnd = open('./csv_files/' + name + '.csv','w')

	fhnd.write('Title,Authors,Year,Citations,Journal,Link,Topic\n')
	outfile = csv.writer(fhnd, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

	for row in input_list:
		outfile.writerow(row)

	fhnd.close()

##########################################################################


def wrapper_call(search_term, ID_num):
    outlist = []
    html_list = []
    cite_list = []
    journal_list = []
    params_d = {}
    maxPage = 50

    # setting up Database stuff
    conn, cur = get_connection_and_cursor()

    # add values
    cur.execute("""INSERT INTO "Subjects"("ID", "Name") VALUES(%s, %s) on conflict do nothing""", (ID_num, search_term))

    if DEBUG:
        print("%s added to Subject database" % (search_term))

    ### This part gets the information from google, then mines it for info

#    try:
    for num in range(0,maxPage,10):
        params_d['start'] = num
        if DEBUG:
            print("Page %s" % (num))

        for entry in search_google_scholar(search_term, params_d):

            a = Paper(entry, search_term)

            outlist.append(a.package())
            html_list.append(a.package_html())

            cur.execute("""SELECT "ID" FROM "Publications" """)
            id_test = len(cur.fetchall())

            insert(conn, cur, "Publications", {"ID": id_test+1, "Title": a.title, "Authors": a.authors, "Year": a.year, "Citations": a.no_citations, "Journal": a.journal, "Link": a.link, "Topic_ID": ID_num})

            if DEBUG:
            	print("Added %s to database" % (a.title))

            cite_list.append(a.no_citations)

#    except:
#        print("Please try another search term. We couldn't find enough Google Results")
    conn.commit()

	# Create a csv file
    write_to_csv(search_term, outlist)
    return (cite_list, html_list[:5])


def plotdata(input_dict):
	# CITE: Code taken from http://blog.bharatbhole.com/creating-boxplots-with-matplotlib/
	key_names = list(input_dict.keys())
	plot_list = []

	for key in key_names:
		plot_list.append(np.asarray(input_dict[key][0]))

	# Create a figure instance
	fig = plt.figure(1, figsize = (9, 6))
	plt.title('Number of Citations Per Search Term')

	# Create an axes instance
	ax = fig.add_subplot(111)

	# Create the boxplot
	bp = ax.boxplot(plot_list, patch_artist=True)
	ax.set_xticklabels(key_names)

	## change outline color, fill color and linewidth of the boxes
	for box in bp['boxes']:
		# change outline color
		box.set( color='#7570b3', linewidth=2)
		# change fill color
		box.set( facecolor = '#1b9e77' )

	## change color and linewidth of the whiskers
	for whisker in bp['whiskers']:
		whisker.set(color='#7570b3', linewidth=2)

	## change color and linewidth of the caps
	for cap in bp['caps']:
		cap.set(color='#7570b3', linewidth=2)

	## change color and linewidth of the medians
	for median in bp['medians']:
		median.set(color='#b2df8a', linewidth=2)

	## change the style of fliers and their fill
	for flier in bp['fliers']:
		flier.set(marker='o', color='#e7298a', alpha=0.5)

	fig.savefig('./static/fig1.png', bbox_inches = 'tight')
	plt.clf()


###################################################### INTERFACE ######################################################

def interface(fields):
	# setting up Database stuff
	conn, cur = get_connection_and_cursor()
	# set up the database
	setup_database()

	search_dict = {}

	#response = input("List up to five fields to compare, separated by commas\n(e.g. Memristors, ebola virus, reduced order models, hepatocellular carcinoma, HIV):\n")
	#fields = [x.strip() for x in response.split(',')]
	
	print(fields)

	count = 0
	for fieldName in fields:
		count += 1
		search_dict[fieldName] = wrapper_call(fieldName, count)

	plotdata(search_dict)

	return(search_dict)

######################################################

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

manager = Manager(app)

@app.route('/')
def my_form():
	return render_template('interface.html')


@app.route('/', methods=['GET', 'POST'])
def my_form_post():
    text = request.form['text']
    fields = [x.strip() for x in text.upper().split(',')]
    return render_template('results.html', fields = fields, return_dict = interface(fields))
 

if __name__ == '__main__':
    manager.run() # Runs the flask server in a special way that makes it nice to debug

