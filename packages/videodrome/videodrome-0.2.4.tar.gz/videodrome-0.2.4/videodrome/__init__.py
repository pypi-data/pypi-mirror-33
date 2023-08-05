import os, sys
import json
import generate

APP="Videodrome"
APP_PATH = os.path.dirname(os.path.realpath(__file__))

def test():
	print "Videodrome!"
	# generate.generateIndexPages(sys.argv[2], "", 0)
	# generate.generateIndexPages(APP_PATH + "/videos/", 0)
	# call(None, json.dumps({'command':sys.argv[1], 'path':sys.argv[2]}));
	print "done!"

def call(ws, json_string):
	parsed_json = json.loads(json_string)
	command = parsed_json['command']
	print "command:", command
	if command == "ping":
		json_send = {"command":"pong"}
		ws.write_message(json_send)
	elif command == "generate":
		print parsed_json['path']
		generate.generateIndexPages(parsed_json['path'], 1)
		