#!/usr/bin/python
import requests
import base64
import mysql.connector as mysql
import json

string=''+':api_token'
headers={'Authorization':'Basic '+base64.b64encode(string)}
url='https://www.toggl.com/api/v8/me'
response=requests.get(url,headers=headers)
if response.status_code!=200:
    print "Login failed. Check your API key"
    quit()
response=response.json()

mysqldb_config = {
   'user': 'root',
   'password': 'root',
   'host': 'localhost',
   'database': 'toggl'
}
mysqldb_connection = mysql.connect(**mysqldb_config)

workspaces=response['data']['workspaces']

def workspaceExist(workspacesId, mysqldb_connection):
    """Verify if a workspace exist"""
    cursor = mysqldb_connection.cursor(dictionary=True)
    query = ("SELECT wid, name FROM workspace "
            "WHERE wid = %(id)s")
    queryData = {
      'id': workspacesId
    }
    cursor.execute(query, queryData)
    for row in cursor:
        if row != '':
            return True
        else:
            return False

    cursor.close()


def createWorkspace(workspace, mysqldb_connection):
    """This function create a single workspace"""
    cursor = mysqldb_connection.cursor(dictionary=True)
    oldWorkspace = workspaceExist(workspace['id'],mysqldb_connection)
    if not oldWorkspace:
        addWorkspace = ("INSERT INTO workspace "
                        "(wid, name)"
                        "VALUES (%(id)s, %(name)s)")
        workspaceData = {
        'id': workspace['id'],
        'name': workspace['name'],
        }
        cursor.execute(addWorkspace,workspaceData)
        mysqldb_connection.commit()
        cursor.close()


for workspace in workspaces:
    #projects = requests.get('https://www.toggl.com/api/v8/workspaces/'+str(workspace['id'])+'/projects', headers=headers)
    #projects = projects.json()
    createWorkspace(workspace, mysqldb_connection)
