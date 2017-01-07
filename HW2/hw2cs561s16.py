import argparse, copy

## Define classes and functions
def askStc(line):	# Write Ask into file
	if isinstance(line, list):
		temp = ""
		for i in range(len(line[1])):
			if i != 0:
				temp += ", "
			if isVariable(line[1][i]):
				temp += "_"
			else:
				temp += line[1][i]
		f.write("Ask: " + line[0] + "(" + temp + ")")
	else:
		f.write("Ask: " + line)
	f.write("\n")

def trueStc(line):	# Write true into file
	if isinstance(line, list):
		temp = ""
		for i in range(len(line[1])):
			if i != 0:
				temp += ", "
			temp += line[1][i]
		f.write("True: " + line[0] + "(" + temp + ")")
	else:
		f.write("True: " + line)
	f.write("\n")

def falseStc(line):	# Write false into file
	if isinstance(line, list):
		temp = ""
		for i in range(len(line[1])):
			if i != 0:
				temp += ", "
			temp += line[1][i]
		f.write("False: " + line[0] + "(" + temp + ")")
	else:
		f.write("False: " + line)
	f.write("\n")

def checkStc(stc):	# Check if sentence is already in the KB's atomic sentence
	for j in range(len(atomicStc)):
		if stc == atomicStc[j]:
			return True
	return False

def argsIntoList(x):	# Return arguments into list form
	result = []
	lparenPos = x.find("(")
	if lparenPos != -1:
		temp = x[x.find("(") + 1 : len(x) - 1]
	else:
		temp = x
	while 1:
		pos = temp.find(", ")
		if pos == -1:
			result.append(temp)
			return result
		else:
			result.append(temp[0:pos])
			temp = temp[pos + 2 : ]

def parseAtomicStc(stc):	# Parse Atomic Sentence. If it has predicate, return [predicate, arguments]. If not, return sentence
	lparen = stc.find("(")
	if(lparen != -1):
		return [stc[0 : lparen], argsIntoList(stc[lparen + 1 : len(stc) - 1])]
	return stc

def parseStc(stc):	# Parse complex sentence into atomic sentence without implication
	result = []
	symAnd = stc.find(" && ")
	while (symAnd != -1):	# Parse complex sentences into atomic sentences
		result.append(stc[0 : symAnd])
		stc = stc[symAnd + 4 : ]
		symAnd = stc.find(" && ")
	result.append(stc)
	for i in range(len(result)):	# Parse atomic sentence into list form
		result[i] = parseAtomicStc(result[i])
	return result

def FOL_BC_ASK(query):	# Start function for asking query. Every goals need to be satisfied
	goals = parseStc(query)
	theta = []
	for i in range(len(goals)):
		thetaTemp = FOL_BC_OR(goals[i], theta)
		if thetaTemp == FAIL:
			return False
		else:
			theta += thetaTemp
	return True

def FOL_BC_OR(goal, theta):	# This OR function only need to satisfy one of many possible candidates. Here, theta is useless, since every theta would be empty.
	goalTemp = subArgs([goal], theta)[0]
	isAsked = False
	if checkStc(goalTemp):	# When query is already in KB's atomic sentence,
		askStc(goalTemp)
		trueStc(goalTemp)
		return theta
	inAtomicStc = False
	for j in range(len(atomicStc)):	# If there is possible argument substitution in atomic sentence, substitute it
		if goal[0] == atomicStc[j][0]:
			thetaTemp = unify(goalTemp[0] + "(" + ", ".join(goalTemp[1]) + ")", atomicStc[j][0] + "(" + ", ".join(atomicStc[j][1]) + ")", [])
			if thetaTemp != FAIL:
				inAtomicStc = True
				theta += thetaTemp
	if inAtomicStc:
		askStc(goalTemp)
		goalTemp = subArgs([goal], theta)[0]
		trueStc(goalTemp)
		return theta
	# If there is no possible argument substitution in atomic sentence,
	lhs, rhs, implNum = fetchRulesForGoal(goal)
	global gFuncLevel
	for j in range(len(rhs)):	# goal can have many implications in KB
		gFuncLevel += 1
		varRe = str(implNum[j]) + str(gFuncLevel)	# Rename variables by adding varRe
		lhs[j] = varArgsRename(lhs[j], varRe)
		rhs[j] = varArgsRename(rhs[j], varRe)
		goalTemp = subArgs([goal], theta)[0]
		askStc(goalTemp)
		isAsked = True
		lstcs = parseStc(lhs[j])
		thetaTemp = unify(rhs[j], goalTemp[0] + "(" + ", ".join(goalTemp[1]) + ")", [])
		theta += thetaTemp
		temp = FOL_BC_AND(lstcs, theta)	# lhs and rhs is in original sentence form
		if temp != FAIL:
			theta = temp
			trueStc(subArgs([goal], theta)[0])
			isAsked = False
			return theta
		else:
			theta = removeTheta(theta, thetaTemp)
	if not isAsked:
		askStc(goalTemp)
	falseStc(goalTemp)
	return FAIL

def FOL_BC_AND(goals, theta):	# This AND function need to satisfy every goals generated
	global isRetry
	global gFuncLevel
	funcLevel = gFuncLevel
	for i in range(len(goals)):
		
		if not isRetry:
			temp = FOL_BC_OR(goals[i], theta)
		else:
			temp = FOL_BC_OR_RETRY(goals[i], theta)
		if temp == FAIL:
			gFuncLevel = funcLevel
			while 1:
				theta = retryOthTheta(goals[i][1], theta)	# goals[i][1] is goals[i]'s variable list
				if theta == FAIL:
					return FAIL
				else:
					isRetry = True
					temp = FOL_BC_AND(goals, theta)
					if temp != FAIL:
						isRetry = False
						return temp	# If there is successive temp, it can be used as theta
		else:
			theta = temp
	return theta

def FOL_BC_OR_RETRY(goal, theta):	# This function is for retry of FOL_BC_OR
	global retryVar
	isTarget = False
	goalTemp = subArgsRetry([goal], theta, retryVar)[0]
	for i in range(len(goal[1])):
		if goalTemp[1][i] == retryVar:
			isTarget = True
			break
	if not isTarget:
		return theta
	if isInAtomicStc(subArgs([goal], theta)[0]):
		askStc(goalTemp)
		goalTemp = subArgs([goal], theta)[0]
		trueStc(goalTemp)
		return theta
	# If there is no possible argument substitution in atomic sentence,
	lhs, rhs, implNum = fetchRulesForGoal(goal)
	global gFuncLevel
	for j in range(len(rhs)):	# goal can have many implications in KB
		gFuncLevel += 1
		varRe = str(implNum[j]) + str(gFuncLevel)
		lhs[j] = varArgsRename(lhs[j], varRe)	# Name variables again
		rhs[j] = varArgsRename(rhs[j], varRe)
		# goalTemp = subArgsRetry([goal], theta, retryVar)[0]
		lstcs = parseStc(lhs[j])
		temp = FOL_BC_AND(lstcs, theta)	# lhs and rhs is in original sentence form
		if temp != FAIL:
			trueStc(subArgs([goal], theta)[0])
			return theta
	# When there is no answer,
	askStc(subArgs([goal], theta)[0])
	falseStc(subArgs([goal], theta)[0])
	return FAIL

def subArgsRetry(stcs, theta, retryVar):	# Substitute variables into constants in theta
	result = copy.deepcopy(stcs)
	for i in range(len(result)):
		for j in range(len(result[i][1])):	# ith stc's argument list
			for k in range(len(theta)):
				if result[i][1][j] == theta[k][0] and retryVar != theta[k][0]:
					result[i][1][j] = theta[k][1]
	return result

def isRetryAtomicStc(goal, retryVar):	# Check if retrying goal is in atomic sentence without retryVar
	for j in range(len(atomicStc)):
		result = True
		if goal[0] == atomicStc[j][0] and len(goal[1]) == len(atomicStc[j][1]):	# When predicate name and arguments number are same,
			for i in range(len(goal[1])):
				if goal[1][i] != retryVar and goal[1][i] != atomicStc[j][1][i]:
					result = False
					break
			if result:
				return True
	return False

def isInAtomicStc(goal):
	for j in range(len(atomicStc)):
		result = True
		if goal[0] == atomicStc[j][0] and len(goal[1]) == len(atomicStc[j][1]):	# When predicate name and arguments number are same,
			
			for i in range(len(goal[1])):
				if goal[1][i] != atomicStc[j][1][i]:
					result = False
					break
			if result:
				return True
	return False

def unify(x, y, theta):	# Synchronize all variables in sentence x, y
	if theta == FAIL:
		return FAIL
	elif x == y:
		return theta
	elif isVariable(x):
		return unifyVar(x, y, theta)
	elif isVariable(y):
		return unifyVar(y, x, theta)
	elif isCompound(x) and isCompound(y):	# F(x, y) form
		return unify(argsIntoList(x), argsIntoList(y), unify(findOp(x), findOp(y), theta))
	elif isinstance(x, list) and isinstance(y, list):	# when x and y are list,
		if len(x) == 1 and len(y) == 1:
			return unify(x[0], y[0], theta)
		elif len(x) != len(y):
			return FAIL
		else:
			return unify(x[1:], y[1:], unify(x[0], y[0], theta))	# unify(x.rest, y.rest, unify(x.first, y.first, theta))
	else:
		return FAIL

def unifyVar(var, x, theta):
	for i in range(len(theta)):
		if var == theta[i][0]:
			return unify(theta[i][1], x, theta)
		elif x == theta[i][0]:
			return unify(var, theta[i][1], theta)
		elif var == theta[i][0] and x == theta[i][1]:
			return FAIL
	theta.append([var, x])
	return theta

def fetchRulesForGoal(goal):	# Fetch implications whose conclusion is goal. lhs and rhs are one string each.
	lhs = []
	rhs = []
	implNum = []
	for i in range(len(impl)):
		temp = parseAtomicStc(impl[i][1])	# rhs atomic sentence of implication
		if temp[0] == goal[0]:	# If predicate is same,
			lhs.append(impl[i][0])	# Add implication's premise
			rhs.append(impl[i][1])	# Add implication's conclusion
			implNum.append(i)
	return [lhs, rhs, implNum]

def isVariable(x):
	if isinstance(x, list):
		return False
	elif x.find("(") != -1:
		return False
	elif x == x.lower():
		return True
	else:
		return False

def isCompound(x):
	if isinstance(x, list):
		return False
	elif x.find("(") == -1:
		return False
	else:
		return True

def findOp(x):
	return x[0 : x.find("(")]

def subArgs(stcs, theta):	# Substitute variables into constants in theta
	result = copy.deepcopy(stcs)
	for i in range(len(result)):
		for j in range(len(result[i][1])):	# ith stc's argument list
			for k in range(len(theta)):
				if result[i][1][j] == theta[k][0]:
					result[i][1][j] = theta[k][1]
	return result

def thetaInGoalArgs(goal, theta):	# Return only theta in goal's argument
	result = []
	for i in range(len(theta)):
		inGoal = False
		for j in range(len(goal[1])):	# goal[1] is list of arguments
			if theta[i][0] == goal[1][j]:	# theta[i][0] is variable in theta (ex) x / Pine
				inGoal = True
				result.append(theta[i])
				break
	return result

def varArgsRename(stc, varRe):	# Adjust goal's variable arguments into goal specific arguments (ex) x -> x1
	stcs = parseStc(stc)	# Parse string form into list form
	for i in range(len(stcs)):	# For each sentence
		for j in range(len(stcs[i][1])):	# For each sentence's arguments
			arg = stcs[i][1][j]
			if isVariable(arg):
				stcs[i][1][j] = arg + varRe
	result = ""
	for i in range(len(stcs)):	# Parse list form into string form
		if i != 0:
			result += " && "
		result += stcs[i][0] + "("
		for j in range(len(stcs[i][1])):
			if j != 0:
				result += ", "
			result += stcs[i][1][j]
		result += ")"
	return result

def removeTheta(theta, thetaTemp):
	result = []
	for i in range(len(theta)):
		inThetaTemp = False
		for j in range(len(thetaTemp)):
			if theta[i] == thetaTemp[j]:
				inThetaTemp = True
				break
		if not inThetaTemp:
			result.append(theta[i])
	return result

def retryOthTheta(varList, theta):
	thetaLen = len(theta)
	for i in range(thetaLen - 1):
		if theta[thetaLen - i - 1][0] == theta[thetaLen - i - 2][0]:
			for j in range(len(varList)):
				if varList[j] == theta[thetaLen - i - 1][0]:
					global retryVar
					retryVar = varList[j]
					index = thetaLen - i - 1
					while theta[index][0] == theta[index - 1][0]:
						index -= 1
					del theta[index]
					return theta
	return FAIL


## Global Constants
FAIL = "fail"
isRetry = False
retryVar = ""
gFuncLevel = 0

## Parse command line argument
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputfile", help="input file route")
args = parser.parse_args()

## Open file and check existence
try:
	f = open(args.inputfile, 'r')
except IOError as e:
	print "I/O error({0}): {1}".format(e.errno, e.strerror)
	exit()

## Read file
query = f.readline().replace("\n", "")
numStc = int(f.readline())
stcs = []
for i in range(numStc):
	stcs.append(f.readline().replace("\n", ""))
f.close()

## Preprocess
atomicStc = []	# atomic sentence
impl = []	# implication
for stc in stcs:
	imply = stc.find(" => ")
	if imply == -1:
		lparen = stc.find("(")
		atomicStc.append([stc[0 : lparen], argsIntoList(stc[lparen + 1 : len(stc) - 1])])	# In each item, atomicStc[i][0] is predicate and atomicStc[i][1] is argument list
	else:
		impl.append([stc[0 : imply], stc[imply + 4 : ]])	# impl[i][0] is premise and impl[i][1] is conclusion

## Execution
# outFileName = args.inputfile[:-3] + "output.txt"
outFileName = "output.txt"
f = open(outFileName, 'w')

if FOL_BC_ASK(query):
	f.write("True")
else:
	f.write("False")
f.close()