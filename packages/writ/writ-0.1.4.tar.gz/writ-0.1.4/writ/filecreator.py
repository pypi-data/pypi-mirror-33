import os
from writ.config import procpath, helpCmds

def createFile(name, template):
	try:
		with open(procpath + "/templates/" + template) as newText:
			with open(name, 'w+') as newFile:
				newFile.write(newText.read())
	except IOError:
		print(template + " doesn't exist.")
	else:
		print("Created: " + name)
	
def copyFile(filename, newFile):
	try:
		with open(filename) as newText:
			with open(procpath + "/templates/" + newFile, 'w+') as newTemplate:
				newTemplate.write(newText.read())
	except IOError:
		print(filename + " doesn't exist.")
	else:
		print("Copied: " + filename + " as " + newFile)
			
def listTemplates():
	templates = os.listdir(procpath + "/templates")
	for file in templates:
		print(file)
		
def printTemplate(template):
	with open(procpath + "/templates/" + template) as fileSelect:
		print(fileSelect.read())
		
def deleteTemplate(template):
	deletePath = procpath + "/templates/" + template
	if os.path.exists(deletePath):
		if input("Delete " + template + "? y/n ") != "y":
			return
			
		os.remove(deletePath)
		print("Deleted: " + template)
	else:
		print(template + " doesn't exist.")
		
def printHelp():
	for cmd in helpCmds:
		print(cmd)