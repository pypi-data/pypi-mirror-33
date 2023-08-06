#!/usr/bin/env python2
import datetime,json,os,cPickle
from block_magic.blockmagic_client import *

IO_Toolkit = {"serialize":{0:json.dumps,1:cPickle.dumps},"deserialize":{0:json.loads,1:cPickle.loads}}

dbs = {}
dbm = os.getcwd()+'/db.cache'

def ReadFile(f,deserializer_id):
    process = open(f,'rb+')
    s = process.read()
    process.close()
    return IO_Toolkit["deserialize"][deserializer_id](s)

def UpdateFile(f,k,serializer_id):
    process = open(f,'wb+')
    process.write(IO_Toolkit["serialize"][serializer_id](k))
    process.close()

def ReadDBCache():
    return ReadFile(dbm,1)

def UpdateDBCache(dbs):
    UpdateFile(dbm,dbs,1)

try:
	dbs = ReadDBCache()
except:
	UpdateDBCache(dbs)

def timestamp():
    return datetime.datetime.today()

class LocalDB:
    def __init__(self,name,password):
        self.name = name;
        self.password = password;
        self.Tables = {};
        self.entries = {};
        self.created = timestamp();
        self.createdTime = {};
        self.deletedTime = {};
        self.editHistory = {};

    def newTable(self,tableName,blockName,password):
        if password != self.password:
            return "DBAccessError: could not connect to database [bad password]"
        tableName,blockName = map(lambda x:str(x).lower(), [tableName,blockName])
        if tableName in ["","None"]:
            return "CreateTableError: bad table name: %s" % tableName.upper()
        else:
            if tableName in self.Tables:
                return "CreateTableError: duplicate table name: %s" % tableName.upper()
            else:
                if blockName == "block not found":
                    return "CreateTableError: target block: %s not found" % blockName.upper()
                else:
                    self.Tables[tableName] = [];
                    self.entries[tableName] = -1;
                    self.createdTime[tableName] = timestamp();
                    self.editHistory[tableName] = [];
                    return "CreateTableSuccess: table: %s was created" % tableName.upper()

    def deleteTable(self,tableName,password):
        if password != self.password:
            return "DBAccessError: could not connect to database [bad password]"
        proposed = str(tableName).lower()
        master = map(lambda x:str(x).lower(), self.Tables.keys())
        if proposed in master:
            self.deletedTime[proposed] = timestamp()
            del self.Tables[proposed]
            return "DeleteTableSuccess: table: %s was deleted" % tableName.upper()
        else:
            return "DeleteTableError: no such table: %s" % tableName.upper()

    def newEntry(self,tableName,entry,password):
        if password != self.password:
            return "DBAccessError: could not connect to database [bad password]"
        proposed = str(tableName).lower()
        master = map(lambda x:str(x).lower(), self.Tables.keys())
        if proposed not in master:
            return "WriteTableError: no such table: %s" % tableName.upper()
        else:
            if 'dict' not in str(type(entry)):
                return "WriteTableError: document format not valid"
            else:
                self.entries[tableName]+=1;
                self.editHistory[tableName].append(timestamp());
                self.Tables[tableName].append(entry);
                return "WriteTableSuccess: table: %s  was updated" % tableName.upper()

    def viewEntry(self,tableName,entryPos,password):
        if password != self.password:
            return "DBAccessError: could not connect to database [bad password]"
        proposed = str(tableName).lower()
        master = map(lambda x:str(x).lower(), self.Tables.keys())
        if proposed not in master:
            return "ReadTableError: no such table: %s" % tableName.upper()
        else:
            if 'int' not in str(type(entryPos)):
                return "ReadTableError: invalid row number"
            else:
                try:
                    return self.Tables[tableName][entryPos]
                except:
                    return "ReadTableError: row number out of range (max: %d)" % self.entries[tableName]

    def editEntry(self,tableName,entryPos,new,password):
        if password != self.password:
            return "DBAccessError: could not connect to database [bad password]"
        proposed = str(tableName).lower()
        master = map(lambda x:str(x).lower(), self.Tables.keys())
        if proposed not in master:
            return "EditTableError: no such table: %s" % tableName.upper()
        else:
            if 'int' not in str(type(entryPos)):
                return "EditTableError: invalid row number"
            else:
                try:
                    if 'dict' not in str(type(new)):
                        return "EditTableError: document format not valid"
                    else:
                        self.Tables[tableName][entryPos] = new;
                        self.editHistory[tableName].append(timestamp());
                        return "EditTableSuccess: table: %s was updated at row: %d" % (tableName.upper(),entryPos)
                except:
                    return "EditTableError: row number out of range (max: %d)" % self.entries[tableName]

    def lastChanged(self,tableName,password):
        if password != self.password:
            return "DBAccessError: could not connect to database [bad password]"
        proposed = str(tableName).lower()
        master = map(lambda x:str(x).lower(), self.Tables.keys())
        if proposed not in master:
            return "Error: no such table: %s" % tableName.upper()
        else:
            return str(self.editHistory[proposed][-1])

    def rows(self,tableName,password):
        if password != self.password:
            return "DBAccessError: could not connect to database [bad password]"
        proposed = str(tableName).lower()
        master = map(lambda x:str(x).lower(), self.Tables.keys())
        if proposed not in master:
            return "Error: no such table: %s" % tableName.upper()
        else:
            return self.entries[proposed]

    def deleteEntry(self,tableName,entryPos,password):
        if password != self.password:
            return "DBAccessError: could not connect to database [bad password]"
        proposed = str(tableName).lower()
        master = map(lambda x:str(x).lower(), self.Tables.keys())
        if proposed not in master:
            return "EditTableError: no such table: %s" % tableName.upper()
        else:
            if 'int' not in str(type(entryPos)):
                return "EditTableError: invalid row number"
            else:
                try:
                    self.Tables[tableName].pop(entryPos)
                    self.editHistory[tableName].append(timestamp());
                    self.entries[tableName]-=1
                    return "EditTableSuccess: row: %d of table: %s was deleted" % (entryPos,tableName.upper())
                except:
                    return "EditTableError: row number out of range (max: %d)" % self.entries[tableName]

def dbManager(command,options={}):
    command = command.lower()
    if command == 'new_database':
        required = ["dbname","dbpassword"]
        provided = map(lambda x:str(x).lower(), options.keys())
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            dbname = str(options["dbname"])
            dbpassword = str(options["dbpassword"])
            if dbname in ["","None"]:
                return "CreateDBError: bad database name: %s" % dbname.upper()
            if dbpassword in ["","None"]:
                return "CreateDBError: bad database password: %s" % dbpassword.upper()
            if dbname in ReadDBCache():
                    return "CreateDBError: duplicate database name: %s" % dbname.upper()
            else:
                dbs = ReadDBCache()
                dbs[dbname] = LocalDB(dbname,dbpassword);

                UpdateDBCache(dbs)
                return "CreateDBSuccess: database: %s was created" % dbname.upper()

    if command == 'delete_database':
        required = ["dbname","dbpassword"]
        provided = map(lambda x:str(x).lower(), options.keys())
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            dbname = str(options["dbname"])
            dbpassword = str(options["dbpassword"])
            dbs = ReadDBCache()
            if dbname not in dbs:
                return "DBAccessError: could not connect to database [not found]"
            else:
                try:
                    if dbpassword != dbs[dbname].password:
                        return "DBAccessError: could not connect to database [bad password]"
                    else:
                        del dbs[dbname]

                        UpdateDBCache(dbs)
                        return "DBOpSuccess: database %s was deleted" % dbname.upper()
                except:
                    return "DBAccessError: problem executing your query"

    if command == 'add_table':
        required = ["dbname","dbpassword","tablename","blockname"]
        provided = map(lambda x:str(x).lower(), options.keys())
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            dbname = str(options["dbname"])
            dbpassword = str(options["dbpassword"])
            tablename = str(options["tablename"])
            blockname = str(options["blockname"])
            dbs = ReadDBCache()
            if dbname not in dbs:
                return "DBAccessError: could not connect to database [not found]"
            else:
                try:
                    if dbpassword != dbs[dbname].password:
                        return "DBAccessError: could not connect to database [bad password]"
                    else:
                        if tablename in dbs[dbname].Tables:
                            return "TableAccessError: table exists"
                        else:
                            if GetBlockIdentifiers(blockname) == "block not found":
                                return "TableAccessError: target block not found"
                            else:
                                message = dbs[dbname].newTable(tablename,blockname,dbpassword)

                                UpdateDBCache(dbs)
                                return message
                except:
                    return "DBAccessError: problem executing your query"

    if command == 'delete_table':
        required = ["dbname","dbpassword","tablename"]
        provided = map(lambda x:str(x).lower(), options.keys())
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            dbname = str(options["dbname"])
            dbpassword = str(options["dbpassword"])
            tablename = str(options["tablename"])
            dbs = ReadDBCache()
            if dbname not in dbs:
                return "DBAccessError: could not connect to database [not found]"
            else:
                try:
                    if dbpassword != dbs[dbname].password:
                        return "DBAccessError: could not connect to database [bad password]"
                    else:
                        if tablename not in dbs[dbname].Tables:
                            return "TableAccessError: table not found"
                        else:
                            message = dbs[dbname].deleteTable(tablename,dbpassword)

                            UpdateDBCache(dbs)
                            return message
                except:
                    return "DBAccessError: problem executing your query"

    if command == 'new_entry':
        required = ["dbname","dbpassword","tablename","entry"]
        provided = map(lambda x:str(x).lower(), options.keys())
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            dbname = str(options["dbname"])
            dbpassword = str(options["dbpassword"])
            tablename = str(options["tablename"])
            entry = options["entry"]
            dbs = ReadDBCache()
            if dbname not in dbs:
                return "DBAccessError: could not connect to database [not found]"
            else:
                try:
                    if dbpassword != dbs[dbname].password:
                        return "DBAccessError: could not connect to database [bad password]"
                    else:
                        if tablename not in dbs[dbname].Tables:
                            return "TableAccessError: table not found"
                        else:
                            message = dbs[dbname].newEntry(tablename,entry,dbpassword)

                            UpdateDBCache(dbs)
                            return message
                except:
                    return "DBAccessError: problem executing your query"

    if command == 'view_entry':
        required = ["dbname","dbpassword","tablename","entrypos"]
        provided = map(lambda x:str(x).lower(), options.keys())
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            dbname = str(options["dbname"])
            dbpassword = str(options["dbpassword"])
            tablename = str(options["tablename"])
            entryPos = options["entryPos"]
            dbs = ReadDBCache()
            if dbname not in dbs:
                return "DBAccessError: could not connect to database [not found]"
            else:
                try:
                    if dbpassword != dbs[dbname].password:
                        return "DBAccessError: could not connect to database [bad password]"
                    else:
                        if tablename not in dbs[dbname].Tables:
                            return "TableAccessError: table not found"
                        else:
                            message = dbs[dbname].viewEntry(tablename,entryPos,dbpassword)

                            UpdateDBCache(dbs)
                            return message
                except:
                    return "DBAccessError: problem executing your query"

    if command == 'edit_entry':
        required = ["dbname","dbpassword","tablename","entrypos","new"]
        provided = map(lambda x:str(x).lower(), options.keys())
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            dbname = str(options["dbname"])
            dbpassword = str(options["dbpassword"])
            tablename = str(options["tablename"])
            entryPos = options["entryPos"]
            new = options["new"]
            dbs = ReadDBCache()
            if dbname not in dbs:
                return "DBAccessError: could not connect to database [not found]"
            else:
                try:
                    if dbpassword != dbs[dbname].password:
                        return "DBAccessError: could not connect to database [bad password]"
                    else:
                        if tablename not in dbs[dbname].Tables:
                            return "TableAccessError: table not found"
                        else:
                            message = dbs[dbname].editEntry(tablename,entryPos,new,dbpassword)

                            UpdateDBCache(dbs)
                            return message
                except:
                    return "DBAccessError: problem executing your query"

    if command == 'delete_entry':
        required = ["dbname","dbpassword","tablename","entrypos"]
        provided = map(lambda x:str(x).lower(), options.keys())
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            dbname = str(options["dbname"])
            dbpassword = str(options["dbpassword"])
            tablename = str(options["tablename"])
            entryPos = options["entryPos"]
            dbs = ReadDBCache()
            if dbname not in dbs:
                return "DBAccessError: could not connect to database [not found]"
            else:
                try:
                    if dbpassword != dbs[dbname].password:
                        return "DBAccessError: could not connect to database [bad password]"
                    else:
                        if tablename not in dbs[dbname].Tables:
                            return "TableAccessError: table not found"
                        else:
                            message = dbs[dbname].deleteEntry(tablename,entryPos,dbpassword)

                            UpdateDBCache(dbs)
                            return message
                except:
                    return "DBAccessError: problem executing your query"

    if command == 'last_changed':
        required = ["dbname","dbpassword","tablename"]
        provided = map(lambda x:str(x).lower(), options.keys())
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            dbname = str(options["dbname"])
            dbpassword = str(options["dbpassword"])
            tablename = str(options["tablename"])
            dbs = ReadDBCache()
            if dbname not in dbs:
                return "DBAccessError: could not connect to database [not found]"
            else:
                try:
                    if dbpassword != dbs[dbname].password:
                        return "DBAccessError: could not connect to database [bad password]"
                    else:
                        if tablename not in dbs[dbname].Tables:
                            return "TableAccessError: table not found"
                        else:
                            message = dbs[dbname].lastChanged(tablename,dbpassword)

                            UpdateDBCache(dbs)
                            return message
                except:
                    return "DBAccessError: problem executing your query"

    if command == 'row_count':
        required = ["dbname","dbpassword","tablename"]
        provided = map(lambda x:str(x).lower(), options.keys())
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            dbname = str(options["dbname"])
            dbpassword = str(options["dbpassword"])
            tablename = str(options["tablename"])
            dbs = ReadDBCache()
            if dbname not in dbs:
                return "DBAccessError: could not connect to database [not found]"
            else:
                try:
                    if dbpassword != dbs[dbname].password:
                        return "DBAccessError: could not connect to database [bad password]"
                    else:
                        if tablename not in dbs[dbname].Tables:
                            return "TableAccessError: table not found"
                        else:
                            message = dbs[dbname].rows(tablename,dbpassword)

                            UpdateDBCache(dbs)
                            return message
                except:
                    return "DBAccessError: problem executing your query"
