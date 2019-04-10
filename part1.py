import sys
import re

def extract_info(filename):
	f = open(filename, 'r')
	transactions = dict()

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

	for no,line in enumerate(f):
		if line == "\n":
			trans += 1
			create = 0
		if line != "\n":
			if trans >= 0 and create == 0:
				create = 1
				tname = line.split(" ")[0]
				# print(tname, "Created")
				transactions[tname] = []
				# transactions[tname] = [line.strip()]
			elif create == 1:
				transactions[tname].append(line.strip())
	f.close()
	return transactions, init

transactions, initials = extract_info(sys.argv[1])
print(initials)
print(transactions)
step = int(sys.argv[2])
print(step)
print("\n")
#####

disk = initials
membuf = dict()
localmem = dict()

iterators = [-1 for _ in range(0, len(transactions))]
curpos = -1

def run_input(var):
	global disk, membuf
	if var not in disk.keys():
		print("Error: INPUT var not found in disk")
		exit()
	print("copied" , var, "to membuf from disk")
	membuf[var] = disk[var]

def run_read(var, locvar):
	global localmem, membuf
	if var not in membuf:
		run_input(var) #copy to membuf
	print("copied" , var, "from membuf to locmem")
	localmem[var] = membuf[var]	

def run_write(var, locvar):
	global localmem, membuf
	if var not in localmem:
		print("Error: WRITE var not found in localmem")
		exit()		
	if var not in membuf:
		run_input(var) # copy to membuf
	print("copied" , var, "from locmem to membuf")
	membuf[var] = localmem[var]		

def run_output(var):
	global disk, membuf
	if var not in membuf:
		print("Error: OUTPUT var not found in membuf")
		exit()	
	if var not in disk.keys():
		print("Error: OUTPUT var not found in disk")
		exit()
	print("copied" , var, "from membuf to disk")
	disk[var] = membuf[var]


# read = re.compile("READ\((.*)\)")
# write = re.compile("WRITE\((.*)\)")
# inp = re.compile("INPUT\((.*)\)")
# out = re.compile("OUTPUT\((.*)\)")
# oper = re.compile("(.*):=(.*)")

# for ts in transactions["T1"]:
# 	# print(ts)
# 	if "READ" in ts:
# 		print("READ",ts)
# 		try:
# 			readvars = read.match(ts).groups()[0].strip().split(",")
# 			print(readvars)
# 		except:
# 			print("Error: Processing ", ts)
# 			exit()
# 	elif "WRITE" in ts:
# 		print("WRITE",ts)
# 		try:
# 			writevars = write.match(ts).groups()[0].strip().split(",")
# 			print(writevars)
# 		except:
# 			print("Error: Processing ", ts)
# 			exit()		
# 	elif "INPUT" in ts:
# 		print("INPUT",ts)
# 		try:
# 			invars = inp.match(ts).groups()[0].strip()
# 			print(invars)
# 		except:
# 			print("Error: Processing ", ts)
# 			exit()		
# 	elif "OUTPUT" in ts:
# 		print("OUTPUT",ts)
# 		try:
# 			outvars = out.match(ts).groups()[0].strip()
# 			print(outvars)
# 		except:
# 			print("Error: Processing ", ts)
# 			exit()				
# 	elif ":=" in ts:
# 		print("OP",ts)	
# 		try:
# 			opvars = list(map(str.strip, oper.match(ts).groups()))
# 			print(opvars)
# 			assert(len(opvars) is 2)
# 		except:
# 			print("Error: Processing ", ts)
# 			exit()				
# 	else:
# 		print("Error: Processing ", ts)
# 		exit()

def getnext_pos():
	global transactions, iterators, curpos
	curpos = (curpos + 1) % len(iterators)
	if iterators[curpos] == "done":
		return getnext_pos()
	else:
		return curpos

def get_ts_curpos():
	global transactions, iterators, curpos, step
	begin = iterators[curpos]
	if begin >= len(transactions[list(transactions.keys())[curpos]]):
		iterators[curpos] =  "done"
		return []
	end = begin + step
	try:
		iterators[curpos] = end
		if end == len(transactions[list(transactions.keys())[curpos]]):
			iterators[curpos] =  "done"
		return transactions[list(transactions.keys())[curpos]][begin:end]
	except:
		iterators[curpos] = "done"
		return transactions[list(transactions.keys())[curpos]][begin:]

def getnext_tset():
	global transactions, iterators, curpos
	if iterators.count("done") == len(iterators):
		return []
	else:
		curpos = getnext_pos()
		if iterators[curpos] == -1:
			print("<START", list(transactions.keys())[curpos] , ">")
			iterators[curpos] = 0
		return get_ts_curpos()




ts_set =  getnext_tset()
while len(ts_set) is not 0:
	print(ts_set)
	ts_set = getnext_tset()








