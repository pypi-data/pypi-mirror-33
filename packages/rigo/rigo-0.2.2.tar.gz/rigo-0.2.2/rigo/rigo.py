#!/usr/bin/env python2

"""
Rigo: A Lightweight Database Application for Python2
(c) 2018. Monty Dimkpa. All Rights Reserved.
"""

import datetime,json,os,cPickle

global dbs

IO_Toolkit = {"serialize":{0:json.dumps,1:cPickle.dumps},"deserialize":{0:json.loads,1:cPickle.loads}}

dbm = os.getcwd()+'/rigo.cache'

def ReadFile(f,deserializer_id):
    process = open(f,'rb+')
    s = process.read()
    process.close()
    return IO_Toolkit["deserialize"][deserializer_id](s)

def UpdateFile(f,k,serializer_id):
    process = open(f,'wb+')
    process.write(IO_Toolkit["serialize"][serializer_id](k))
    process.close()
    return "OK"

def ReadDBCache():
    return ReadFile(dbm,1)

def UpdateDBCache(dbs):
    UpdateFile(dbm,dbs,1)

def timestamp():
    return datetime.datetime.today()

def uniform_dataset(discontiguous_data_list):
    field_pool = []; uniform_data = {}
    for record in discontiguous_data_list:
        fields = record.keys()
        new_fields = set(fields).difference(set(field_pool))
        old_fields = set(fields).intersection(set(field_pool))
        for field in new_fields:
            field_pool.append(field)
            uniform_data[field] = [record[field]]
        for field in old_fields:
            uniform_data[field].append(record[field])
    return uniform_data

def join(table_list,join_field,join_values,ranged=False,grouped=False):

    def predicate():
        if ranged:
            return "range"
        else:
            return "item"

    def meetsCondition(subject,object,predicate):
        if predicate == "item":
            return subject in object
        elif predicate == "range":
            min_ = min(object)
            max_ = max(object)
            return bool(subject>=min_ and subject<=max_)
        else:
            return False

    joined_table = []
    for table in table_list:
        try:
            dbname,tablename = table.split('.')
            table_data = ReadDBCache()[dbname].Tables[tablename];
            for row in [row for row in [row for row in table_data if join_field in row] if meetsCondition(row[join_field],join_values,predicate())]:
                joined_table.append(row)
        except:
            pass
    if grouped:
        return uniform_dataset(joined_table)
    else:
        return joined_table

def safely_evaluate(options):
    safe_copy = {}
    for key in options:
        safe_copy[str(key).lower()] = options[key]
    return safe_copy, safe_copy.keys()

def allTables():
    tabs = []; dbs = ReadDBCache();
    for db in dbs:
        for tab in dbs[db].Tables:
            tabs.append(tab)
    return tabs

class Rigo:
    def __init__(self,name,password):
        self.name = name;
        self.password = password;
        self.Tables = {};
        self.entries = {};
        self.created = timestamp();
        self.createdTime = {};
        self.deletedTime = {};
        self.editHistory = {};

    def newTable(self,tableName,password):
        if password != self.password:
            return "DBAccessError: could not connect to database [bad password]"
        tableName = str(tableName).lower()
        if tableName in ["","none"]:
            return "CreateTableError: bad table name: %s" % tableName.upper()
        else:
            if tableName in self.Tables:
                return "CreateTableError: duplicate table name: %s" % tableName.upper()
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

    def viewEntries(self,tableName,entry_pos,password):
        if password != self.password:
            return "DBAccessError: could not connect to database [bad password]"
        proposed = str(tableName).lower()
        master = map(lambda x:str(x).lower(), self.Tables.keys())
        if proposed not in master:
            return "ReadTableError: no such table: %s" % tableName.upper()
        else:
            if 'list' not in str(type(entry_pos)) and entry_pos != "*":
                return "ReadTableError: invalid selection. Use list or *"
            else:
                if entry_pos == "*":
                    return self.Tables[tableName]
                else:
                    selection = [];
                    for index in entry_pos:
                        try:
                            selection.append(self.Tables[tableName][index])
                        except:
                            return "ReadTableError: row number: %d out of range (max: %d)" % (index,self.entries[tableName])
                    return selection

    def editEntry(self,tableName,entry_pos,new,password):
        if password != self.password:
            return "DBAccessError: could not connect to database [bad password]"
        proposed = str(tableName).lower()
        master = map(lambda x:str(x).lower(), self.Tables.keys())
        if proposed not in master:
            return "EditTableError: no such table: %s" % tableName.upper()
        else:
            if 'int' not in str(type(entry_pos)):
                return "EditTableError: invalid row number"
            else:
                try:
                    if 'dict' not in str(type(new)):
                        return "EditTableError: document format not valid"
                    else:
                        self.Tables[tableName][entry_pos] = new;
                        self.editHistory[tableName].append(timestamp());
                        return "EditTableSuccess: table: %s was updated at row: %d" % (tableName.upper(),entry_pos)
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

    def deleteEntry(self,tableName,entry_pos,password):
        if password != self.password:
            return "DBAccessError: could not connect to database [bad password]"
        proposed = str(tableName).lower()
        master = map(lambda x:str(x).lower(), self.Tables.keys())
        if proposed not in master:
            return "EditTableError: no such table: %s" % tableName.upper()
        else:
            if 'int' not in str(type(entry_pos)):
                return "EditTableError: invalid row number"
            else:
                try:
                    self.Tables[tableName].pop(entry_pos)
                    self.editHistory[tableName].append(timestamp());
                    self.entries[tableName]-=1
                    return "EditTableSuccess: row: %d of table: %s was deleted" % (entry_pos,tableName.upper())
                except:
                    return "EditTableError: row number out of range (max: %d)" % self.entries[tableName]

def RigoDB(command,options={}):
    global dbs
    command = command.lower()
    if command == 'new_database':
        required = ["dbname","dbpassword"]
        options,provided = safely_evaluate(options)
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            dbname = str(options["dbname"])
            dbpassword = str(options["dbpassword"])
            if dbname in ["","none"]:
                return "CreateDBError: bad database name: %s" % dbname.upper()
            if dbpassword in ["","none"]:
                return "CreateDBError: bad database password: %s" % dbpassword.upper()
            if dbname in ReadDBCache():
                    return "CreateDBError: duplicate database name: %s" % dbname.upper()
            else:
                dbs = ReadDBCache()
                dbs[dbname] = Rigo(dbname,dbpassword);
                UpdateDBCache(dbs)
                return "CreateDBSuccess: database: %s was created" % dbname.upper()

    if command == 'delete_database':
        required = ["dbname","dbpassword"]
        options,provided = safely_evaluate(options)
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
        required = ["dbname","dbpassword","tablename"]
        options,provided = safely_evaluate(options)
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            dbname = str(options["dbname"])
            dbpassword = str(options["dbpassword"])
            tablename = str(options["tablename"])
            if tablename in ["","none"]:
                return "CreateTableError: bad table name: %s" % tablename.upper()
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
                            message = dbs[dbname].newTable(tablename,dbpassword)
                            UpdateDBCache(dbs)
                            return message
                except:
                    return "DBAccessError: problem executing your query"

    if command == 'delete_table':
        required = ["dbname","dbpassword","tablename"]
        options,provided = safely_evaluate(options)
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
        options,provided = safely_evaluate(options)
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

    if command == 'view_entries':
        required = ["dbname","dbpassword","tablename","entry_pos"]
        options,provided = safely_evaluate(options)
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            dbname = str(options["dbname"])
            dbpassword = str(options["dbpassword"])
            tablename = str(options["tablename"])
            entry_pos = options["entry_pos"]
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
                            message = dbs[dbname].viewEntries(tablename,entry_pos,dbpassword)
                            UpdateDBCache(dbs)
                            return message
                except:
                    return "DBAccessError: problem executing your query"

    if command == 'edit_entry':
        required = ["dbname","dbpassword","tablename","entry_pos","new"]
        options,provided = safely_evaluate(options)
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            dbname = str(options["dbname"])
            dbpassword = str(options["dbpassword"])
            tablename = str(options["tablename"])
            entry_pos = options["entry_pos"]
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
                            message = dbs[dbname].editEntry(tablename,entry_pos,new,dbpassword)
                            UpdateDBCache(dbs)
                            return message
                except:
                    return "DBAccessError: problem executing your query"

    if command == 'delete_entry':
        required = ["dbname","dbpassword","tablename","entry_pos"]
        options,provided = safely_evaluate(options)
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            dbname = str(options["dbname"])
            dbpassword = str(options["dbpassword"])
            tablename = str(options["tablename"])
            entry_pos = options["entry_pos"]
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
                            message = dbs[dbname].deleteEntry(tablename,entry_pos,dbpassword)
                            UpdateDBCache(dbs)
                            return message
                except:
                    return "DBAccessError: problem executing your query"

    if command == 'last_changed':
        required = ["dbname","dbpassword","tablename"]
        options,provided = safely_evaluate(options)
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
        options,provided = safely_evaluate(options)
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

    if command == 'list_databases':
        return ReadDBCache().keys()

    if command == 'list_tables':
        required = ["dbname","dbpassword"]
        options,provided = safely_evaluate(options)
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
                        return dbs[dbname].Tables.keys()
                except:
                    return "DBAccessError: problem executing your query"

    if command == 'join':
        required = ["targets","join_field","join_values","ranged","grouped","as_table"]
        options,provided = safely_evaluate(options)
        missing = [x for x in required if x not in provided]
        if missing != []:
            return "the following required fields are missing: %s" % str(missing)
        else:
            asTable = options["as_table"]
            ranged = options["ranged"]
            grouped = options["grouped"]
            targets = options["targets"]
            join_field = options["join_field"]
            join_values = options["join_values"]
            try:
                dbname = options["dbname"]
                dbpassword = options["dbpassword"]
                tablename = options["tablename"]
            except:
                pass
            if 'bool' not in str(type(asTable)):
                return "QueryError: [as_table] must be boolean"
            else:
                if asTable:
                    missing = [x for x in ["dbname","dbpassword","tablename"] if x not in provided]
                    if missing != []:
                        return "the following required fields are missing: %s" % str(missing)
                    dbname = options["dbname"]
                    if dbname not in RigoDB("list_databases"):
                        return "QueryError: database [%s] was not found" % dbname.upper()
                    dbpassword = options["dbpassword"]
                    if dbpassword != ReadDBCache()[dbname].password:
                        return "QueryError: password not valid for target database"
                    tablename = options["tablename"]
                    if tablename in ["","none"]:
                        return "QueryError: [tablename] must not be null"
                    if tablename in allTables():
                        return "QueryError: [tablename] must be unique (is duplicate)"
            if 'bool' not in str(type(ranged)):
                return "QueryError: [ranged] must be boolean"
            if 'bool' not in str(type(grouped)):
                return "QueryError: [grouped] must be boolean"
            if 'dict' not in str(type(targets)):
                return "QueryError: [targets] must be JSON"
            if 'list' not in str(type(join_values)):
                return "QueryError: [join_values] must be a list"
            if 'str' not in str(type(join_field)) and 'int' not in str(type(join_field)):
                return "QueryError: [join_field] must be string or integer"
            try:
                target_list = []
                for db in targets:
                    password = targets[db][0]
                    table_list = targets[db][1]
                    if db not in RigoDB("list_databases"):
                        return "QueryError: database: [%s] does not exist" % db.upper()
                    if password != ReadDBCache()[db].password:
                        return "QueryError: password for database: [%s] is incorrect" % db.upper()
                    for table in table_list:
                        if table not in ReadDBCache()[db].Tables:
                            return "QueryError: table: [%s] not found in database: [%s]" % (table.upper(),db.upper())
                        else:
                            target_list.append(db+"."+table)
                try:
                    joined_table = join(target_list,join_field,join_values,ranged=ranged,grouped=grouped)
                    if asTable:
                        RigoDB("add_table",{"dbname":dbname,"dbpassword":dbpassword,"tablename":tablename})
                        if grouped:
                            RigoDB("new_entry",{"dbname":dbname,"dbpassword":dbpassword,"tablename":tablename,"entry":joined_table})
                            return {"info":"join results also saved in table: /%s/%s" % (dbname,tablename),"data":joined_table}
                        else:
                            for row in joined_table:
                                RigoDB("new_entry",{"dbname":dbname,"dbpassword":dbpassword,"tablename":tablename,"entry":row})
                            return {"info":"join results also saved in table: /%s/%s" % (dbname,tablename),"data":joined_table}
                    else:
                        return joined_table
                except:
                    return "JoinError: there was a problem executing your join"
            except:
                return "QueryError: check [targets] structure. Clue: {'db1':['password1',table_list_1],'db2':['password2',table_list_2]}"
