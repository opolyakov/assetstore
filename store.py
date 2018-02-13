#!/usr/bin/python

from flask import Flask, jsonify, request
import re, json, os

app = Flask(__name__)

datafile = 'asset_store.json'
store = {}

#store['abcd-1'] = { 'type': 'satellite', 'class': 'dove'}
#store['xdfk-56'] = { 'type': 'antenna', 'class': 'dish', 'details': \
#  { 'diameter': 2.2, 'radome': False}}

if not os.path.isfile(datafile) or os.path.getsize(datafile) == 0:
  data_file = open(datafile,"w+")
  data_file.write('{}')
  data_file.close()

with open(datafile) as data_file:
    store = json.load(data_file)


def check_entry(name, data):
  MINLENGTH = 4
  MAXLENGTH = 64
  message = ''

  # check asset name for correctness
  if len(name) < MINLENGTH or len(name) > MAXLENGTH:
    message += "wrong name length. "
  if name[0] == '_' or name[0] == '-':
    message += "Name should not start with '_' or '-'. "
  if re.search(r'[^\w-]',name):
     message += "Name should contain only alphanumeric or '_', '-' characters. "

  if not {'class', 'type'}.issubset(data): 
    message += "Asset type or class is missing. "
    return message

  if data['type'] == 'satellite':
    if data['class'] != 'dove' and  data['class'] != 'rapideye' :
      message += "Wrong satellite class. " 
  elif data['type'] == 'antenna':
    if data['class'] != 'dish' and  data['class'] != 'yagi' :
      message += "Wrong antenna class. " 
  elif data['type'] != 'satellite' and data['type'] != 'antenna':
    message += "Wrong asset type. "

  if data['type'] == 'antenna':
    if 'details' not in data:
      message += "Antenna details are missing. "
      return message
    else:
      if data['class'] == 'yagi':
        if 'gain' not in data['details']:
          message += "Yagi gain is missing. "
          return message
        elif type(data['details']['gain']) == int:
          data['details']['gain'] = float(data['details']['gain'])
        elif type(data['details']['gain']) != float:
          message += "Yagi gain should be float number. "
      elif  data['class'] == 'dish':
        if 'diameter' not in data['details']:
          message += "Dish diameter is missing. "
          return message
        elif type(data['details']['diameter']) == int:
          data['details']['diameter'] = float(data['details']['diameter'])
        elif type(data['details']['diameter']) != float:
          message += "Yagi diameter should be float number. "
        if 'radome' not in data['details']:
          message += "Dish radome is missing. "
          return message
        elif type(data['details']['radome']) != bool:
          message += "Dish radome should be boolean. "

  return message


@app.route('/store')
def get_store():
  filtered = {}
  asset_name = request.args.get('name', default = '*', type = str)
  asset_type = request.args.get('type', default = '*', type = str)
  asset_class = request.args.get('class', default = '*', type = str)

  # filter by asset name, ignore other arguments if any
  if asset_name != '*':
    if asset_name in store:
      filtered[asset_name] = store[asset_name]
  else:
    for name,data in store.items():
      # filter by asset type AND asset class
      if data['type'] == asset_type and data['class'] == asset_class:
        filtered[name] = data
      # filter by asset type OR asset class
      elif (asset_class == '*' and data['type'] == asset_type) \
        or (asset_type == '*' and data['class'] == asset_class):
        filtered[name] = data
  # do not filter
  if asset_name == '*' and asset_type == '*' and asset_class == '*':
    filtered = store
  return jsonify(filtered) 


@app.route('/store', methods=['POST'])
def add_store():
  messages = {}
  output = ''
  if 'X-User' in request.headers:
    if request.headers['X-User'] != 'admin':
      return "Fail: Only admin user allowed to add assets"
  else:
    return "Fail: X-User header is missing"
  content = request.get_json()
  for name,data in content.items():
    messages[name] = check_entry(name, data)
    if messages[name] == '':
      if name not in store:
        store[name] = data
      else:
        messages[name] = "Name should be unique."
  for name, error in messages.items():
    if len(error) > 0:
      output += name + " Fail: " + error + '\n'
    else:
      output += name + " Success\n"

  with open('asset_store.json', 'w') as outfile:
     json.dump(store, outfile, sort_keys = True, indent = 2,
               ensure_ascii = True)
  return output


