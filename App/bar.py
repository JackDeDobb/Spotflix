import json
import time
from flask import Flask, request, redirect, g, render_template, Response
import requests
from urllib.parse import quote
from credentials import *
from songScraper import *


@app.route('/progress')
def progress():
	def generate():
		x = 0
		while x <= 100:
			yield "data:" + str(x) + "\n\n"
			x = x + 10
			time.sleep(0.5)
	return Response(generate(), mimetype= 'text/event-stream')
