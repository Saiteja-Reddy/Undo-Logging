import sys

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
			elif create == 1:
				transactions[tname].append(line.strip())
	f.close()
	return transactions, init

transactions, initials = extract_info(sys.argv[1])


print(initials)
print(transactions)