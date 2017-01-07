import argparse, copy

class OpenFile:	# class for opening file
	def __init__(self):
		self.initialize()
	def initialize(self):
		self.parseCmd()
		self.openFile()
	def parseCmd(self):	# Parse command line argument
		parser = argparse.ArgumentParser()
		parser.add_argument("-i", "--inputfile", help="input file route")
		self.args = parser.parse_args()
	def openFile(self):	# Open file and check existence
		try:
			self.fileObj = open(self.args.inputfile, 'r')
		except IOError as e:
			print "I/O error({0}): {1}".format(e.errno, e.strerror)
			exit()
	def __del__(self):
		self.fileObj.close()

class ParseFile:	# class for parsing file
	def __init__(self, fileObj):
		self.query = []
		self.chanceNode = []
		self.decisionNode = []
		self.utilNode = []
		self.fileObj = fileObj
		self.initialize()
	def initialize(self):
		self.readFile()
	def readFile(self):
		f = self.fileObj
		self.lineParse(f, self.query, "******")	# Parse query
		self.parseQuery()
		self.lineParse(f, self.chanceNode, "******")	# Parse event node
		self.parseChanceNode()
		self.lineParse(f, self.utilNode, "******")	# Parse utility node
		self.parseUtilNode()
	def lineParse(self, f, arr, delimiter):
		line = f.readline().replace("\n", "")
		while (line and line != delimiter):
			arr.append(line)
			line = f.readline().replace("\n", "")
	def parseQuery(self):	# Set query list
		qNode = []
		for item in self.query:
			temp = []
			delimiter = item.find("(")
			temp.append(item[:delimiter])
			temp.append(item[delimiter+1:len(item)-1])
			qNode.append(temp)
		self.query = qNode
	def parseChanceNode(self):	# Set chanceNode list
		cNode = []
		temp = []
		tempProb = []
		cond = 1
		for item in self.chanceNode:
			if cond == 1:
				temp.append(item)
				cond = 0
			elif item != "***":
				if item != "decision":
					self.parseChanceItem(item, tempProb)
				else:
					tempProb.append(item)
			else:	# If item is "***"
				cond = 1
				temp.append(tempProb)
				if tempProb[0] == "decision":
					self.decisionNode.append(temp[0])
				else:
					cNode.append(temp)
				temp = []
				tempProb = []
		temp.append(tempProb)
		cNode.append(temp)
		self.chanceNode = cNode
	def parseChanceItem(self, item, tempProb):
		delimiter = item.find(" ")
		if delimiter != -1:
			tempProb.append( [ item[0:delimiter] , item[delimiter+1:] ] )
		else:
			tempProb.append(item)
	def parseUtilNode(self):	# Set utilNode list
		uNode = []
		temp = []
		tempProb = []
		cond = 1
		if self.utilNode:
			for item in self.utilNode:
				if cond == 1:	# If the line is showing condition nodes,
					delimiter = item.find("|")
					item = item[delimiter+2:]
					temp.append(item)
					cond = 0
				elif item != "***":
					self.parseChanceItem(item, tempProb)
				else:	# If item is "***"
					cond = 1
					temp.append(tempProb)
					uNode.append(temp)
					temp = []
					tempProb = []
			temp.append(tempProb)
			uNode.append(temp)
			self.utilNode = uNode

class OutFile:	# class for writing output file
	def __init__(self, path):
		self.initialize(path)
	def initialize(self, path):
		self.openFile(path)
	def openFile(self, path):
		try:
			self.fileObj = open(path, 'w')
		except IOError as e:
			print "I/O error({0}): {1}".format(e.errno, e.strerror)
			exit()
	def write(self, str):
		self.fileObj.write(str)
	def writeList(self, list):
		for item in list:
			print >> self.fileObj, item
	def __del__(self):
		self.fileObj.close()

class BayesianNetwork:	# Parse bayesian network
	cNodeNameIdx = 0
	cNodeProbIdx = 1
	nodeNameIdx = 0
	nodeValIdx = 1
	def __init__(self, parseFileInstance):
		self.nodes = []	# All nodes including decision nodes and chance nodes
		self.cNodes = []	# BayesianNode instance list. Ordered by network dependency.
		self.f = parseFileInstance
		self.dNodes = self.f.decisionNode
		self.uNodes = self.f.utilNode
		self.initialize()
	def initialize(self):
		self.setNodes(self.f)
		self.bnEquation()
	def setNodes(self, f):	# Set nodes list, cNodes list and utilNodes list
		for item in f.decisionNode:
			self.nodes.append(item)
		for item in f.chanceNode:
			delimiter = item[self.cNodeNameIdx].find(" |")
			if delimiter != -1:	# When there is parent node,
				self.nodes.append(item[self.cNodeNameIdx][:delimiter])
				cNode = BayesianNode(item[self.cNodeNameIdx][:delimiter])
				cNode.addProbabilityWParent(item[self.cNodeProbIdx])
				parentArr = []	# Add parent nodes
				parent = item[self.cNodeNameIdx][delimiter+3:]
				parentDelimiter = parent.find(" ")
				while parentDelimiter != -1:
					parentArr.append(parent[:parentDelimiter])
					parent = parent[parentDelimiter+1:]
					parentDelimiter = parent.find(" ")
				parentArr.append(parent)
				cNode.addParent(parentArr)
			else:	# When there is no parent node,
				self.nodes.append(item[self.cNodeNameIdx])
				cNode = BayesianNode(item[self.cNodeNameIdx])
				cNode.addProbabilityWOParent(item[self.cNodeProbIdx])
			cNode.nodeListAssign()
			self.cNodes.append(cNode)
		utilNodeName = []
		for item in self.uNodes:
			utilNodeStr = item[self.nodeNameIdx]
			delimiter = utilNodeStr.find(" ")
			while delimiter != -1:
				utilNodeName.append(utilNodeStr[:delimiter])
				utilNodeStr = utilNodeStr[delimiter+1:]
				delimiter = utilNodeStr.find(" ")
			if utilNodeStr != "":
				utilNodeName.append(utilNodeStr)
			item[self.nodeNameIdx] = utilNodeName
	def bnEquation(self):	# Make cNodes in order of dependency.
		bnEq = []
		for item in self.cNodes:
			self.addToList(item, bnEq)
		self.cNodes = bnEq
	def addToList(self, target, list):	# Add target(BayesianNode) into list
		parentList = target.parent
		for item in parentList:
			parent = self.findBayesianNode(item, self.cNodes)
			if parent and not self.isNodeInList(parent, list):	# If parent is in cNodes but not in the bnEq list,
				self.addToList(parent, list)
		if not self.isNodeInList(target, list):
			list.append(target)
	def findBayesianNode(self, str, list):	# Return BayesianNode whose node name is str. Otherwise, return False.
		for item in list:
			if str == item.node:
				return item
		return False
	def isNodeInList(self, BayesianNode, list):	# Check BayesianNode is in the BayesianNode list
		for item in list:
			if BayesianNode.node == item.node:
				return True
		return False
	def printCNodes(self):
		for item in self.cNodes:
			print item.node

class BayesianNode:	# class for bayesian chance node
	probValIdx = 0
	probAssignIdx = 1
	def __init__(self, node):
		self.node = node
		self.parent = []
		self.probability = []
		self.nodeList = []
	def addParent(self, node):
		self.parent = self.parent + node
	def addProbabilityWParent(self, probability):
		for item in probability:
			self.probability = self.probability + [ [ item[self.probValIdx], '+ '+item[self.probAssignIdx] ] ]
			self.probability = self.probability + [ [ str(1 - float(item[self.probValIdx])), '- '+item[self.probAssignIdx] ] ]
	def addProbabilityWOParent(self, probability):
		for item in probability:
			self.probability = self.probability + [ [ item, '+' ] ]
			self.probability = self.probability + [ [ str(1 - float(item)), '-' ] ]
	def nodeListAssign(self):	# All nodes including parent and itself
		self.nodeList = [self.node] + self.parent

class Factor:	# class for Pointwise-Product of factors
	nodeNameIdx = 0
	nodeValIdx = 1
	probIdx = 0
	probAssignIdx = 1
	firstElem = 0
	resolution = 0.01
	def __init__(self):
		self.variable = []	# queryNode + hiddenNode which are in cNode
		self.probVarList = []	# factor's probability variable list
		self.probability = []	# factor's probability list accroding to variables
	def initialize(self, cNode, queryNode, evidenceNode, hiddenNode):
		self.setVariable(cNode, queryNode, hiddenNode)
		self.setProbability(cNode, evidenceNode)
	def setVariable(self, cNode, queryNode, hiddenNode):	# Set variable list
		queryList = []
		for item in queryNode:
			queryList.append(item[self.nodeNameIdx])
		queryVarNodes = queryList + hiddenNode	# nodes for parsing except evidenceNode
		for item in queryVarNodes:
			if cNode.node == item:
				self.variable.append(item)
				break
		for item in cNode.parent:
			for item2 in queryVarNodes:
				if item2 == item:
					self.variable.append(item)
					break
	def setProbability(self, cNode, evidenceNode):	# Set probability variable list and probability list
		probVarListTemp = []
		for item in cNode.nodeList:	# Change variable names into assignment
			isVar = True
			for item2 in evidenceNode:
				if item == item2[self.nodeNameIdx]:
					probVarListTemp = probVarListTemp + [item2[self.nodeValIdx]]
					isVar = False
					break
			if isVar:
				probVarListTemp = probVarListTemp + [item]
		probability = cNode.probability
		for i in range(len(probVarListTemp)):	# Leave nodes which correspond to evidenceNode
			temp = []
			if probVarListTemp[i] == '+' or probVarListTemp[i] == '-':	# When node is in evidenceNode,
				for j in range(len(probability)):
					if probVarListTemp[i] == probability[j][self.probAssignIdx][2*i : 2*i+1]:	# When the probability has same value with evidence node, add that node into probability list
						temp.append(probability[j])
				probability = temp
		probVarList = []
		probabilityTemp = []
		for j in range(len(probability)):	# Initialize probabilityTemp
			probabilityTemp.append( [ probability[j][self.probIdx], '' ] )
		for i in range(len(probVarListTemp)):
			if probVarListTemp[i] != '+' and probVarListTemp[i] != '-':	# When node is variable, add them to probVarList and probabilityTemp
				probVarList.append(probVarListTemp[i])
				for j in range(len(probability)):
					if probabilityTemp[j][self.probAssignIdx] == '':
						probabilityTemp[j][self.probAssignIdx] = probability[j][self.probAssignIdx][2*i : 2*i+1]
					else:
						probabilityTemp[j][self.probAssignIdx] = probabilityTemp[j][self.probAssignIdx] + " " + probability[j][self.probAssignIdx][2*i : 2*i+1]
		self.probVarList = probVarList
		if self.probVarList:
			self.probability = probabilityTemp
		else:
			self.probability = probabilityTemp[0][self.probIdx]
	@classmethod
	def factorSum(cls, factorInst, var):	# Summation of a which eliminates var
		if not cls.checkInList(factorInst, var):
			return False
		result = Factor()
		result.probVarList = copy.deepcopy(factorInst.probVarList)
		for i in range(len(result.probVarList)):	# Delete var in the probVarList
			if var == result.probVarList[i]:
				sumIdx = i
				del result.probVarList[sumIdx]
				break
		tempAssign = cls.probAssignSet([], len(result.probVarList))	# Assignment of + and -
		for item in tempAssign:
			temp = []
			temp.append(str(cls.removeProbElemBySum(factorInst, result, item, sumIdx)))
			temp.append(item)
			result.probability.append(temp)
		if not tempAssign:
			probP = cls.getProbability(factorInst.probability, "+")
			probN = cls.getProbability(factorInst.probability, "-")
			result.probability = float(probP) + float(probN)
		return result
	@classmethod
	def removeProbElemBySum(cls, parent, child, assign, sumIdx):
		if len(assign) > 2*sumIdx:
			probP = cls.getProbability(parent.probability, assign[:2*sumIdx] + "+ " + assign[2*sumIdx:])
			probN = cls.getProbability(parent.probability, assign[:2*sumIdx] + "- " + assign[2*sumIdx:])
		else:
			probP = cls.getProbability(parent.probability, assign + " +")
			probN = cls.getProbability(parent.probability, assign + " -")
		return float(probP) + float(probN)
	@classmethod
	def factorMul(cls, a, b, var):	# Multiplication between a and b according to var
		if not cls.checkInList(a, var):
			return False
		if not cls.checkInList(b, var):
			return False
		result = Factor()
		for item in a.probVarList:	# Make result Factor's probVarList
			result.probVarList.append(item)
		for item in b.probVarList:
			isInList = False
			for item2 in result.probVarList:
				if item == item2:
					isInList = True
					break
			if not isInList:
				result.probVarList.append(item)
		tempAssign = cls.probAssignSet([], len(result.probVarList))
		for item in tempAssign:
			temp = []
			probA = float(cls.getProbability(a.probability, cls.findProbabilityAssign(result.probVarList, item, a.probVarList)))
			probB = float(cls.getProbability(b.probability, cls.findProbabilityAssign(result.probVarList, item, b.probVarList)))
			temp.append(str(probA * probB))
			temp.append(item)
			result.probability.append(temp)
		return result
	@classmethod
	def checkInList(cls, factorInst, var):	# Check whether Factor instance contains variable var
		for item in factorInst.probVarList:
			if var == item:
				return True
		return False
	@classmethod
	def findProbabilityAssign(cls, parent, assign, child):	# Find child's probability assignment according to parent
		result = ""
		for j in range(len(child)):
			item = child[j]
			for i in range(len(parent)):
				if item == parent[i]:
					if j == 0:
						result = result + assign[2*i:2*i+1]
					else:
						result = result + " " + assign[2*i:2*i+1]
					break
		return result
	@classmethod
	def getProbability(cls, probabilityList, assign):	# Return probability of assign in probabilityList
		for item in probabilityList:
			if assign == item[cls.probAssignIdx]:
				return item[cls.probIdx]
	@classmethod
	def probAssignSet(cls, assign, varNum):	# Make a whole set of assign with varNum number of variables.
		if varNum == 0:
			return assign
		if not assign:
			assign = ['+', '-']
		else:
			temp = []
			for item in assign:
				temp.append('+ ' + item)
			for item in assign:
				temp.append('- ' + item)
			assign = temp
		return cls.probAssignSet(assign, varNum-1)
	@classmethod
	def normalize(cls, factorList, queryNode, decisionNode):	# Normalize probability and return the variable's probability according to queryNode's assign
		for factorInst in factorList:
			if not factorInst.probVarList:	# If factorInstance's probability variable is empty,
				continue
			else:
				queryVar = []
				queryAssign = ""
				decisionAssignIdx = []
				for i in range(len(factorInst.probVarList)):
					var = factorInst.probVarList[i]
					for item in queryNode:
						if var == item[cls.nodeNameIdx]:
							queryVar.append(item[cls.nodeNameIdx])
							if queryAssign == "":
								queryAssign = item[cls.nodeValIdx]
							else:
								queryAssign = queryAssign + " " + item[cls.nodeValIdx]
							for dNode in decisionNode:
								if item[cls.nodeNameIdx] == dNode:
									decisionAssignIdx.append( [ i , item[cls.nodeValIdx] ] )
							break
				denominator = 0.0
				for factorProb in factorInst.probability:	# Find numerator and denominator in order to normalize
					if factorProb[cls.probAssignIdx] == queryAssign:
						numerator = float(factorProb[cls.probIdx])
						denominator = denominator + float(factorProb[cls.probIdx])
					else:
						isDecisionAssignIdx = True
						for item in decisionAssignIdx:
							assignPos = item[0]
							assignChar = item[1]
							if factorProb[cls.probAssignIdx][2*assignPos : 2*assignPos+1] != assignChar:
								isDecisionAssignIdx = False
								break
						if isDecisionAssignIdx:
							denominator = denominator + float(factorProb[cls.probIdx])
				result = numerator / denominator	# result canceled out in numerator and denominator
		return result
	@classmethod
	def checkDNodeAssign(cls, factorInst, decisionNode, queryNode):
		probVarList = factorInst.probVarList
		

class SolveQuery:	# Solve query
	queryTypeIdx = 0
	queryQuestionIdx = 1
	nodeNameIdx = 0
	nodeValIdx = 1
	utilValIdx = 0
	utilAssignIdx = 1
	firstElem = 0
	resolution = 0.01
	assignList = ['+', '-']
	def __init__(self, bayesianNetwork):
		self.bn = bayesianNetwork
		self.f = self.bn.f
		self.initialize()
	def initialize(self):
		temp = []
	def solve(self):
		query = self.f.query
		queryTypeIdx = self.queryTypeIdx
		queryQuestionIdx = self.queryQuestionIdx
		result = ""
		for item in query:
			if item[queryTypeIdx] == "P":
				temp = self.solveP(item[queryQuestionIdx])
				temp = round(temp / self.resolution, 0) * self.resolution
				temp = format(temp, '.2f')
			elif item[queryTypeIdx] == "EU":
				temp = self.solveEU(item[queryQuestionIdx])
				temp = round(temp, 0)
				temp = str(int(temp))
				temp = str((temp))
			elif item[queryTypeIdx] == "MEU":
				assign, value = self.solveMEU(item[queryQuestionIdx])
				value = round(value, 0)
				value = str(int(value))
				temp = assign + " " + value
			if not result:
				result = temp
			else:
				result = result + "\n" + temp
		return result
	def solveP(self, question):
		cNodes = self.bn.cNodes
		queryNode, evidenceNode, MEUVar = self.findQueryEvidenceNode(question)
		hiddenNode = self.findHiddenNode(queryNode + evidenceNode)
		result = self.probByFactor(self.bn.cNodes, queryNode, evidenceNode, hiddenNode, self.bn.dNodes)
		return result
	def solveEU(self, question):
		cNodes = self.bn.cNodes
		queryNode, evidenceNode, MEUVar = self.findQueryEvidenceNode(question)
		hiddenNode = self.findHiddenNode(queryNode + evidenceNode)
		decisionNode = self.bn.dNodes
		utilityNodes = self.bn.uNodes
		result = self.EUByFactor(self.bn.cNodes, queryNode, evidenceNode, hiddenNode, decisionNode, utilityNodes)
		return result
	def solveMEU(self, question):
		cNodes = self.bn.cNodes
		queryNode, evidenceNode, MEUVar = self.findQueryEvidenceNode(question)
		hiddenNode = self.findHiddenNode(queryNode + evidenceNode)
		decisionNode = self.bn.dNodes
		utilityNodes = self.bn.uNodes
		assign, value = self.MEUByFactor(self.bn.cNodes, queryNode, evidenceNode, hiddenNode, decisionNode, utilityNodes, MEUVar)
		return assign, value
	def findQueryEvidenceNode(self, question):	# Used for P
		temp = question
		temp = temp.replace(" ", "")
		queryNode = []
		evidenceNode = []
		MEUVar = []
		delimiter = temp.find("|")
		if delimiter != -1:	# When there is parent node,
			tempChild = temp[:delimiter]
			tempParent = temp[delimiter+1:]
		else:	# When there is no parent node,
			tempChild = temp
			tempParent = ""
		tempChildList = []	# Make all child nodes into list
		delimiter = tempChild.find(",")
		while delimiter != -1:
			tempChildList.append(tempChild[0:delimiter])
			tempChild = tempChild[delimiter+1:]
			delimiter = tempChild.find(",")
		tempChildList.append(tempChild)	# Add last one left in tempChild
		for tempChild in tempChildList:
			delimiter = tempChild.find("=")
			if delimiter != -1:	# If there is assigned value,
				queryNode.append( [ tempChild[0:delimiter], tempChild[delimiter+1:delimiter+2] ] )
			else:	# If there is no assigned value,
				MEUVar.append(tempChild)
		if tempParent:
			tempParentList = []	# Make all parent nodes into list
			delimiter = tempParent.find(",")
			while delimiter != -1:
				tempParentList.append(tempParent[0:delimiter])
				tempParent = tempParent[delimiter+1:]
				delimiter = tempParent.find(",")
			tempParentList.append(tempParent)	# Add last one left in tempParent
			for tempParent in tempParentList:
				delimiter = tempParent.find("=")
				if delimiter != -1:	# If there is assigned value,
					evidenceNode.append( [ tempParent[0:delimiter], tempParent[delimiter+1:delimiter+2] ] )
				else:	# If there is no assigned value,
					MEUVar.append(tempParent)
		return queryNode, evidenceNode, MEUVar
	def probByFactor(self, cNodes, queryNode, evidenceNode, hiddenNode, decisionNode):	# Return probability factor as not rounded
		factorList = []
		for item in cNodes:	# When making factorList, factors excludes evidence nodes
			temp = Factor()
			temp.initialize(item, queryNode, evidenceNode, hiddenNode)
			factorList.append(temp)
		for var in hiddenNode:	# Calculate for each hiddenNode
			isFirst = True
			newFactorList = []
			for factor in factorList:	# Check all factors in the factorList
				
				if not Factor.checkInList(factor, var):	# If factor doesn't have hiddenNode,
					newFactorList.append(factor)	# Save factor for later use
					continue
				if isFirst:	# If factor is the first node which has hiddenNode,
					newFactor = factor
					isFirst = False
				else:
					newFactor = Factor.factorMul(newFactor, factor, var)	# Multiply factors which have hiddenNodes
			newFactor = Factor.factorSum(newFactor, var)	# Sum out the hiddenNode so that remove hiddenNode from factors
			newFactorList.append(newFactor)
			factorList = newFactorList
		for item in queryNode:
			var = item[self.nodeNameIdx]
			isFirst = True
			newFactorList = []
			for factor in factorList:	# Multiply factors which have var
				if not Factor.checkInList(factor, var):	# If factor doesn't have var,
					newFactorList.append(factor)	# Save factor for later use
					continue
				if isFirst:	# If factor is the first node which has var,
					newFactor = factor
					isFirst = False
				else:
					newFactor = Factor.factorMul(newFactor, factor, var)	# Multiply factors which have var
			newFactorList.append(newFactor)
			factorList = newFactorList
		result = Factor.normalize(factorList, queryNode, bn.dNodes)
		return result
	def EUByFactor(self, cNodes, queryNode, evidenceNode, hiddenNode, decisionNode, utilityNodes):
		utilityVar = self.findUtilityVar(queryNode, evidenceNode, utilityNodes)
		tempHiddenNode = []
		for item in hiddenNode:	# Insert hidden nodes into tempHiddenNode which is not in the utilityVar
			isInUtility = False
			for item2 in utilityVar:
				if item == item2:
					isInUtility = True
					break
			if not isInUtility:
				tempHiddenNode.append(item)
		tempQueryNodeList = []
		tempQueryNode = []
		tempQueryNodeList = self.makeUtilityEvidenceNode(tempQueryNodeList, utilityVar, tempQueryNode)
		result = 0
		for tempQueryNode in tempQueryNodeList:
			probOfUtil = self.probByFactor(cNodes, queryNode + tempQueryNode, evidenceNode, tempHiddenNode, decisionNode)
			utilVal = float(self.findUtilityVal(queryNode + tempQueryNode + evidenceNode, utilityNodes))
			result = result + probOfUtil * utilVal
		return result
	def MEUByFactor(self, cNodes, queryNode, evidenceNode, hiddenNode, decisionNode, utilityNodes, MEUVar):
		tempQueryNodeList = []
		tempQueryNode = []
		tempQueryNodeList = self.makeUtilityEvidenceNode(tempQueryNodeList, MEUVar, tempQueryNode)
		result = 0
		for tempQueryNode in tempQueryNodeList:
			hiddenNode = self.findHiddenNode(queryNode + tempQueryNode + evidenceNode)
			temp = self.EUByFactor(cNodes, queryNode + tempQueryNode, evidenceNode, hiddenNode, decisionNode, utilityNodes)
			if result < temp:
				result = temp
				assign = self.findAssign(tempQueryNode, MEUVar)
		return assign, result
	def findAssign(self, evidenceNode, varList):
		assign = ""
		for var in varList:
			for node in evidenceNode:
				if var == node[self.nodeNameIdx]:
					if assign == "":
						assign = node[self.nodeValIdx]
					else:
						assign = assign + " " + node[self.nodeValIdx]
					break
		return assign
	def findUtilityVal(self, tempEvidenceNode, utilityNodes):
		assign = ""
		for uNodeList in utilityNodes:
			for uNode in uNodeList[self.nodeNameIdx]:
				for eNode in tempEvidenceNode:
					if uNode == eNode[self.nodeNameIdx]:
						if assign == "":
							assign = assign + eNode[self.nodeValIdx]
						else:
							assign = assign + " " + eNode[self.nodeValIdx]
			for uNode in uNodeList[self.nodeValIdx]:
				if uNode[self.utilAssignIdx] == assign:
					return uNode[self.utilValIdx]
	def makeUtilityEvidenceNode(self, tempEvidenceNodeList, utilityVar, tempEvidenceNode):
		if not utilityVar:
			tempEvidenceNodeList.append(copy.deepcopy(tempEvidenceNode))
			return tempEvidenceNodeList
		for assign in self.assignList:
			tempEvidenceNode.append( [ utilityVar[0], assign ] )
			tempEvidenceNodeList = self.makeUtilityEvidenceNode(tempEvidenceNodeList, utilityVar[1:], tempEvidenceNode)
			del tempEvidenceNode[-1]
		return tempEvidenceNodeList
	def findUtilityVar(self, queryNode, evidenceNode, utilityNodes):
		utilityVar = []
		for uNodeList in utilityNodes:	# Initialize unitlityVar list by inserting every utilityNodes
			for uNode in uNodeList[self.nodeNameIdx]:
				isAdded = False
				for addedNode in utilityVar:	# If uNode is added in utilityVar list already, skip it
					if uNode == addedNode:
						isAdded = True
						break
				if not isAdded:
					utilityVar.append(uNode)
		if queryNode:
			for qNode in queryNode:
				for i in range(len(utilityVar)):
					if qNode[self.nodeNameIdx] == utilityVar[i]:
						del utilityVar[i]
						break
		if evidenceNode:
			for eNode in evidenceNode:
				for i in range(len(utilityVar)):
					if eNode[self.nodeNameIdx] == utilityVar[i]:
						del utilityVar[i]
						break
		return utilityVar
	def findEvidenceNode(self, question):	# Used for EU
		temp = question
		temp = temp.replace(" ", "")
		evidenceNode = []
		delimiter = temp.find("=")
		while delimiter != -1:
			evidenceNode.append( [ temp[0:delimiter], temp[delimiter+1:delimiter+2] ] )
			temp = temp[delimiter+3:]
			delimiter = temp.find("=")
		return evidenceNode
	def findHiddenNode(self, qeNode):
		hiddenNode = []
		for item in self.bn.cNodes:
			isHidden = True
			for item2 in qeNode:
				if item.node == item2[self.nodeNameIdx]:
					isHidden = False
					break
			if isHidden:
				hiddenNode.append(item.node)
		for dNode in self.bn.dNodes:
			isHidden = True
			for item2 in qeNode:
				if dNode == item2[self.nodeNameIdx]:
					isHidden = False
					break
			if isHidden:
				hiddenNode.append(dNode)
		return hiddenNode


##### Execution #####
a = OpenFile()
f = ParseFile(a.fileObj)
bn = BayesianNetwork(f)
sq = SolveQuery(bn)

outFile = OutFile("output.txt")
outFile.write(sq.solve())