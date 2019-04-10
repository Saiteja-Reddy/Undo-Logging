import sys
import re
import ast


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
	return transactions, initials

transactions, initials = extract_info(sys.argv[1])
# print(initials)
# print(transactions)
step = int(sys.argv[2])
# print(step)
# print("\n")
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
	# print("copied" , var, "to membuf from disk")
	membuf[var] = disk[var]

def run_read(var, locvar):
	# print("*")
	global localmem, membuf
	if var not in membuf:
		run_input(var) #copy to membuf
	# print("copied" , var, "from membuf to locmem")
	localmem[locvar] = membuf[var]	
	# print("*")

def run_write(tsname, var, locvar):
	global localmem, membuf
	if locvar not in localmem:
		print("Error: WRITE var not found in localmem")
		exit()		
	if var not in membuf:
		run_input(var) # copy to membuf
	# print("copied" , var, "from locmem to membuf")
	print("<", tsname, ", ", var, ", ", membuf[var], ">", sep="")
	membuf[var] = localmem[locvar]		
	print_mem_buf()
	print_disk_buf()	

def run_output(var):
	global disk, membuf
	if var not in membuf:
		print("Error: OUTPUT var not found in membuf")
		exit()	
	if var not in disk.keys():
		print("Error: OUTPUT var not found in disk")
		exit()
	# print("copied" , var, "from membuf to disk")
	disk[var] = membuf[var]

def print_mem_buf():
	for a, var in enumerate(sorted(membuf.keys())):
		print(var," ", membuf[var], sep="", end = "")
		if a != len(sorted(membuf.keys())) - 1:
			print(" ", end="")
	print()

def print_disk_buf():
	for a, var in enumerate(sorted(disk.keys())):
		print(var, " ", disk[var], sep="", end = "")
		if a != len(sorted(disk.keys())) - 1:
			print(" ", end="")		
	print()

def get_variables(expression):
	code = expression
	st = ast.parse(code)
	out = []
	for node in ast.walk(st):
	    if type(node) is ast.Name:
	        # print(node.id)
	        out.append(node.id)
	return out

def make_safe_dict(expression_vars):
	global localmem
	# print("heere", localmem)
	safe_dict = dict()
	for var in expression_vars:
		if var not in localmem.keys():
			print("Error: Incorrect expression vars", var)
			exit()
		safe_dict[var] = localmem[var]
	return safe_dict


read = re.compile("READ\((.*)\)")
write = re.compile("WRITE\((.*)\)")
inp = re.compile("INPUT\((.*)\)")
out = re.compile("OUTPUT\((.*)\)")
oper = re.compile("(.*):=(.*)")
to_commit_current = 0


def execute_transaction(tsname, ts):
	global read, write, inp, out, oper
	if "READ" in ts:
		# print("READ",ts)
		try:
			readvars = read.match(ts).groups()[0].strip().split(",")
			# print(tsname,readvars)
			run_read(readvars[0], readvars[1])
		except:
			print("Error: Processing ", ts)
			exit()
	elif "WRITE" in ts:
		# print("WRITE",ts)
		try:
			writevars = write.match(ts).groups()[0].strip().split(",")
			# print(tsname,writevars)
			run_write(tsname, writevars[0], writevars[1])
		except:
			print("Error: Processing ", ts)
			exit()		
	elif "INPUT" in ts:
		# print("INPUT",ts)
		try:
			invars = inp.match(ts).groups()[0].strip()
			# print(tsname,invars)
		except:
			print("Error: Processing ", ts)
			exit()		
	elif "OUTPUT" in ts:
		# print("OUTPUT",ts)
		try:
			outvars = out.match(ts).groups()[0].strip()
			# print(tsname,outvars)
			run_output(outvars)
		except:
			print("Error: Processing ", ts)
			exit()				
	elif ":=" in ts:
		# print("OP",ts)	
		try:
			opvars = list(map(str.strip, oper.match(ts).groups()))
			# print(tsname,opvars)
			assert(len(opvars) is 2)
			expression_vars = get_variables(opvars[1])
			# print(expression_vars)
			safe_dict = make_safe_dict(expression_vars)
			# print(safe_dict)
			try:
				localmem[opvars[0]] = eval(opvars[1], {"__builtins__":None}, safe_dict) 
				# print(localmem)
			except:
				print("Error: incorrect localmem op", opvars[0])
				exit()
		except:
			print("Error: Processing ", ts)
			exit()				
	else:
		print("Error: Processing ", ts)
		exit()

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
		if end >= len(transactions[list(transactions.keys())[curpos]]):
			iterators[curpos] =  "done"
		return transactions[list(transactions.keys())[curpos]][begin:end]
	except:
		iterators[curpos] = "done"
		return transactions[list(transactions.keys())[curpos]][begin:]

def getnext_tset():
	global transactions, iterators, curpos, to_commit_current
	if iterators.count("done") == len(iterators):
		return []
	else:
		curpos = getnext_pos()
		if iterators[curpos] == -1:
			print("<START ", list(transactions.keys())[curpos] , ">", sep="")
			print_mem_buf()
			print_disk_buf()
			iterators[curpos] = 0
		to_ret = get_ts_curpos()
		# print(iterators)
		tsname = list(transactions.keys())[curpos]  
		if iterators[curpos] == "done":
			to_commit_current = 1
			# print("COMMIT", tsname)
		return to_ret


ts_set =  getnext_tset()
flag = 1
while len(ts_set) is not 0 and flag:
	# print(ts_set)
	# flag-=1
	tsname = list(transactions.keys())[curpos]
	for ts in ts_set:
		execute_transaction(tsname, ts)
	if to_commit_current == 1:
		print("<COMMIT ", tsname, ">", sep="")
		# run_commit()
		print_mem_buf()
		print_disk_buf()
		to_commit_current = 0
	# print("--")
	## next ts_set
	ts_set = getnext_tset()





