from flask import Flask, request, render_template, redirect, url_for
import json
import requests

app = Flask(__name__)

BASE_URL = "http://backend:6000"

@app.route("/")
def index():
    return "XUIXUIXUI"
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
