import argparse

## Global Constants
BOARD_SIZE = 5
INFINITY = 987654321
BOARD_COL_CHAR = ['A', 'B', 'C', 'D', 'E']
NOT_DEPLOYED = '*'

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
taskNum = int(f.readline().strip())	## Read task number
if taskNum in [1, 2, 3]:	## If task number is 1, 2 or 3,
	myPlayer = f.readline().strip()
	if myPlayer == 'X':
		othPlayer = 'O'
	elif myPlayer == 'O':
		othPlayer = 'X'
	cutOff = int(f.readline().strip())
	boardValue = [[eval(val) for val in f.readline().split()] for i in range(BOARD_SIZE)]
	boardState = []
	for i in range(BOARD_SIZE):
		line = f.readline()
		boardState.append([])
		for j in range(BOARD_SIZE):
			boardState[i] += line[j]
elif taskNum == 4:	## If task number is 4,
	player1 = f.readline().strip()
	player1Algo = int(f.readline().strip())
	player1CutOff = int(f.readline().strip())
	player2 = f.readline().strip()
	player2Algo = int(f.readline().strip())
	player2CutOff = int(f.readline().strip())
	boardValue = [[eval(val) for val in f.readline().split()] for i in range(BOARD_SIZE)]
	boardState = []
	for i in range(BOARD_SIZE):
		line = f.readline()
		boardState.append([])
		for j in range(BOARD_SIZE):
			boardState[i] += line[j]
else:
	print "task number should be 1, 2, 3 or 4!"
	exit()

## Define classes and functions
class Node :	## board's element node
	def __init__(self, row, col, depth, value = 0, alpha = 0, beta = 0):
		if row == -1 and col == -1:
			self.nodeName = "root"
		else:
			self.nodeName = BOARD_COL_CHAR[col] + str(row+1)
		self.row = row
		self.col = col
		self.depth = depth
		self.value = value
		self.alpha = alpha
		self.beta = beta
def printBoardintoFile():	## Print board state into file
	f.write("\n")
	for i in range(BOARD_SIZE):
		printRow = ""
		for j in range(BOARD_SIZE):
			printRow += boardState[i][j]
		if i < BOARD_SIZE - 1:
			printRow += "\n"
		f.write(printRow)
def printMinimaxNode(node):
	if taskNum == 2:
		if node.value == INFINITY:
			valueStr = "Infinity"
		elif node.value == -INFINITY:
			valueStr = "-Infinity"
		else:
			valueStr = str(node.value)
		f.write("\n" + node.nodeName + "," + str(node.depth) + "," + valueStr)
		# printBoardintoFile()#####
def printAlphaBetaNode(node):
	if taskNum == 3:
		if node.value == INFINITY:
			valueStr = "Infinity"
		elif node.value == -INFINITY:
			valueStr = "-Infinity"
		else:
			valueStr = str(node.value)
		if node.alpha == INFINITY:
			alphaStr = "Infinity"
		elif node.alpha == -INFINITY:
			alphaStr = "-Infinity"
		else:
			alphaStr = str(node.alpha)
		if node.beta == INFINITY:
			betaStr = "Infinity"
		elif node.beta == -INFINITY:
			betaStr = "-Infinity"
		else:
			betaStr = str(node.beta)
		f.write("\n" + node.nodeName + "," + str(node.depth) + "," + valueStr + "," + alphaStr + "," + betaStr)
		# printBoardintoFile()#####
def evalFunc(myPlayer, boardState):	## Calculate player's value
	if myPlayer == 'X':
		othPlayer = 'O'
	elif myPlayer == 'O':
		othPlayer = 'X'
	value = 0
	for i in range(BOARD_SIZE):
		for j in range(BOARD_SIZE):
			if boardState[i][j] == myPlayer:
				value += boardValue[i][j]
			elif boardState[i][j] == othPlayer:
				value -= boardValue[i][j]
	return value
def myMove(myPlayer, row, col):	## Define whether my move is raid or sneak
	if myPlayer == 'X':
		othPlayer = 'O'
	elif myPlayer == 'O':
		othPlayer = 'X'
	if (col - 1 >= 0 and boardState[row][col - 1] == myPlayer) or (row - 1 >= 0 and boardState[row - 1][col] == myPlayer) or (col + 1 <= BOARD_SIZE - 1 and boardState[row][col + 1] == myPlayer) or (row + 1 <= BOARD_SIZE - 1 and boardState[row + 1][col] == myPlayer):
		return "raid"
	else:
		return "sneak"
def nextMoveCommit(myPlayer, row, col):	## change the board state by next move
	if myPlayer == 'X':
		othPlayer = 'O'
	elif myPlayer == 'O':
		othPlayer = 'X'
	boardState[row][col] = myPlayer
	if myMove(myPlayer, row, col) == "raid":
		if (col - 1 >= 0 and boardState[row][col - 1] == othPlayer):
			boardState[row][col - 1] = myPlayer
		if (row - 1 >= 0 and boardState[row - 1][col] == othPlayer):
			boardState[row - 1][col] = myPlayer
		if (col + 1 <= BOARD_SIZE - 1 and boardState[row][col + 1] == othPlayer):
			boardState[row][col + 1] = myPlayer
		if (row + 1 <= BOARD_SIZE - 1 and boardState[row + 1][col] == othPlayer):
			boardState[row + 1][col] = myPlayer
def nextMoveTemp(myPlayer, row, col):	## change the board state by next move
	if myPlayer == 'X':
		othPlayer = 'O'
	elif myPlayer == 'O':
		othPlayer = 'X'
	boardState[row][col] = myPlayer
	raidedArr = []
	if myMove(myPlayer, row, col) == "raid":
		if (col - 1 >= 0 and boardState[row][col - 1] == othPlayer):
			boardState[row][col - 1] = myPlayer
			raidedArr.append((row, col - 1))
		if (row - 1 >= 0 and boardState[row - 1][col] == othPlayer):
			boardState[row - 1][col] = myPlayer
			raidedArr.append((row - 1, col))
		if (col + 1 <= BOARD_SIZE - 1 and boardState[row][col + 1] == othPlayer):
			boardState[row][col + 1] = myPlayer
			raidedArr.append((row, col + 1))
		if (row + 1 <= BOARD_SIZE - 1 and boardState[row + 1][col] == othPlayer):
			boardState[row + 1][col] = myPlayer
			raidedArr.append((row + 1, col))
	return raidedArr
def reverseNextMoveTemp(myPlayer, row, col, raidedArr):	## change the board state by next move
	if myPlayer == 'X':
		othPlayer = 'O'
	elif myPlayer == 'O':
		othPlayer = 'X'
	boardState[row][col] = NOT_DEPLOYED
	for grid in raidedArr:
		boardState[grid[0]][grid[1]] = othPlayer
def retMax(val1, val2):	## return maximum value
	if val1 >= val2:
		return val1
	else:
		return val2
def retMin(val1, val2):	## return minimum value
	if val1 <= val2:
		return val1
	else:
		return val2
def boardRemainCheck():
	remain = "T"
	for i in range(BOARD_SIZE):
		for j in range(BOARD_SIZE):
			if boardState[i][j] == NOT_DEPLOYED:
				return remain == "T"
	return remain == "F"

def greedyBestFirstSearch(myPlayer, cutOff):	## Perform greedy Best-First Search
	if myPlayer == 'X':
		othPlayer = 'O'
	elif myPlayer == 'O':
		othPlayer = 'X'
	rootNode = Node(-1, -1, 0, -INFINITY)
	maxVal = -INFINITY
	for i in range(BOARD_SIZE):
		for j in range(BOARD_SIZE):
			if boardState[i][j] == NOT_DEPLOYED:
				raidedArr = nextMoveTemp(myPlayer, i, j)
				childNodeVal = evalFunc(myPlayer, boardState)
				if childNodeVal > maxVal:
					maxVal = childNodeVal
					rootNode.row = i
					rootNode.col = j
				reverseNextMoveTemp(myPlayer, i, j, raidedArr)
				rootNode.value = maxVal
	return rootNode

def minimaxMax(myPlayer, row, col, depth, cutOff):
	if myPlayer == 'X':
		othPlayer = 'O'
	elif myPlayer == 'O':
		othPlayer = 'X'
	maxChildNode = Node(row, col, depth, -INFINITY)
	maxVal = -INFINITY
	if depth < cutOff and boardRemainCheck():
		printMinimaxNode(maxChildNode)
		for i in range(BOARD_SIZE):
			for j in range(BOARD_SIZE):
				if boardState[i][j] == NOT_DEPLOYED:
					raidedArr = nextMoveTemp(myPlayer, i, j)
					childNode = minimaxMin(myPlayer, i, j, depth + 1, cutOff)
					if childNode.value > maxVal:
						maxVal = childNode.value
					reverseNextMoveTemp(myPlayer, i, j, raidedArr)
					maxChildNode.value = maxVal
					printMinimaxNode(maxChildNode)
	else:
		maxChildNode.value = evalFunc(myPlayer, boardState)
		printMinimaxNode(maxChildNode)
	return maxChildNode
def minimaxMin(myPlayer, row, col, depth, cutOff):
	if myPlayer == 'X':
		othPlayer = 'O'
	elif myPlayer == 'O':
		othPlayer = 'X'
	minChildNode = Node(row, col, depth, INFINITY)
	minVal = INFINITY
	if depth < cutOff and boardRemainCheck():
		printMinimaxNode(minChildNode)
		for i in range(BOARD_SIZE):
			for j in range(BOARD_SIZE):
				if boardState[i][j] == NOT_DEPLOYED:
					raidedArr = nextMoveTemp(othPlayer, i, j)
					childNode = minimaxMax(myPlayer, i, j, depth + 1, cutOff)
					if childNode.value < minVal:
						minVal = childNode.value
					reverseNextMoveTemp(othPlayer, i, j, raidedArr)
					minChildNode.value = minVal
					printMinimaxNode(minChildNode)
	else:
		minChildNode.value = evalFunc(myPlayer, boardState)
		printMinimaxNode(minChildNode)
	return minChildNode
def minimax(myPlayer, cutOff):	## perform minimax search
	if myPlayer == 'X':
		othPlayer = 'O'
	elif myPlayer == 'O':
		othPlayer = 'X'
	if taskNum == 2:
		global f
		f = open("traverse_log.txt", 'w')
		f.write("Node,Depth,Value")
	rootNode = Node(-1, -1, 0, -INFINITY)
	printMinimaxNode(rootNode)
	maxVal = -INFINITY
	for i in range(BOARD_SIZE):
		for j in range(BOARD_SIZE):
			if boardState[i][j] == NOT_DEPLOYED:
				raidedArr = nextMoveTemp(myPlayer, i, j)
				childNode = minimaxMin(myPlayer, i, j, 1, cutOff)
				if childNode.value > maxVal:
					maxVal = childNode.value
					rootNode.row = i
					rootNode.col = j
				reverseNextMoveTemp(myPlayer, i, j, raidedArr)
				rootNode.value = maxVal
				printMinimaxNode(rootNode)
	if taskNum == 2:
		f.close()
	return rootNode

def alphaBetaMax(myPlayer, row, col, depth, alpha, beta, cutOff):
	if myPlayer == 'X':
		othPlayer = 'O'
	elif myPlayer == 'O':
		othPlayer = 'X'
	currentNode = Node(row, col, depth, -INFINITY, alpha, beta)
	maxVal = -INFINITY
	if depth < cutOff and boardRemainCheck():
		printAlphaBetaNode(currentNode)
		for i in range(BOARD_SIZE):
			for j in range(BOARD_SIZE):
				if boardState[i][j] == NOT_DEPLOYED:
					raidedArr = nextMoveTemp(myPlayer, i, j)
					childNode = alphaBetaMin(myPlayer, i, j, depth + 1, currentNode.alpha, currentNode.beta, cutOff)
					if childNode.value > maxVal:
						maxVal = childNode.value
					currentNode.value = maxVal
					if childNode.value >= currentNode.beta:
						reverseNextMoveTemp(myPlayer, i, j, raidedArr)
						printAlphaBetaNode(currentNode)
						break
					if childNode.value > currentNode.alpha:
						currentNode.alpha = childNode.value
					reverseNextMoveTemp(myPlayer, i, j, raidedArr)
					printAlphaBetaNode(currentNode)
			if 'childNode' in locals() and childNode.value >= currentNode.beta:
				break
	else:
		currentNode.value = evalFunc(myPlayer, boardState)
		printAlphaBetaNode(currentNode)
	return currentNode
def alphaBetaMin(myPlayer, row, col, depth, alpha, beta, cutOff):
	if myPlayer == 'X':
		othPlayer = 'O'
	elif myPlayer == 'O':
		othPlayer = 'X'
	currentNode = Node(row, col, depth, INFINITY, alpha, beta)
	minVal = INFINITY
	if depth < cutOff and boardRemainCheck():
		printAlphaBetaNode(currentNode)
		for i in range(BOARD_SIZE):
			for j in range(BOARD_SIZE):
				if boardState[i][j] == NOT_DEPLOYED:
					raidedArr = nextMoveTemp(othPlayer, i, j)
					childNode = alphaBetaMax(myPlayer, i, j, depth + 1, currentNode.alpha, currentNode.beta, cutOff)
					if childNode.value < minVal:
						minVal = childNode.value
					currentNode.value = minVal
					if childNode.value <= currentNode.alpha:
						reverseNextMoveTemp(othPlayer, i, j, raidedArr)
						printAlphaBetaNode(currentNode)
						break
					if childNode.value < currentNode.beta:
						currentNode.beta = childNode.value
					reverseNextMoveTemp(othPlayer, i, j, raidedArr)
					printAlphaBetaNode(currentNode)
			if 'childNode' in locals() and childNode.value <= currentNode.alpha:
				break
	else:
		currentNode.value = evalFunc(myPlayer, boardState)
		printAlphaBetaNode(currentNode)
	return currentNode
def alphaBetaPruning(myPlayer, cutOff):	## perform alpha beta pruning search
	if myPlayer == 'X':
		othPlayer = 'O'
	elif myPlayer == 'O':
		othPlayer = 'X'
	if taskNum == 3:
		global f
		f = open("traverse_log.txt", 'w')
		f.write("Node,Depth,Value,Alpha,Beta")
	rootNode = Node(-1, -1, 0, -INFINITY, -INFINITY, INFINITY)
	printAlphaBetaNode(rootNode)
	maxVal = -INFINITY
	for i in range(BOARD_SIZE):
		for j in range(BOARD_SIZE):
			if boardState[i][j] == NOT_DEPLOYED:
				raidedArr = nextMoveTemp(myPlayer, i, j)
				childNode = alphaBetaMin(myPlayer, i, j, 1, rootNode.alpha, rootNode.beta, cutOff)
				if childNode.value > maxVal:
					maxVal = childNode.value
					rootNode.row = i
					rootNode.col = j
				rootNode.value = maxVal
				rootNode.alpha = maxVal
				reverseNextMoveTemp(myPlayer, i, j, raidedArr)
				printAlphaBetaNode(rootNode)
	if taskNum == 3:
		f.close()
	return rootNode

def printBoard(boardState):	## print board state into next_state.txt file
	f = open("next_state.txt", 'w')
	for i in range(BOARD_SIZE):
		printRow = ""
		for j in range(BOARD_SIZE):
			printRow += boardState[i][j]
		if i < BOARD_SIZE - 1:
			printRow += "\n"
		f.write(printRow)
	f.close()

if taskNum == 1:	## when Greedy Best-first Search,
	# print "Greedy Best-first Search"
	nextNode = greedyBestFirstSearch(myPlayer, 1)
	nextMoveCommit(myPlayer, nextNode.row, nextNode.col)
	printBoard(boardState)
elif taskNum == 2:	## when MiniMax,
	# print "MiniMax"
	nextNode = minimax(myPlayer, cutOff)
	nextMoveCommit(myPlayer, nextNode.row, nextNode.col)
	printBoard(boardState)
elif taskNum == 3:	## when Alpha-beta Pruning,
	# print "Alpha-beta Pruning"
	nextNode = alphaBetaPruning(myPlayer, cutOff)
	nextMoveCommit(myPlayer, nextNode.row, nextNode.col)
	printBoard(boardState)
elif taskNum == 4:	## when Battle simulation,
	# print "Battle simulation"
	if player1Algo == 1:
		player1Func = globals()['greedyBestFirstSearch']
	elif player1Algo == 2:
		player1Func = globals()['minimax']
	elif player1Algo == 3:
		player1Func = globals()['alphaBetaPruning']
	else:
		print "Wrong first player's algorithm"
		exit()
	if player2Algo == 1:
		player2Func = globals()['greedyBestFirstSearch']
	elif player2Algo == 2:
		player2Func = globals()['minimax']
	elif player2Algo == 3:
		player2Func = globals()['alphaBetaPruning']
	else:
		print "Wrong first player's algorithm"
		exit()
	f = open("trace_state.txt", 'w')
	battleCount = 0
	while 1:
		player1Node = player1Func(player1, player1CutOff)
		if player1Node.value == -INFINITY:
			break
		nextMoveCommit(player1, player1Node.row, player1Node.col)
		if battleCount > 0:
			f.write("\n")
		printBoardintoFile()
		player2Node = player2Func(player2, player2CutOff)
		if player2Node.value == -INFINITY:
			break
		nextMoveCommit(player2, player2Node.row, player2Node.col)
		f.write("\n")
		printBoardintoFile()
		battleCount+=1