#To run,
# >python rest.py
# From browser: http://localhost:8080/houses

import web
import json

urls = (
    '/houses', 'list_houses',
    '/house/(.*)', 'get_house'
)

app = web.application(urls, globals())

class list_houses:
    def GET(self):
	# output = 'users:[';
	# for child in root:
    #             print 'child', child.tag, child.attrib
    #             output += str(child.attrib) + ','
	# output += ']';
        # return output
        return '{"something":"houses"}'

class get_house:
    def GET(self, user):
	# for child in root:
	# 	if child.attrib['id'] == user:
	# 	    return str(child.attrib)
        return '{"something":"house"}'

if __name__ == "__main__":
    app.run()
