#For making requests
import urllib3
#For parsing 
import json
import xml.etree.ElementTree as ET 
import csv
import yaml

#For threading
import multiprocessing
import threading

#For Web Server
import socket
import sys
HOST_NAME = sys.argv[2]
PORT_NUMBER = int(sys.argv[3])

mainPool=False
http = urllib3.PoolManager()
walletsList=[]
threads=[]
#Taking the main token
def register():
    return request('/register')['access_token']

#Mage the GET request to the server and return the body of the request
def request(url='/',token=''):
    response=http.request('GET',sys.argv[1]+url,headers={
        'X-Access-Token':token
    })
    return json.loads(response.data.decode('UTF-8'))

def parseXML(xml):
    list=[]
    root = ET.fromstring(xml)
    for record in root.findall('record'):
        element={}
        for attr in record:
            element[attr.tag]= attr.text
        list.append(element)
    return list

def parseCSV(str):
    response=[]
    reader = csv.reader(str.split('\n'), delimiter=',')
    records=list(reader)
    for row in records[1:-1]:
        element={}
        for (i,attr) in enumerate(row):
            element[records[0][i]]=attr
        response.append(element)
    return response

def writeInFile(save):
    with open('db.json', 'w') as f:
       json.dump(save, f)

def readFromFile():
    with open('db.json', 'r') as content_file:
        return json.loads(content_file.read())

def fetchRoute(route):
    print(route)
    response=request(route,token)
    if 'data' in response:
        try:
            if 'mime_type' in response: 
                if response['mime_type']=='application/xml':
                        writeInFile(parseXML(response['data'])+readFromFile())
                elif response['mime_type']=='text/csv':
                        writeInFile(parseCSV(response['data'])+readFromFile())
                elif response['mime_type']=='application/x-yaml':
                        writeInFile(yaml.load(response['data'])+readFromFile())
            else:
                if isinstance(response['data'],str):
                    data=yaml.load(response['data'])
                else:
                    data=response['data']
                writeInFile(yaml.load(response['data'])+readFromFile())
        except:
            print(route+' error')
   
    if('link' in response):
        for link in response['link']:
            p=multiprocessing.Process(target=fetchRoute,args=[response['link'][link]])
            p.start()






writeInFile([])
token =register()
links=fetchRoute('/home')


serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind((HOST_NAME, PORT_NUMBER))
serv.listen(5)
while True:
    conn, addr = serv.accept()
    from_client = ''
    while True:
        data = conn.recv(4096)
        result=[]
        command=data.decode('UTF-8')
        commands=command.split(' ')
        if not data: break
        print()
        if commands[0]=='SelectColumn':
            users=readFromFile()
            print(commands)
            for user in users:
                if commands[1] in user:
                    if len(commands)==3:
                        if (commands[2] in user[commands[1]]):
                            result.append(user[commands[1]])
                    else:
                        result.append(user[commands[1]])
            send=json.dumps(result).encode('UTF-8')
            # print(send)
            conn.send(send)
        
    conn.close()
    print('client disconnected')
