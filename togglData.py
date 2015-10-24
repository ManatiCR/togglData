#!/usr/bin/python
import requests
import base64
import mysql.connector as mysql
from datetime import datetime
import datetime
import json
import dateutil.parser

#Initial year
initialYear = 0

#API KEY HERE
string = ''+':api_token'
headers = {'Authorization':'Basic '+base64.b64encode(string)}
print base64.b64encode(string)
url = 'https://www.toggl.com/api/v8/me?with_related_data=true'


mysqldb_config = {
   'user': 'root',
   'password': 'root',
   'host': 'localhost',
   'database': 'toggl'
}
mysqldb_connection = mysql.connect(**mysqldb_config)


def isInitialSynchronization(mysqldb_connection):
    """Verify if is the initial Synchronization"""
    cursor = mysqldb_connection.cursor(dictionary=True)
    query = ("SELECT count(teid) as teid_count  FROM time_entry")
    cursor.execute(query)
    for row in cursor:
        if row['teid_count'] != 0:
            return False
        else:
            return True

# Verify if is the First Synchronization to set the initial year.
if isInitialSynchronization(mysqldb_connection):
    flag = False
    while not flag:
        startYear = raw_input('Start year for your initial Synchronization: ')
        try:
            initialYear = int(startYear)
            if len(str(initialYear)) == 4:
                flag = True
            else:
                print 'The format of the year should be YYYY'
        except ValueError:
            print 'Re-enter the year value'

#First request to toggl API
response = requests.get(url,headers=headers)
if response.status_code != 200:
    print "Login failed. Check your API key"
    quit()
response = response.json()
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



def existTimeEntryTag(timeEntryId, tagId, mysqldb_connection):
    """Verify if one time entry is associated with specific tag"""
    cursor = mysqldb_connection.cursor(dictionary=True)
    query = ("SELECT id FROM time_entry_tag WHERE teid=%(teid)s and tid=%(tid)s")
    queryData = {
    'teid': timeEntryId,
    'tid': tagId
    }
    cursor.execute(query, queryData)
    row = cursor.fetchone()
    if row is not None and row != '' :
        return row['id']
    else:
        return False




def createTimeEntryTag(timeEntryTag, mysqldb_connection):
    """Create the association between a time entry and one tag"""
    if not existTimeEntryTag(timeEntryId = timeEntryTag['teid'], tagId = timeEntryTag['tid'], mysqldb_connection= mysqldb_connection):
        cursor =  mysqldb_connection.cursor()
        query = ("INSERT INTO time_entry_tag (teid, tid) "
                 "VALUES(%(teid)s, %(tid)s)")
        cursor.execute(query, timeEntryTag)
        mysqldb_connection.commit()
        cursor.close()


def createTag(tag, mysqldb_connection):
    "create a single tag"
    cursor = mysqldb_connection.cursor()
    query = ("INSERT INTO tag "
            "(name) VALUES(%(name)s)")
    queryValues = {
    'name': tag
    }
    cursor.execute(query, queryValues)
    newTagId = cursor.lastrowid
    mysqldb_connection.commit()
    cursor.close()
    return newTagId


def getTagbyName(tagName, mysqldb_connection):
    "get a single tag by name"
    cursor = mysqldb_connection.cursor(dictionary=True)
    query = ("SELECT tid FROM tag WHERE name LIKE %(name)s")
    queryData = {
    'name': tagName
    }
    cursor.execute(query, queryData)
    row = cursor.fetchone()
    if row is not None and row != '' :
        return row['tid']
    else:
        return False


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

def timeEntryExist(timeEntryId, mysqldb_connection):
    """Verify if a time entry exist"""
    cursor = mysqldb_connection.cursor(dictionary=True)
    query = ("SELECT teid FROM time_entry "
            "WHERE teid = %(teid)s")
    queryData = {
    'teid': timeEntryId
    }
    cursor.execute(query, queryData)
    for row in cursor:
        if row != '':
            cursor.close()
            return True
        else:
            cursor.close()
            return False

def timeEntryUpdated(timeEntry, mysqldb_connection):
    """Verify if an time entry is up to date"""
    cursor = mysqldb_connection.cursor(dictionary=True)
    query = ("SELECT updated FROM time_entry "
            "WHERE teid = %(teid)s")
    queryData = {
    'teid': timeEntry['id']
    }
    cursor.execute(query, queryData)
    row = cursor.fetchone()
    if row is not None:
        if row['updated'] != dateutil.parser.parse(timeEntry['updated'],  ignoretz=True):
            cursor.close()
            return True
    cursor.close()
    return False

def updateTimeEntry(timeEntry, mysqldb_connection):
    """Update a specific timeEntry"""
    cursor = mysqldb_connection.cursor()
    query = ("UPDATE time_entry "
            "SET description=%(description)s, pid=%(pid)s, start_date=%(start_date)s, stop_date=%(stop_date)s, duration=%(duration)s, updated=%(updated)s "
            "WHERE teid=%(teid)s")
    queryData = {
    'teid': timeEntry['id'],
    'pid': timeEntry['pid'],
    'description': timeEntry['description'],
    'start_date': timeEntry['start'],
    'stop_date': timeEntry['end'],
    'duration': timeEntry['dur'],
    'updated': timeEntry['updated'],
    }
    cursor.execute(query, queryData)
    mysqldb_connection.commit()
    cursor.close()


def createTimeEntry(timeEntry, mysqldb_connection):
    """This function create a single TimeEntry"""
    if not timeEntryExist(timeEntry['id'], mysqldb_connection):
        cursor = mysqldb_connection.cursor()
        addTimeEntry = ("INSERT INTO time_entry "
                    "(teid, pid, uid, description, start_date, stop_date, duration, updated)"
                    "VALUES (%(teid)s, %(pid)s, %(uid)s, %(description)s, %(start_date)s, %(stop_date)s, %(duration)s, %(updated)s)")

        if  str(timeEntry['pid']) != 'None' and not projectExist(timeEntry['pid'], mysqldb_connection):
            response = requests.get('https://www.toggl.com/api/v8/projects/' + str(timeEntry['pid']),headers=headers)
            if response.status_code == 200:
                response = response.json()
                createProject(response['data'], mysqldb_connection)
            else:
                print str(response.status_code) + ' status'

        if str(timeEntry['end']) != 'None' and str(timeEntry['start']) != 'None':
            if  userExist(timeEntry['uid'], mysqldb_connection):
                tagsIds = []
                if timeEntry['tags']:
                    for tag in timeEntry['tags']:
                        tagId = getTagbyName(str(tag), mysqldb_connection)
                        if tagId:
                            tagsIds.append(tagId)
                        else:
                            newTagId = createTag(tag=tag, mysqldb_connection=mysqldb_connection)
                            tagsIds.append(newTagId)

                timeEntryData = {
                'teid': timeEntry['id'],
                'pid': timeEntry['pid'],
                'uid': timeEntry['uid'],
                'description': timeEntry['description'],
                'start_date': timeEntry['start'],
                'stop_date': timeEntry['end'],
                'duration': timeEntry['dur'],
                'updated': timeEntry['updated'],
                }
                cursor.execute(addTimeEntry, timeEntryData)
                mysqldb_connection.commit()
                cursor.close()

                # Create the association between time entries and tags
                if tagsIds:
                    for tid in tagsIds:
                        timeEntrytag = {
                        'teid': timeEntry['id'],
                        'tid': tid
                        }
                        createTimeEntryTag(timeEntryTag = timeEntrytag, mysqldb_connection = mysqldb_connection)
            else:
                print 'Ignored time Entry: user ' +  timeEntry['user']
        else:
            print 'No stop or start date defined'
    else:
        if timeEntryUpdated(timeEntry, mysqldb_connection):
            updateTimeEntry(timeEntry, mysqldb_connection)

def initialSynchronization(headers, mysqldb_connection, workspaces, initialYear):
    """Get all the time entries in intervals of one years"""
    now = datetime.datetime.now()
    actualYear = now.year
    for workspace in workspaces:
        print str(workspace['id']) + ' Workspace'
        nextYear = initialYear
        while actualYear + 1 >= nextYear:
            startYear = nextYear
            nextYear = nextYear + 1
            totalPages = 0
            actualPage = 1
            url = 'https://www.toggl.com/reports/api/v2/details?user_agent=toggleData&workspace_id=' + str(workspace['id']) + '&since=' + str(startYear) + '-01-01&until=' + str(nextYear) + '-01-01&page=1'
            response = requests.get(url,headers=headers)
            response = response.json()
            totalPages = int(response['total_count']) / int(response['per_page'])

            if int(response['total_count']) % int(response['per_page']) != 0:
                totalPages = totalPages + 1
            timeEntriesProcesor(mysqldb_connection, response['data'])

            while actualPage <= totalPages:
                actualPage = actualPage + 1
                url = 'https://www.toggl.com/reports/api/v2/details?user_agent=toggleData&workspace_id=' + str(workspace['id']) + '&since=' + str(startYear)+ '-01-01&until=' + str(nextYear) + '-01-01&page=' + str(actualPage)
                response = requests.get(url,headers=headers)
                response = response.json()
                timeEntriesProcesor(mysqldb_connection, response['data'])

def timeEntriesProcesor(mysqldb_connection, timeEntries):
    """Helper to save all the time entries"""
    for timeEntry in timeEntries:
        createTimeEntry(timeEntry, mysqldb_connection)

def continuousSynchronization(headers, mysqldb_connection, workspaces):
    """Handles the continuous Synchronization process"""
    for workspace in workspaces:
        totalPages = 0
        actualPage = 1
        url = 'https://www.toggl.com/reports/api/v2/details?user_agent=toggleData&workspace_id=' + str(workspace['id'])
        response = requests.get(url,headers=headers)
        response = response.json()
        totalPages = int(response['total_count']) / int(response['per_page'])

        if int(response['total_count']) % int(response['per_page']) != 0:
            totalPages = totalPages + 1
        timeEntriesProcesor(mysqldb_connection, response['data'])

        while actualPage <= totalPages:
            actualPage = actualPage + 1
            url = 'https://www.toggl.com/reports/api/v2/details?user_agent=toggleData&workspace_id=' + str(workspace['id']) + '&page=' + str(actualPage)
            response = requests.get(url,headers=headers)
            response = response.json()
            timeEntriesProcesor(mysqldb_connection, response['data'])

for workspace in workspaces:
    # Create a  workspace
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
            if not workspaceExist(user['default_wid'], mysqldb_connection):
                newWorkspace = {
                'id': user['default_wid'],
                'name': user['fullname'] + ' workspace',
                }
                createWorkspace(newWorkspace, mysqldb_connection)
            createUser(user, mysqldb_connection)
    else:
        if usersResponse.status_code == 403:
            usersUrl = 'https://www.toggl.com/api/v8/workspaces/' + str(workspace['id']) + '/workspace_users'
            usersResponse = requests.get(usersUrl, headers=headers)
            if usersResponse.status_code == 200:
                usersResponse = usersResponse.json()
                for user in usersResponse:
                    if user['admin'] == True and not workspaceExist(user['wid'], mysqldb_connection):
                        newWorkspace = {
                        'id': user['wid'],
                        'name': user['name'] + ' workspace',
                        }
                        createWorkspace(newWorkspace, mysqldb_connection)
                    print 'user in exception ' + user['name']
                    newUser = {
                    'id': user['uid'],
                    'default_wid': user['wid'],
                    'fullname': user['name'],
                    }
                    createUser(newUser, mysqldb_connection)



if isInitialSynchronization(mysqldb_connection):
    initialSynchronization(headers, mysqldb_connection, workspaces, initialYear)
else:
    continuousSynchronization(headers, mysqldb_connection, workspaces)
mysqldb_connection.close()

#close the execution of script
exit()
