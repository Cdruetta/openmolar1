# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

import MySQLdb,sys,datetime,os
from xml.dom import minidom
import _version

__version__= "0.1.1"

#--this is a hack to get the correct bzr number. it will always be one up.
__build__= int(_version.version_info.get("revno"))+1

print "Version %s\nRevision No. %s"%(__version__,__build__)

if "win" in sys.platform:
    #-- sorry about this... but cross platform is a goal :(
    cflocation='C:\\Program Files\\openmolar\\openmolar.conf'
    localFileDirectory=os.path.join(os.environ.get("HOMEPATH"),".openmolar")
    
elif "linux" in sys.platform:
    #-- linux hurrah!!
    cflocation='/etc/openmolar/openmolar.conf'
    localFileDirectory=os.path.join(os.environ.get("HOME"),".openmolar")
    
else:
    print "unknown system platform - defaulting to settings in /etc/openmolar"
    cflocation='/etc/openmolar/openmolar.conf'
    localFileDirectory=os.path.join(os.environ.get("HOME"),".openmolar")


#updated if correct password is given
successful_login=False

#-- these permissions are for certain admin duties.
permissionsRaised=False
permissionExpire=datetime.datetime.now()

#-- set a base time for forum check
def forumVisited():
    global lastForumVisit
    lastForumVisit=datetime.datetime.now()
forumVisited()

#-- self-explanatory?
about='''<p>
openMolar - open Source dental practice management software.<br />
Version %s  -  Bazaar Revno %s<br />
Copyright (C) 2009  Neil A. Wallace B.Ch.D.<br />
sourcecode available at <a href="http://launchpad.net/openmolar">
"http://launchpad.net/openmolar"</a>.
</p>
Thanks to <a href="http://rfquerin.org">Richard Querin</a>
for the wonderful icon and Logo.'''%(__version__,__build__)

license='''<hr />
<p>
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
<br />
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
<br />
You should have received a copy of the GNU General Public License
along with this program.
If not, see <a href="http://www.gnu.org/licenses">
http://www.gnu.org/licenses</a>.</p>'''


#-- this variable is used when using DATE_FORMAT from the database
#-- my preference is the UK style dd/mm/YYYY
sqlDateFormat=r"%d/%m/%Y"

#-- undated at login
operator="unknown"
allowed_logins=[]

#-- this list is used for navigating back and forth through the list
recent_snos=[]

#-- update whenever a manual search is made
#-- sname,fname dob... etc
lastsearch=("","","","","","")

#-- used to load combobboxes etc....
activedents=[]
activehygs=[]
clinicianNo=0
clinicianInits=""

earliestStart=datetime.time(8,0)
latestFinish=datetime.time(20,0)


#--this dictionary is upated when this file is initiate -
#--it links dentist keys with practioners
#--eg ops[1]="JJ"
ops={}

#--keys/dents the other way round.
ops_reverse={}
apptix={}
#--this dictionary is upated when this file is initiate -
#--it links appointment keys with practioners
#--eg app[13]="jj"

apptix_reverse={}
referralfile=""
#contains a link to the xml document with the referral info in it -
#--this data will eventually be in the mysql?
stylesheet="resources/style.css"


##TODO - is this obselete now?
descriptions={}
#--treatment codes..

apptTypes=("EXAM","BITE","BT","DOUBLE",
"FAMILY","FILL","FIT","HYG","IMPS","LF","ORTHO",
"PAIN","PREP","RCT","RECEM","REVIEW","SP","TRY","XLA")

#-- default appt font size
appointmentFontSize=8

message=""
dentDict={}

#-- surgery or reception machine?
station="surgery"
#-- openmolar needs to know where it is when calling x-rays
surgeryno=-1

#-- pt's are "private, independent, NHS etc...."
csetypes=["P","I","N","N OR","N O"]


#--for debugging purposes... set this to true.- not yet implemented throughout.
logqueries=False
#-- self evident
practiceAddress=("The Academy Dental Practice","19 Union Street",
"Inverness","IV1 1PP")

#--localsettings.defaultNewPatientDetails=(pt.sname,
#--pt.addr1,pt.addr2,pt.addr3,pt.town,
#--pt.county,pt.pcde,pt.tel1)
defaultNewPatientDetails=("",)*8

#-- these gets initiated
privateFees={}
nhsFees={}
treatmentCodes={}
#itemCodes=[]

#-- 1 less dialog box for these lucky people
defaultPrinterforGP17=True


#-- my own class of excpetion, for when a serialno is called
#--from the database and no match is found
class PatientNotFoundError(Exception):
    pass

def curTime():        #self.estimates = cursor.fetchall()
    return datetime.datetime.today()   #(2009, 3, 7, 18, 56, 37, 582484)

def ukToday():
    d=datetime.datetime.today()   #(2009, 3, 7, 18, 56, 37, 582484)
    return "%02d/%02d/%04d"%(d.day,d.month,d.year)
def sqlToday():
    '''returns today in sql compatible format'''
    t=curTime()
    return "%04d%02d%02d"%(t.year,t.month,t.day)
def pyDatetoSQL(d):
    return "%04d%02d%02d"%(d.year,d.month,d.day)
    
def formatMoney(m):
    '''takes an integer, returns "7.30"'''
    try:
        return "%d.%02d"%(m/100,m%100)
    except:
        return "???"

def GP17formatDate(d):
    if d=="" or d==None:
        return" "*8
    else:
        return d.replace("/","") #"%02d%02d%04d"%(d.day,d.month,d.year)

def dayName(d):
    '''
    expects a datetime object, returns the day
    '''
    try:
        return ("Monday","Tuesday","Wednesday","Thursday",
        "Friday","Saturday","Sunday")[d.isoweekday()]
    except:
        pass

def monthName(d):
    '''
    expects a datetime object, returns the month
    '''
    try:
        return("","January","February","March","April","May","June","July",
        "August","September","October","November","December")[d.month]
    except:
        pass

def longDate(d):
    try:
        return "%s, %d %s %d"%(dayName(d),d.day,monthName(d),d.year)
    except:
        pass

def formatDate(d):
    '''takes a date, returns a uk type date string'''
    try:
        retarg= "%02d/%02d/%d"%(d.day,d.month,d.year)
    except Exception,e:
        print "uable convert date to uk format - will return ",e
        retarg="no date"
    return retarg
def uk_to_sqlDate(d):
    '''reverses the above'''
    try:
        ds=d.split("/")
        retarg="%04d%02d%02d"%(int(ds[2]),int(ds[1]),int(ds[0]))
    except Exception,e:
        print "incorrect uk date, %s returning None"%d,e
        retarg=None
    return retarg

def wystimeToHumanTime(t):
    '''converts a time in the format of 0830 or 1420 to "HH:MM" (string)'''
    try:
        hour,min=int(t)//100,int(t)%100
        return "%d:%02d"%(hour,min)
    except:
        return None
def humanTimetoWystime(t):
    try:
        t=t.replace(":","")
        return int(t)
    except:
        return None
def minutesPastMidnighttoWystime(t):
    '''
    converts minutes past midnight(int) to format HHMM  (integer)
    '''
    hour,min=t//60,int(t)%60
    return hour*100+min
def minutesPastMidnight(t):
    '''
    converts a time in the format of 0830 or 1420
    to minutes past midnight (integer)
    '''
    hour,min=int(t)//100,int(t)%100
    return hour*60+min
def humanTime(t):
    '''converts minutes past midnight(int) to format 'HH:MM' (string)'''
    hour,min=t//60,int(t)%60
    return "%s:%02d"%(hour,min)

def setlogqueries():
    global logqueries
    logqueries=True

def setOperator(u1, u2):
    global operator, clinicianNo, clinicianInits
    if u2 == "":
        operator = u1
    else:
        operator = "%s/%s"%(u1, u2)
    if u1 in activedents+activehygs:
        clinicianNo = ops_reverse.get(u1)
        clinicianInits = u1
    else:
        print "no clinician!"

def getLocalSettings():
    '''
    check for a local settings file (which has preferences etc...
    and "knows" it's surgery number etc...
    if one doesn't exist... knock one up.
    '''
    global surgeryno
    if not os.path.exists(localFileDirectory):
        os.mkdir(localFileDirectory)

    localSets=os.path.join(localFileDirectory,"localsettings.conf")
    if os.path.exists(localSets):
        print "local user level settings file found...."
        dom=minidom.parse(localSets)
        node=dom.getElementsByTagName("surgeryno")
        if node and node[0].hasChildNodes():
            surgeryno=int(node[0].firstChild.data)
            print station
        else: 
            print "unknown"
    else:
        #-- no file found..
        #--so create a settings file.
        f=open(localSets,"w")
        f.write('''<?xml version="1.0" ?>
        <settings><version>1.0</version></settings>
        ''')
        f.close()

def updateLocalSettings(setting,value):
    '''
    adds or updates node "setting" with text value "value"
    '''
    try:
        localSets=os.path.join(localFileDirectory,"localsettings.conf")
        print "updating local settings... %s = %s"%(setting,value)
        if os.path.exists(localSets):
            dom=minidom.parse(localSets)
            print dom.toxml()
            nodeToChange=dom.getElementsByTagName(setting)
            if len(nodeToChange)==0:
                print "no %s node - creating node"%setting
                nodeToChange=dom.createElement(setting)
                print "node created",nodeToChange
                dom.firstChild.appendChild(nodeToChange)
            #--remove any existing values
            else:
                if nodeToChange[0].firstChild.data==value:
                    print "setting unchanged"
                    return
            for children in nodeToChange.childNodes:
                nodeToChange.removeChild(children)
            valueNode=dom.createTextNode(value)
            nodeToChange.appendChild(valueNode)
            print dom.toxml()
            f=open(localSets,"w")
            f.write(dom.toxml())
            f.close()            
            return True
    except Exception,e:
        print "error updating local settings file",e
        return False
    
def initiate(debug=False):
    print "initiating settings"
    global referralfile,stylesheet,fees,message,dentDict,privateFees,\
    nhsFees,allowed_logins,ops,ops_reverse,activedents,activehygs,apptix,\
    apptix_reverse #,itemCodes
    from openmolar.connect import connect
    from openmolar.settings import fee_keys
    from openmolar.dbtools import feesTable
    db=connect()
    cursor = db.cursor()
    #set up four lists with key/value pairs reversedto make for easy referencing

    #first"ops" which is all practitioners
    ops={}
    ops_reverse={}
    apptix_reverse={}
    cursor.execute("select id,inits,apptix from practitioners")
    practitioners = cursor.fetchall()
    for practitioner in practitioners:
        if practitioner[1]!=None:
            ops[practitioner[0]]=practitioner[1]
            ops_reverse[practitioner[1]]=practitioner[0]
            if practitioner[2]!=0:
                apptix_reverse[practitioner[2]]=practitioner[1]
        else:
            ops[0]="NONE"
            ops_reverse["NONE"]=0

    try:
        ##correspondence details for NHS forms
        query="select id,inits,name,formalname,fpcno,quals "
        query+="from practitioners where flag0=1"
        if logqueries:
            print query
        cursor.execute(query)
        practitioners = cursor.fetchall()
        dentDict={}
        for practitioner in practitioners:
            dentDict[practitioner[0]]=practitioner[1:]

        #now get only practitioners who have an active daybook
        query="select apptix,inits from practitioners where flag3=1"
        if logqueries:
            print query
        cursor.execute(query)
        practitioners = cursor.fetchall()
        apptix={}
        for practitioner in practitioners:
            if practitioner[0] != 0 and practitioner[0] != None: #apptix
                apptix[practitioner[1]]=practitioner[0]
        cursor.execute(
        "select inits from practitioners where flag3=1 and flag0=1")
        #dentists where appts active
        activedents=[]
        practitioners = cursor.fetchall()
        for practitioner in practitioners:
            activedents.append(practitioner[0])
        cursor.execute(
        "select inits from practitioners where flag3=1 and flag0=0")
        #hygenists where appts active
        practitioners = cursor.fetchall()
        activehygs=[]
        for practitioner in practitioners:
            activehygs.append(practitioner[0])
    except:
        print "error loading practitioners"

    try:
        cursor.execute("select id from opid")
        #grab initials of those currently allowed to log in
        trows = cursor.fetchall()
        allowed_logins=[]
        for row in trows:
            allowed_logins.append(row[0])
    except Exception,e:
        print "error loading from opid",e


    #-- majorly important dictionary being created.
    #-- the keys are treatment codes form NHS scotland
    #-- the values are a custom data class in the fee_keys module

    try:   #this breaks compatibility with the old database schema
        query="select code, description, pfa, USERCODE,"
        query+="description1, regulation from newfeetable"
        if logqueries:
            print query
        cursor.execute(query)
        rows=cursor.fetchall()
        privateFees={}
        for row in rows:
            code=row[0]
            #itemCodes.append(code)
            usercode=row[3]
            if code!="":
                if privateFees.has_key(code):
                    privateFees[code].addFee(row[2])
                else:
                    newFee=fee_keys.fee()
                    newFee.description=row[4]
                    newFee.setRegulations(row[5])
                    newFee.addFee(row[2])
                    privateFees[code]=newFee

                    descriptions[code]=row[1]

            if usercode!="" and usercode!=None:
                treatmentCodes[usercode]=code

    except Exception,e:
        print "error loading privateFees Dict from newfeetable",e


    try:   #this breaks compatibility with the old database schema
        query="select code, description, NF08, USERCODE,"
        query+="description1, regulation, NF08_pt from newfeetable"
        if logqueries:
            print query
        cursor.execute(query)
        rows=cursor.fetchall()
        nhsFees={}
        for row in rows:
            code=row[0]
            usercode=row[3]
            if code!="":
                if nhsFees.has_key(code):
                    nhsFees[code].addFee(row[2])
                    nhsFees[code].addPtFee(row[6])
                else:
                    newFee=fee_keys.fee()
                    newFee.description=row[4]
                    newFee.setRegulations(row[5])
                    newFee.addFee(row[2])
                    newFee.addPtFee(row[6])
                    nhsFees[code]=newFee

    except Exception,e:
        print "error loading nhs Fees Dict from newfeetable",e

    getLocalSettings()

    wkdir=os.getcwd()
    referralfile=os.path.join (wkdir,"resources","referral_data.xml")

    message='''<html><head><link rel="stylesheet" href="%s" type="text/css">
    </head><body><div align="center">
    <img src="html/images/newlogo.png" width="150",height="100", align="left" />

    <img src="html/images/newlogo.png" width="150",height="100", align="right" />
    <h1>Welcome to OpenMolar!</h1><ul><li>Version %s</li><li>Revision %s</li></ul>
    <p>Your Data is Accessible, and the server reports no issues.</p>
    <p>Have a great day!</p></div></body></html>'''%(stylesheet,__version__,__build__)

    if debug:
        #print formatMoney(1150)
        print "ops = ",ops
        print "ops_reverse = ",ops_reverse
        print "apptix = ",apptix
        print "apptix_reverse = ",apptix_reverse
        print "activedents =",activedents
        print "activehygs=",activehygs
        print "allowed logins=",allowed_logins
        print stylesheet
        print referralfile
        #print curTime()
        #print sqlToday()
        #print dentDict
        #print descripŕtions
        
        #for key in privateFees.keys():
        #    print privateFees[key].fees,
        #    print nhsFees[key].fees
        #print treatmentCodes
        #print fees

if __name__ == "__main__":
    '''testing only'''
    sys.path.append("/home/neil/openmolar/openmolar")
    #print cflocation
    initiate(True)
    updateLocalSettings("stationID","surgery3")
    