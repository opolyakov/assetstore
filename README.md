# assetstore

store.py program is written on Python 2 and dependent on Flask

Prerequisites:
For RHEL/CentOS run:

sudo yum install -y python2-pip
sudo pip install flask

To start program run

sh bootstrap.sh

Program listens on any IP address and port 8000.
Permanent store is asset_store.json file. It would be created if doesn't
exist or empty.

Adding data with POST (user admin in X-User header) - examples :

curl -S -X POST -H "Content-Type: application/json" -H "X-User: admin" -d '{
"SAT-AAF_576": { "class": "rapideye", "type": "satellite" }}
' http://127.0.0.1:8000/store

curl -S -X POST -H "Content-Type: application/json" -H "X-User: admin" -d '{
"SAT-lkj_555": { "class": "dove", "type": "satellite" }}
' http://127.0.0.1:8000/store

curl -X POST -H "Content-Type: application/json" -H "X-User: admin" -d '{
"arty569": { "class": "yagi", "type": "antenna", "details": { "gain": 10.5}},
"artsd36": { "class": "dish", "type": "antenna", "details": 
{ "diameter":2, "radome":false }}}'  http://127.0.0.1:8000/store

It is possible to add multiple entries at once.
If one of entry has an error another would be added anyway.
There are multiple checks on correctness which should prevent to add wrong data.
Integer numbers will be converted to float numbers.
Asset names are unique and are checked against length limits, character types etc. 
After each update permanent store would be rewritten.

Query examples - any user can send a query:

Gives all data:

curl  'http://192.168.1.21:8000/store'

Filter out entry by name (if there other parameters they would be ignored):

curl  'http://127.0.0.1:8000/store?name=arty569'

Filter out data by aset type:

curl -s 'http://127.0.0.1:8000/store?type=antenna'

Filter out data by asset class:

curl -s 'http://127.0.0.1:8000/store?class=yagi'

Filters could be combined to narrow down search:

curl -s 'http://127.0.0.1:8000/store?type=antenna&class=yagi'


