# some code from
	#http://pygame.org/wiki/TextWrap
	#http://thepythongamebook.com/en:pygame:step003


import pygame
import pprint
import requests
import requests.auth
import json

secret = "putYourSecretHere"
client_ID = "putYourClientIDHere"
user_agent = "CS290Bot by RegexRationalist"
username = "yourUserName"
password = "SuperS3cr3tp@$$w0rd"

# first we send our client ID and secret to autheticate ourselves
# then we send a post (with username and password) to ask for an access token
# we then get in return the access token

def authenticate(secret, client_ID, user_agent, username,password):
	client_auth = requests.auth.HTTPBasicAuth(client_ID, secret)
	post_data = {"grant_type": "password", "username": username, "password": password}
	headers = {"User-Agent": user_agent}
	response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
	parsedResponse = json.loads(response.content.decode("utf-8"))
	token = parsedResponse["access_token"]
	return token

def getArticles():
	response = requests.get("https://oauth.reddit.com/r/AccidentalRenaissance/hot", headers=headers)
	parsedResponse = json.loads(response.content.decode("utf-8"))["data"]["children"]
	return parsedResponse

def writeParsedToFile(parsedResponse, name):		
	DataFile = open(name, "w")
	DataFile.write(json.dumps(parsedResponse, indent=4, sort_keys=True))
	DataFile.close()

def getTopComments(chosen_thread):		
	#kind of weird because although the api says we need some other data, we actually don't. 
	response = requests.get("https://oauth.reddit.com/r/AccidentalRenaissance/comments/" + chosen_thread, headers=headers)
	parsedResponse = json.loads(response.content.decode("utf-8"))[1]["data"]["children"]
	return parsedResponse


def getSubComments(thread, comment):
	post_data = {"link_id": "t3_" + thread, "children": comment, "api_type":"json", "sort":"top"} 
	response = requests.post("https://oauth.reddit.com/api/morechildren", headers=headers,data=post_data)
	parsedResponse = json.loads(response.content.decode("utf-8"))
	writeParsedToFile(parsedResponse, "needJson")

	return parsedResponse["json"]["data"]["things"]

def vote(comment, dir, type = "comment"):
	prefix = "t1_"
	if (type == "article"):
		prefix = "t3_"
	post_data = {"id": prefix + comment, "dir":dir} 
	response = requests.post("https://oauth.reddit.com/api/vote", headers=headers,data=post_data)

def printComments(comments):
	for comment in comments:
		print(comment["data"]["body"] + "\n")

def printArticles(Articles):
	count = 0
	for comment in Articles:
		currCount = str(count)
		print(currCount+ "    " + comment["data"]["id"] + "   " + comment["data"]["title"] + "\n")
		count+= 1

def getArticlesInfo(Articles):
	count = 0
	ids = []
	texts = []
	replies = []

	for article in Articles:
		currCount = str(count)
		ids.append(article["data"]["id"])
		texts.append(article["data"]["title"])
		if (article["data"]["num_comments"] > 0):
			replies.append(True)
		else:
			replies.append(False)
		count+= 1
	return ids,texts,count, replies


# text wrapping function from http://pygame.org/wiki/TextWrap
# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def drawText(surface, text, color, rect, font, aa=False, bkg=None):
	rect = pygame.Rect(rect)
	y = rect.top
	lineSpacing = -2

	# get the height of the font
	fontHeight = font.size("Tg")[1]

	while text:
		i = 1

		# determine if the row of text will be outside our area
		if y + fontHeight > rect.bottom:
			break

		# determine maximum width of line
		while font.size(text[:i])[0] < rect.width and i < len(text):
			i += 1

		# if we've wrapped the text, then adjust the wrap to the last word      
		if i < len(text): 
			i = text.rfind(" ", 0, i) + 1

		# render the line and blit it to the surface
		if bkg:
			image = font.render(text[:i], 1, color, bkg)
			image.set_colorkey(bkg)
		else:
			image = font.render(text[:i], aa, color)

		surface.blit(image, (rect.left, y))
		y += fontHeight + lineSpacing

		# remove the text we just blitted
		text = text[i:]

	return text
def writeToSurface(surface, text, size=13):
	print(drawText(surface, text, (0,0,255),(0,0,surface.get_size()[0], 
		surface.get_size()[1]), pygame.font.SysFont('arial', size)))

def makeBoxes(numBoxes):
	boxes = []
	for x in range (0,numBoxes):
		textString = str(x) + " " * 100
		newBox = [pygame.Surface((640,boxHeight)), textString]
		writeToSurface(newBox[0], newBox[1])
		boxes.insert(x,newBox)
	return boxes

def getVoteSurface(dir, fill=0):
	voteSurface = pygame.Surface((50,50))
	voteSurface.fill((0,0,0))
	if (dir == 1):
		pygame.draw.polygon(voteSurface, (0,180,0), ((10,40),(25,10),(40,40)),fill)
	else:
		pygame.draw.polygon(voteSurface, (180,0,0), ((10,10),(25,40),(40,10)),fill)
	return voteSurface


def makeContainers(IDs, textArray, numContainers, replies):
	containers = []
	for x in range (0,numContainers):
		container = []
		upvote = getVoteSurface(1,2)
		downvote = getVoteSurface(-1,2)
		comments = pygame.Surface((100,100))
		commentsColor = (255,0,0)
		if (replies[x] == False):
			commentsColor = (50,50,50)
		pygame.draw.rect(comments, commentsColor, (0,0,100,100))
		textArea = pygame.Surface((490,100))
		pygame.draw.rect(textArea, (255,255,255), (0,0,490,100))

		writeToSurface(textArea, textArray[x])

		border = pygame.Surface((640,200), pygame.SRCALPHA, 32)
		border.fill((0,0,0,0))
		pygame.draw.rect(border, (50,160,50), (00,0,640,100), 3)
		container.insert(0,upvote)
		container.insert(1,downvote)
		container.insert(2,comments)
		container.insert(3,textArea)
		container.insert(4,border)
		containers.insert(x, container)
	return containers

token = authenticate(secret,client_ID,user_agent,username,password)
headers = {"Authorization": "bearer " + token, "User-Agent": user_agent}

pygame.init()


screen=pygame.display.set_mode((640,480))
background = pygame.Surface(screen.get_size())
background.fill((50,50,50))     
background = background.convert()

backwards = pygame.Surface((200,50))
backwards.fill((0,0,0))

backwardsText = pygame.Surface((640,200), pygame.SRCALPHA, 32)
backwardsText.fill((0,0,0,0))

writeToSurface(backwardsText, "BACK", 30)

backwards.blit(backwardsText, (70,8))
pygame.draw.rect(backwards, (50,160,50), (0,0,200,50), 3)

boxHeight = 100
highestBox = 50
lowestBox = 100
boxx = 0
boxy = highestBox

numArticles = 0

IDs = []
textArray = []
boxes = []
containers = []
replies = []


IDArray = [""]
haveData = False

#Some pygame code from: http://thepythongamebook.com/en:pygame:step003
clock = pygame.time.Clock()
mainloop = True
FPS = 30 # desired framerate in frames per second. try out other values !
playtime = 0.0

def getCommentInfo(Comments, parentID):
	count = 0
	ids = []
	texts = []
	replies = []

	for comment in Comments:
		if (comment["data"]["parent_id"] == parentID):
			currCount = str(count)
			ids.append(comment["data"]["id"])
			texts.append(comment["data"]["body"])
			if (comment["data"]["replies"]==""):
				replies.append(False)
			else:
				replies.append(True)
			count+= 1
	return ids,texts,count, replies

def getSubReplies(IDArray, chosen_thread, chosen_comments):
	parsedResponse = getTopComments(chosen_thread)

	IDArray = IDArray[2:]
	count = 0

	output = []

	for comment in parsedResponse:
		if (comment["data"]["id"] == str(IDArray[0])):
			replies = str(comment["data"]["replies"])
			for chosen in chosen_comments:			
				if (replies.find("parent_id': 't1_" + chosen) > 0):
					output.append(True)
				else:
					output.append(False)
	return output




while mainloop:
	milliseconds = clock.tick(FPS) # do not go faster than this frame rate
	if (haveData == False):
		haveData = True
		highestBox = 50
		if (IDArray == [""]):
			highestBox = 0
			parsedResponse = getArticles();
			IDs, textArray, numArticles, replies = getArticlesInfo(parsedResponse)
		elif (len(IDArray) == 2):
			chosen_thread = IDArray[1]
			parsedResponse = getTopComments(chosen_thread)
			IDs, textArray, numArticles, replies = getCommentInfo(parsedResponse, "t3_" + chosen_thread)
		else:
			chosen_thread = IDArray[1]
			chosen_comment = IDArray[len(IDArray)-1]
			parsedResponse = getSubComments(chosen_thread, chosen_comment)
			IDs, textArray, numArticles, _ = getCommentInfo(parsedResponse, "t1_" + chosen_comment)
			replies = getSubReplies(IDArray, chosen_thread, IDs)

		boxy = highestBox
		lowestBox = numArticles*boxHeight
		boxes = makeBoxes(numArticles)
		containers = makeContainers(IDs, textArray, numArticles, replies)
		box = pygame.Surface((640,numArticles*boxHeight))

	# ----- event handler -----
	for event in pygame.event.get():
		if event.type ==  pygame.MOUSEBUTTONDOWN:

			x,y = event.pos
			print(x, " ", y)

			thing = "article"
			if (len(IDArray) > 1):
				thing = "comment"

			if (thing == "comment" and backwards.get_rect().collidepoint(x,y)): 
				if (thing == "comment"):
					IDArray.pop(len(IDArray)-1)
					haveData = False
				break;

			#for box in boxes:

			for container in range (0,len(boxes)):

				#if we don't click on the comment, don't check things on the comment
				if (not boxes[container][0].get_rect().collidepoint(x-boxx,y-boxy-container*boxHeight)): 	
					continue	

				if containers[container][0].get_rect().collidepoint(x-boxx,y-boxy-container*boxHeight):
					print("upvote! ")
					containers[container][0] = getVoteSurface(1)
					containers[container][1] = getVoteSurface(-1,2)
					vote(IDs[container],1,thing)
				if containers[container][1].get_rect().collidepoint(x-boxx,y-boxy-container*boxHeight-50):
					print("downvote! ", thing)
					containers[container][0] = getVoteSurface(1,2)
					containers[container][1] = getVoteSurface(-1)
					vote(IDs[container],-1,thing)
				if containers[container][2].get_rect().collidepoint(x-boxx-50,y-boxy-container*boxHeight):
					print("get comments! ", IDs[container])
					haveData = False
					IDArray.append(IDs[container])
				if containers[container][3].get_rect().collidepoint(x-boxx-150,y-boxy-container*boxHeight):
					print("text box! ")


		if event.type == pygame.QUIT:
			mainloop = False # pygame window closed by user
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				mainloop = False # user pressed ESC

	keys = pygame.key.get_pressed()  #checking pressed keys
	if keys[pygame.K_UP]:
		print(highestBox, boxy, screen.get_rect()[0],screen.get_rect()[1],screen.get_rect()[2],screen.get_rect()[3])
		if (boxy < highestBox):
			boxy += 5
	if keys[pygame.K_DOWN]:
		print(lowestBox, boxy, screen.get_rect()[0],screen.get_rect()[1],screen.get_rect()[2],screen.get_rect()[3])
		if (boxy - screen.get_rect()[3]> -lowestBox):
			boxy -= 5

	screen.blit(background, (0,0))     # blit the background on the screen (overwriting all)
	screen.blit(box, (boxx,boxy))

	for x in range (0,len(boxes)):
		box.blit(boxes[x][0], (0,(x*boxHeight)))
		box.blit(containers[x][0], (0,0+ (x*boxHeight)))
		box.blit(containers[x][1], (0,50+ (x*boxHeight)))
		box.blit(containers[x][2], (50,0+ (x*boxHeight)))
		box.blit(containers[x][3], (150,0+ (x*boxHeight)))
		box.blit(containers[x][4], (0,0+ (x*boxHeight)))
	if (len(IDArray) > 1):
		screen.blit(backwards, (0,0))
	
	pygame.display.flip()      # flip the screen like in a flipbook
print("Have a great rest of your day!)")