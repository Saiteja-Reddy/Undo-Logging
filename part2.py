import sys
import re
import ast

def process_transactions(transactions):
	start = re.compile("START ([a-zA-Z].*)")
	commit = re.compile("COMMIT ([a-zA-Z].*)")
	startckpt = re.compile("START CKPT \((.*)\)")

	processed = []
	temp_startckpt_vars = []
	for ts in transactions:
		if "START CKPT" in ts:
			try:
				startckpt_vars = startckpt.match(ts).groups()[0].strip().split(",")
				startckpt_vars = list(map(str.strip, startckpt_vars))
				# print("START CKPT", startckpt_vars)
				now = dict()
				now['type'] = "SCKPT"
				now['active'] = startckpt_vars
				temp_startckpt_vars = startckpt_vars
				processed.append(now)
			except:
				print("Error: Processing ", ts)
				exit()	
		elif "END CKPT" in ts:
				# print("END CKPT")
				now = dict()
				now['type'] = "ECKPT"
				now['wasactive'] = temp_startckpt_vars	
				processed.append(now)		
		elif "START" in ts:
			try:
				startvars = start.match(ts).groups()[0].strip().split(",")
				# print("START", startvars)
				assert(len(startvars) == 1)
				now = dict()
				now['type'] = "START"
				now['ts'] = startvars[0]
				processed.append(now)			
			except:
				print("Error: Processing ", ts)
				exit()
		elif "COMMIT" in ts:
			try:
				commitvars = commit.match(ts).groups()[0].strip().split(",")
				# print("COMMIT", commitvars)
				assert(len(commitvars) == 1)
				now = dict()
				now['type'] = "COMMIT"
				now['ts'] = commitvars[0]			
				processed.append(now)			
			except:
				print("Error: Processing ", ts)
				exit()			
		else:
			# regular transaction assumed
			try:
				ts = ts.strip().split(",")
				ts = list(map(str.strip, ts))
				assert(len(ts) == 3)
				# print(ts)
				now = dict()
				now['type'] = "N"
				now['ts'] = ts[0]			
				now['var'] = ts[1]
				now['oldval'] = ts[2]
				processed.append(now)			
			except:
				print("Error: Processing ", ts)
				exit()	
	return processed			

def extract_info(filename):
	f = open(filename, 'r')

	trans = -1
	create = 0
	tname = ""
	init = f.readline().strip()

	init = init.split(" ")
	initials = dict()
	flag = 0
	curid = ""
	for i in init:
		if i.isidentifier():
			if flag == 1:
				print("Error: Check initial")
				exit()
			flag = 1
			curid = i
		else:
			flag = 0
			if curid == "":
				print("Error: Check initial id")
				exit()			
			if i.isdigit():
				initials[curid] = int(i);
	# print(initials)	
	steps = []
	for no,line in enumerate(f):
		if line == "\n":
			continue
		line = line.strip().lstrip("<").rstrip(">")
		steps.append(line)
	f.close()
	steps = process_transactions(steps)
	return initials, steps

data, transactions = extract_info(sys.argv[1])

# print(data)
# print(transactions)
# print()

def revert(var, preval):
	global data
	if var not in data.keys():
		print("Error: Log has reference to not present var ", var)
		exit()
	data[var] = preval

def print_data():
	for a, var in enumerate(sorted(data.keys())):
		print(var, " ", data[var], sep="", end = "")
		if a != len(sorted(data.keys())) - 1:
			print(" ", end="")		
	print()	
####
transactions = transactions[::-1]
endckpt_seen = 0
startckpt_seen = 0
wait_to_finish = set()

commited = set()
for ts in transactions:
	# print(ts)
	if ts['type'] == "ECKPT":
		endckpt_seen = 1
	elif ts['type'] == "SCKPT":
		startckpt_seen = 1
		if endckpt_seen is 1:
			# print("Stopped")
			break
		wait_to_finish.update(ts['active'])
		for tsname in commited:
			wait_to_finish.discard(tsname)
		# print("Wait until start of ", wait_to_finish)
	elif ts['type'] == "START":
		if startckpt_seen is 1:
			wait_to_finish.discard(ts['ts'])
			if len(wait_to_finish) is 0:
				break
	elif ts['type'] == "COMMIT":
		commited.add(ts['ts'])
		# print(commited)
	elif ts['type'] == "N":
		if ts['ts'] in commited:
			# print("Skipped", ts)
			continue
		revert(ts['var'], int(ts['oldval']))
		# print_data()
	# elif ts['']

	# print()

print_data()

