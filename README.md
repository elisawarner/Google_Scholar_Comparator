# Final_Project: Google Scholar Comparator
*Regenerated from my previous git folder called "Final_Project"*

**What it does/What to expect:**
* Accepts multiple Google Scholar search terms separated by a comma (up to 5 is suitable for the graphic). Returns a graphic of boxplots to describe the distribution of number of citations for top 50 search results for Google Scholar in that field. Also returns a table for each topic of the top 5 Google Scholar publications for each topic, including the title, authors, year, journal, link to the paper, and number of citations
* Adds every unique entry into a database of publications. Two databases are created:
  1. A table of search terms
  2. A table of publications, with a foreign key connected to search terms
* Returns a csv-format of results for each search term (*e.g. if you typed* Memristors, ebola virus, reduced order models, hepatocellular carcinoma, HIV *you will see five files: MEMRISTORS.csv, EBOLA VIRUS.csv, REDUCED ORDER MODELS.csv, HEPATOCELLULAR CARCINOMA.csv, HIV.csv, with 50 results each*)

### Program Requirements:
* **You must use a Mac computer** (*Backend was changed to tkAgg. Should work in Windows too but not tested*)
* Please use Chrome Browser, because cache-clearing function doesn't work in Safari
* You must use from MWireless or public wifi to avoid overloading requests. Should your requests be overloaded on a public IP address, limit your search terms until requests are met. Once those search terms are cached, you can try comparing the multiple terms again.
* If you were met with an error, reduce your search terms. You were likely overloaded requests (see previous bullet)
* Program requires python 3.6 installed with packages located in *requirements.txt*
* Make sure to update *config.py* with the appropriate database name and database user

## How to run:
1. Download packages in *requirements.txt*
2. Update *config.py* with database name and database user (*note, database name can be anything, but must be a database already created. Store the database name to variable* db_name *and the user to* db_user)
3. Type: *python SI507F17_finalproject.py runserver* into the command prompt to start local server
3. Type: *localhost:5000* in your Chrome browser
4. Type multiple Google Search terms into the search bar separated by a comma

# Screenshots of software: What to Expect

![Image of Google Scholar Comparator](https://github.com/elisawarner/Final_Project/blob/master/Google_Comparator_1.png)
*Google Scholar Comparator Landing Page. Type search terms here separated by a comma*

![Image of Google Scholar Comparator](https://github.com/elisawarner/Final_Project/blob/master/Google_Comparator_3.png)
*Google Scholar Comparator's Citation Results Visual*

![Image of Google Scholar Comparator](https://github.com/elisawarner/Final_Project/blob/master/Google_Comparator-2.png)
*List of top Google Scholar Search Results Table*

## Technical Details: What Happens When the Code Runs
1. The browser cache for the static folder is deleted. The user visits localhost:5000 and sees a landing page with a search bar. This is run by Flask, which borrows a template called interface.html
2. Search terms are separated and stripped. The Google Scholar Search Results for each term are first searched for in the cache file, then request from Google Scholar if not in the cache. This data is ultimately cached.
3. The data is parsed to return only Publications and information about them. A Class called **Paper** is used to parse the data, and will also return information set in formats for csv and Flask manipulation
4. All incoming data is inserted into a database (wrapper_call()). The database is first set up with the setup_database(). The insert() function is used to insert the data into the "Publications" table. Information sent to the "Subjects" table is directly handled through the wrapper_call() function.
5. Number of citations for each Publication in each Subject is saved for later
6. A csv file of each search term data is saved as an extra
7. The plotdata() function takes the citation information from each search term and creates one graph with multiple boxplots based on the number of citations for each search term.
8. Information about the top 5 Publications for each search term is sent from Class Paper (method: package_html()) to results.html. The figure (saved in the static folder) is also integrated into the Results page.
9. The User can refresh the page to start again.

## SUMMARY
**Input:** Search terms separated by a comma in landing page search bar
**Output:**
1. CSV files for top 50 Google Scholar results from each search term (Number of CSV files = Number of search terms). CSV files will be contained in a folder called *csv_files*
2. Two Database tables: "Publications" (containing information about Publications), and "Search Terms" (containing all previously entered search terms)
3. An html Results Page including a boxplot graph of the distribution of citations per search term, and the top 5 Google Scholar hits for each search term. The boxplot will be called *fig1.png* and be contained in a folder called *static*

### Acknowledgments and Citations:
* Complex caching system with expiration date courtesy of: Anand Doshi, nytimes.py
* Unique Cache Key Function (params_unique_combination) courtesy of: Jackie Cohen, Runestone text
* matplotlib example courtesy of: http://blog.bharatbhole.com/creating-boxplots-with-matplotlib/
* setup_database() function courtesy of Jackie Cohen, Project-6
* insert() function for database courtesy of Anand Doshi, section-week-11
