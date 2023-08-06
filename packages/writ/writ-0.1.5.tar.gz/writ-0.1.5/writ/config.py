import os

procpath = os.path.dirname(os.path.abspath( __file__ ))

helpCmds = [
"",
"create - Create file from template list. ex. 'writ create new.html template.html'",
"copy - Create template from existing file. ex. 'writ copy template.html new.html'",
"list - List files in template directory ex. 'writ list'",
"peep - Print selected template file. ex. 'writ peep template.html'",
"delete - Delete template file. ex. 'writ delete template.html'"
]
