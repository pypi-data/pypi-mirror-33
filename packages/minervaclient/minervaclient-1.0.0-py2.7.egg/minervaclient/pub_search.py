# pub_search.py: Search for available places in requested courses (via the Display Dynamic Schedule interface)
# This file is from Minervac, a command-line client for Minerva
# <http://npaun.ca/projects/minervac>
# (C) Copyright 2016-2017 Nicholas Paun
# (C) Copyright 2018-2019 Ryan B Au

import requests,urllib,StringIO,csv,sys
from minerva_common import *

def build_request(term,codes):
	req = [
	('sel_crse',''),
	('sel_title',''),
	('begin_hh','0'),
	('begin_mi','0'),
	('begin_ap','a'),
	('end_hh','0'),
	('end_mi','0'),
	('end_ap','a'),
	('sel_dunt_code',''),
	('sel_dunt_unit',''),
	('sel_from_cred',''),
	('sel_to_cred',''),
	('sel_coll',''),
	('call_value_in','UNSECURED'),
	('display_mode_in','LIST'),
	('search_mode_in',''),
	('term_in',term),
	('sel_subj','dummy'),
	('sel_day','dummy'),
	('sel_ptrm','dummy'),
	('sel_ptrm','%'),
	('sel_camp','dummy'),
	('sel_schd','dummy'),
	('sel_schd','%'),
	('sel_sess','dummy'),
	('sel_instr','dummy'),
	('sel_instr','%'),
	('sel_attr','dummy'),
	('sel_attr','%'),
	('crn','dummy'),
	('rsts','dummy'),
	('sel_levl','dummy'),
	('sel_levl','%'),
	('sel_insm','dummy'),
	]

	for code in codes:
		req.append(('sel_subj',code.split("-")[0]))
	
	return urllib.urlencode(req)

def search(term,course_codes):
	request = build_request(term,course_codes)
	sys.stderr.write("> bwckgens.csv\n")
	result = requests.post("https://horizon.mcgill.ca/rm-PBAN1/bwckgens.csv",request)
	return parse_results(result.text)

def quick_search(term, course_codes, course_type=""):
	"""term is in the form of 201809 where 2018 is the year (2016, 2017...), and 09 is for Fall (01 for Winter, 05 for Summer)
	course_codes is a list and elements may come in the form of:
		general course code, like COMP-202, to retrieve all different sections of it (eg. COMP-202-001, COMP-202-002...)
			AND/OR
		a specific course code with its section number, can be given (eg. COMP-202-001)
	valid course_type values include Lecture, Tutorial, or any other similar type"""
	#TODO: waitlist, availability, tutorials/lectures, 

	# get the course data from Minerva. includes all of the courses that share the same subject(s) as the course_codes parameter
	courses_obj = search(term,course_codes)
	
	# find all of the full course codes that exist in the search query
	final_codes = []
	full_codes = []
	for course_code in course_codes:
		counter = 1
		if(course_code in courses_obj):
			full_codes.append(course_code)
			continue
		else:
			full_code = course_code[:8] + str(counter).join("-000".rsplit('0'*len(str(counter)),1))
		
		while (full_code in courses_obj) and (counter <= 999):
			full_codes.append(full_code)
			counter += 1 
			full_code = course_code[:8] + str(counter).join("-000".rsplit('0'*len(str(counter)),1))

	# only keep course codes of a specified type as defined by course_type, or leave it an empty string to get all
	for full_code in full_codes:
		aType = courses_obj[full_code]['type']
		if (course_type in aType):
			final_codes.append(full_code)

	# a tuple of the relevant course codes (eg. COMP-200-001 CCOM-206-018 ...) and the courses object retrieved from Minerva
	# the courses object contains all of the courses with the same subject (eg. COMP, ECSE, POLI) in a dictionary 
	# with keys in the form of course codes
	return (final_codes, courses_obj)

def print_search(term,course_codes, cType, avail=False, verbose=False, Debug=False):
	# print out all of the courses and their variations really nicely for the command line interface
	full_codes, courses_obj = quick_search(term,course_codes, cType)
	if(Debug):
		print full_codes + "\n"
	full_codes.sort()

	for full_code in full_codes:
		course = courses_obj[full_code]
		if(avail and not (verbose or Debug)):
			print str(course['_code']),
			print " CRN: %-6s" % (str(course['crn'])),
			print " Seats Remaining: %-8s" % ( str(course['wait']['rem']) +"/" + str(course['wait']['cap']) ),
			print " Waitlist: %-8s" % ( str(course['wl_rem']) + "/" +str(course['wl_cap']) )
		else:
			print beautify_course_info(course, (verbose or Debug))

def beautify_course_info(e, Debug=False):
	# accept a specific course's information in the form of a dictionary and formats it to look nice for the command line interface. 
	# set Debug to True to see the all of the original keys and values paired together concatenated to the end of the original outpute
	result = [
		e['title'],
		e['type'] +" Instructor: "+ e['instructor'] +" | Credits: "+str( e['credits'] ) ,
		str(e['_code']) + " CRN: "+ str(e['crn']) + " Seats Remaining: " + str(e['wait']['rem']) +"/" + str(e['wait']['cap']) + " Waitlist: " + str(e['wl_rem']) + "/" +str(e['wl_cap']),
		e['location'] + " " + e['days'] + " " + e['time'] + " Period: " + e['date'],
		""		
	]
	result0 = ""
	for key,value in e.items():
		result0 += key + "=>" + str(value) + " | "
	# return "\n".join(result)
	return "\n".join(result) + ((result0) if Debug else "")


def parse_results(text):
	# converts the HTTP request data from Minerva into a logical format in a python dictionary

	stream = StringIO.StringIO(text.encode("ascii","ignore"))
	field_names = ['crn','subject','course','section','type','credits','title','days','time','cap','wl_cap','wl_act','wl_rem','instructor','date','location','status']
	file = csv.DictReader(stream,field_names)

	records = {}
	first = True
	for row in file:
		if row['subject'] is None or row['subject'] == 'Subject':
			continue

		if row['cap'] == '':
			continue

		if row['wl_rem'] == '':
			row['wl_rem'] = -1000

		row['_code'] = "-".join([row['subject'],row['course'],row['section']])
		row['select'] = MinervaState.only_waitlist_known

		row['reg'] = {}
		row['reg']['cap'] = int(row['cap'])
		
		row['wait'] = {}
		row['wait']['cap'] = int(row['wl_cap'])
		row['wait']['act'] = int(row['wl_act'])
		row['wait']['rem'] = int(row['wl_rem'])

		if row['wait']['rem'] > 0:
			row['_state'] = MinervaState.wait
		else:
			row['_state'] = MinervaState.unknown

		records[row['_code']] = row

	
	return records
