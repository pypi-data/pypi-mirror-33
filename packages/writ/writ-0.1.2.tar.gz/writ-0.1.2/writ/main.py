import sys
import writ.filecreator as file

def selectCommand():
	argLen = len(sys.argv)
	
	try:
		if argLen == 1:
			raise ValueError
		operate = sys.argv[1]
		
		if operate == "list":
		
			file.listTemplates()
			
		elif operate == "peep":
		
			if argLen != 3:
				raise ValueError
			file.printTemplate(sys.argv[2])
			
		elif operate == "create":
		
			if argLen != 4:
				raise ValueError
			file.createFile(sys.argv[2], sys.argv[3])
			
		elif operate == "copy":
		
			if argLen != 4:
				raise ValueError
			file.copyFile(sys.argv[2], sys.argv[3])
			
		elif operate == "delete":
			
			if argLen != 3:
				raise ValueError
			file.deleteTemplate(sys.argv[2])
			
		elif operate == "help":
		
			file.printHelp()
				
		else:
			raise ValueError
			
	except ValueError as err:
		print("Invalid or Improper number of arguments.")
		print("Type: 'writ help' to list commands.")

def main():
	selectCommand()
