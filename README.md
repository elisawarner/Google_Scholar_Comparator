# Final_Project: Google Scholar Comparator
*Regenerated from my previous git folder called "Final_Project"*

**What it does:**
* Accepts multiple Google Scholar search terms separated by a comma (up to 5 is suitable for the graphic). Returns a graphic of boxplots to describe the distribution of number of citations of top search results for Google Scholar in that field. Also returns 

### Program Requirements:
* **You must use a Mac computer** (*Backend was changed to tkAgg. Should work in Windows too but not tested*)
* Please use Chrome Browser, because cache-clearing function doesn't work in Safari
* You must use from MWireless or public wifi to avoid overloading requests. Should your requests be overloaded on a public IP address, limit your search terms until requests are met. Once those search terms are cached, you can try comparing the multiple terms again.
* If you were met with an error, reduce your search terms. You were likely overloaded requests (see previous bullet)
* Program requires python 3.6 installed with packages located in *requirements.txt*
* Make sure to update *config.py* with the appropriate database name and database user

## How to run:
1. Download packages in *requirements.txt*
2. Update *config.py* with database name and database user
3. Type: *python SI507_F17_finalproject.py runserver* into the command prompt to start local server
3. Type: *localhost:5000* in your Chrome browser
4. Type multiple Google Search terms into the search bar separated by a comma

# Screenshots of software

![Image of Google Scholar Comparator](https://github.com/elisawarner/Final_Project/blob/master/Google_Comparator_1.png)
*Google Scholar Comparator Landing Page. Type search terms here separated by a comma*

![Image of Google Scholar Comparator](https://github.com/elisawarner/Final_Project/blob/master/Google_Comparator_3.png)
*Google Scholar Comparator's Citation Results Visual*

![Image of Google Scholar Comparator](https://github.com/elisawarner/Final_Project/blob/master/Google_Comparator-2.png)
*List of top Google Scholar Search Results Table*
