#!/usr/bin/python
import requests
import base64
import mysql.connector as mysql
import json

#API KEY HERE
string = ''+':api_token'
headers = {'Authorization':'Basic '+base64.b64encode(string)}
url = 'https://www.toggl.com/api/v8/me?with_related_data=true'
response = requests.get(url,headers=headers)
if response.status_code != 200:
    print "Login failed. Check your API key"
    quit()
response = response.json()

mysqldb_config = {
   'user': 'root',
   'password': 'root',
   'host': 'localhost',
   'database': 'toggl'
}
mysqldb_connection = mysql.connect(**mysqldb_config)

workspaces = response['data']['workspaces']

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
            cursor.close()
            return True
        else:
            cursor.close()
            return False

def projectExist(projectId, mysqldb_connection):
    """Verify if a project exist"""
    cursor = mysqldb_connection.cursor(dictionary=True)
    query = ("SELECT pid FROM project "
            "WHERE pid = %(pid)s")
    queryData = {
    'pid': projectId
    }
    cursor.execute(query, queryData)
    for row in cursor:
        if row != '':
            cursor.close()
            return True
        else:
            cursor.close()
            return False

def clientExist(clientId, mysqldb_connection):
    """Verify if a client exist"""
    cursor = mysqldb_connection.cursor(dictionary=True)
    query = ("SELECT cid FROM client "
            "WHERE cid = %(cid)s")
    queryData = {
    'cid': clientId
    }
    cursor.execute(query, queryData)
    for row in cursor:
        if row != '':
            cursor.close()
            return True
        else:
            cursor.close()
            return False

def userExist(userId, mysqldb_connection):
    """Verify if a user exist"""
    cursor = mysqldb_connection.cursor(dictionary=True)
    query = ("SELECT uid FROM user "
            "WHERE uid = %(uid)s")
    queryData = {
    'uid': userId
    }
    cursor.execute(query, queryData)
    for row in cursor:
        if row != '':
            cursor.close()
            return True
        else:
            cursor.close()
            return False


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


def createUser(user, mysqldb_connection):
    """This function create a single user"""
    cursor = mysqldb_connection.cursor(dictionary=True)
    if not userExist(user['id'],mysqldb_connection):
        addUser = ("INSERT INTO user "
                        "(uid, default_wid, fullname)"
                        "VALUES (%(uid)s, %(default_wid)s, %(fullname)s)")
        userData = {
        'uid': user['id'],
        'default_wid': user['default_wid'],
        'fullname': user['fullname'],
        }
        cursor.execute(addUser,userData)
        mysqldb_connection.commit()
        cursor.close()

def createProject(project, mysqldb_connection):
    """This function create a single project"""
    cursor = mysqldb_connection.cursor()
    if not projectExist(project['id'], mysqldb_connection):
        addProject = ("INSERT INTO project "
                      "(pid, wid, cid, name)"
                      "VALUES (%(pid)s, %(wid)s, %(cid)s, %(name)s)")
        if not 'cid' in project:
            if not clientExist(0, mysqldb_connection):
                client = {
                'name': 'No Client',
                'id': 0,
                'wid': project['wid'],
                }
                #create the 0 client if not exist
                createClient(client, mysqldb_connection)
            project['cid'] = 0

        projectData = {
        'pid': project['id'],
        'wid': project['wid'],
        'cid': project['cid'],
        'name': project['name'],
        }
        cursor.execute(addProject, projectData)
        mysqldb_connection.commit()
        cursor.close()


def createClient(client, mysqldb_connection):
    """This function create a single client"""
    if not clientExist(client['id'], mysqldb_connection):
        cursor = mysqldb_connection.cursor()
        addClient = ("INSERT INTO client "
                    "(cid, wid, name)"
                    "VALUES (%(cid)s, %(wid)s, %(name)s)")
        clientData = {
        'cid': client['id'],
        'wid': client['wid'],
        'name': client['name'],
        }
        cursor.execute(addClient, clientData)
        mysqldb_connection.commit()
        cursor.close()

for workspace in workspaces:
    # Create a  workspace
    print str(workspace['id']) + workspace['name']
    createWorkspace(workspace, mysqldb_connection)



#create all the clients
if 'clients' in response['data']:
    clients = response['data']['clients']
    for client in clients:
        createClient(client, mysqldb_connection)

#Create all the projects
if 'projects' in response['data']:
    projects = response['data']['projects']
    for project in projects:
        createProject(project, mysqldb_connection)

for workspace in workspaces:
    #get and create the workspace users
    usersUrl = 'https://www.toggl.com/api/v8/workspaces/' + str(workspace['id']) + '/users'
    usersResponse = requests.get(usersUrl, headers=headers)
    if usersResponse.status_code == 200:
        usersResponse = usersResponse.json()
        for user in usersResponse:
            print 'default_wid: ' + str(user['default_wid']) +  ' ' + user['fullname']
            if not workspaceExist(user['default_wid'], mysqldb_connection):
                newWorkspace = {
                'id': user['default_wid'],
                'name': user['fullname'] + ' workspace',
                }
                createWorkspace(newWorkspace, mysqldb_connection)
            createUser(user, mysqldb_connection)
    else:
        print workspace['id']




mysqldb_connection.close()
