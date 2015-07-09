#!/usr/bin/env python
"""

	This simple script scans website pai.pt for a particular category and prints 
	the list of emails found.
	The emails found are printed one per line in the output (along with status messages)
	and also writen to a csv file called emails.csv with <email,category> structure
	It uses BeautifulSoup to parse html responses given by the server.

	Usage:
		python main.py <category> [<first_page>]
		e.g.: 
		python main.py http://www.pai.pt/ourivesarias-joalharias/
		python main.py http://www.pai.pt/ourivesarias-joalharias/ 10

	Copyright: 
		Tiago Almeida 
		tiago.b.almeida@gmail.com 
		http://stackoverflow.com/users/1590025/jumpifzero

	License: MIT

"""
import re
import time
import csv
import sys
from urllib import urlopen
import bs4

__author__ 		= "Tiago Almeida"
__copyright__ 	= "Copyright 2015, Tiago Almeida"
__credits__ 	= ["Everyone who contributed to python and BeautifulSoup"]
__license__ 	= "MIT"
__version__ 	= "1.0.0"
__maintainer__ 	= "Tiago Almeida"
__email__ 		= "tiago.b.almeida@gmail.com"
__status__ 		= "Prototype"


def extract_emails_from_page(soup):
	"""
		Returns a list of emails found in page. Using a regex to scan
	"""
	email_pattern = re.compile('([\w\-\.+]+@(\w[\w\-]+\.)+[\w\-]+)')
	try:
		page_content = str(soup)
	except:
		print('Error parsing page. Skipped\n')
		return []
	matches = email_pattern.findall(page_content)
	if matches:
		return [ match[0] for match in matches ]
	return []


	
def write_emails_to_set(emails_lst, s):
	for email in emails_lst:
		s.add(email)
	

	
def write_emails_to_file(result_emails, category):
	"""
	Generates emails.csv file with email,category
	"""
	f = open('emails.csv', 'wb')
	csvWriter = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	for email in result_emails:
		csvWriter.writerow([email, category])	
	f.close()



def print_emails(emails_list):
	for email in emails_list:
		print(email)



def extract_emails_from_category(initial_url, first_page=int(1)):
	"""
		Returns a list of emails contained in all pages of a category

		initial_url: string like http://www.pai.pt/ourivesarias-joalharias/
			and it should point to the top level page of a category
		first_page: optional. Allows skipping the first <first_page> pages

	"""
	result_emails = set() #we will return this
	#last page regex
	lp_regex = re.compile('[0-9]+/;')
	#Open URL
	soup = bs4.BeautifulSoup(urlopen(initial_url), "html5lib")
	#extract the link to the last page. It is inside div.paging-bottom > ul > li with text ">>"
	navigation = soup.find_all("div",id="paging-bottom")
	if not navigation:
		print("This page is weird. It has no navigation. Aborting\n")
		return result_emails

	txt_elem = navigation[0].ul.find_all(text=">>")[0]
	#link to last page
	link = txt_elem.parent
	#Get its url.. smthg like /ourivesarias-joalharias/134/;jsessionid=67E1932531B84B3E77AAF47A29B263CE
	url = link['href']
	#Pick the number of the last page
	match = lp_regex.search(url)
	if match:
		last_page = match.group()[0:-2]
		last_page_i = int(last_page)
	else:
		print("This category has no navigation to the last page\n")
		last_page_i = first_page
		
	#Sanity Check
	if last_page_i < first_page:
		last_page_i = first_page
		
	print("Working on category %s" % initial_url)
	#Now that we have the last page. Time to iterate on each one and get the emails
	for page in xrange( first_page, last_page_i ):
		page_url = initial_url + str(page) + '/' #This is fragile
		print("Scanning page %d of %d (%s)." % (page, last_page_i, page_url))
		try:
			emails = extract_emails_from_page(bs4.BeautifulSoup( unicode(urlopen(page_url).read(),'utf-8','ignore'), "html5lib"))
			write_emails_to_set(emails, result_emails)
			time.sleep(5)
		except IOError:
			print("Coult not fetch url %s. Skipped\n" % page_url)
	return result_emails
		

	
def main():
	if (len(sys.argv) > 1):
		initial_url = sys.argv[1]
		try:
			first_page = int(sys.argv[2])
		except IndexError:
			first_page = int(1)
		result_emails = extract_emails_from_category(initial_url, first_page)
		write_emails_to_file(result_emails, initial_url)
		print_emails(result_emails)
	else:
		print("usage: %s <category url> [<skip_first_pages>]" % sys.argv[0])
		


if __name__ == '__main__':
	main()
