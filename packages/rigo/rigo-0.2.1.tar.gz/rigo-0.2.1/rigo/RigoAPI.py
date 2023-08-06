"""
Rigo Remote Database Service (RRDS) - port 7737

  - Rigo v0.2 Python database
  - Flask web framework

 (c) 2018. Monty Dimkpa. All Rights Reserved.

"""

from flask import Flask, Response, request, redirect
from flask_restful import Resource, Api
from flask_cors import CORS
from collections import OrderedDict
from rigo import *

app = Flask(__name__)
CORS(app)

global dbs

try:
    dbs = ReadDBCache()
except:
    dbs = dbs

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

def message_formatter(code,message,data={}):
    if data != {}:
        msg = OrderedDict();
        msg["code"] = code;
        msg["message"] = message;
        msg["data"] = data;
        return Response(json.dumps(msg), status=code, mimetype='application/json')
    else:
        msg = OrderedDict();
        msg["code"] = code;
        msg["message"] = message;
        return Response(json.dumps(msg), status=code, mimetype='application/json')

# Execution Wrapper
def Execute(command,options={}):
    start = datetime.datetime.today()
    dbmessage = RigoDB(command,options)
    duration = (datetime.datetime.today() - start).seconds
    if command == "view_entries":
        dbmessage = uniform_dataset(dbmessage)
        return message_formatter(200,"Query OK. [lasted: %ds]" % duration, dbmessage)
    else:
        return message_formatter(200,"%s [lasted: %ds]" % (dbmessage,duration))


class CreateDatabase(Resource):
    def get(self):
        command = "new_database";
        options = {};
        options["dbname"] = request.args.get("dbname");
        options["dbpassword"] = request.args.get("dbpassword");
        if "None" in map(str,[options[x] for x in options]):
            return message_formatter(400,"error: please provide non-null arguments")
        else:
            return Execute(command,options)

class AddTable(Resource):
    def get(self):
        command = "add_table";
        options = {};
        options["dbname"] = request.args.get("dbname");
        options["dbpassword"] = request.args.get("dbpassword");
        options["tablename"] = request.args.get("tablename");
        if "None" in map(str,[options[x] for x in options]):
            return message_formatter(400,"error: please provide non-null arguments")
        else:
            return Execute(command,options)

class NewEntry(Resource):
    def post(self):
        command = "new_entry";
        options = request.get_json(force=True);
        try:
            test = eval(options["entry"]);
        except:
            return message_formatter(400,"error: please check your [entry] argument. Should be JSON")
        if "None" in map(str,[options[x] for x in options]):
            return message_formatter(400,"error: please provide non-null arguments")
        else:
            return Execute(command,options)

class ViewEntries(Resource):
    def get(self):
        command = "view_entries";
        options = {};
        options["dbname"] = request.args.get("dbname");
        options["dbpassword"] = request.args.get("dbpassword");
        options["tablename"] = request.args.get("tablename");
        try:
            options["entryPos"] = eval(request.args.get("entryPos"));
        except:
            return message_formatter(400,"error: please check your [entryPos] argument. Should be List or *")
        if "None" in map(str,[options[x] for x in options]):
            return message_formatter(400,"error: please provide non-null arguments")
        else:
            return Execute(command,options)

class EditEntry(Resource):
    def post(self):
        command = "edit_entry";
        options = request.get_json(force=True);
        try:
            test = eval(options["entryPos"]);
            test = eval(options["new"]);
        except:
            return message_formatter(400,"error: please check your [entryPos,new] arguments. Should be [Integer,JSON] respectively")
        if "None" in map(str,[options[x] for x in options]):
            return message_formatter(400,"error: please provide non-null arguments")
        else:
            return Execute(command,options)

class DeleteEntry(Resource):
    def get(self):
        command = "delete_entry";
        options = {};
        options["dbname"] = request.args.get("dbname");
        options["dbpassword"] = request.args.get("dbpassword");
        options["tablename"] = request.args.get("tablename");
        try:
            options["entryPos"] = eval(request.args.get("entryPos"));
        except:
            return message_formatter(400,"error: please check your [entryPos] argument. Should be Integer.")
        if "None" in map(str,[options[x] for x in options]):
            return message_formatter(400,"error: please provide non-null arguments")
        else:
            return Execute(command,options)

class DeleteTable(Resource):
    def get(self):
        command = "delete_table";
        options = {};
        options["dbname"] = request.args.get("dbname");
        options["dbpassword"] = request.args.get("dbpassword");
        options["tablename"] = request.args.get("tablename");
        if "None" in map(str,[options[x] for x in options]):
            return message_formatter(400,"error: please provide non-null arguments")
        else:
            return Execute(command,options)

class DeleteDatabase(Resource):
    def get(self):
        command = "delete_database";
        options = {};
        options["dbname"] = request.args.get("dbname");
        options["dbpassword"] = request.args.get("dbpassword");
        if "None" in map(str,[options[x] for x in options]):
            return message_formatter(400,"error: please provide non-null arguments")
        else:
            return Execute(command,options)

api = Api(app)

api.add_resource(CreateDatabase,'/rigo-remote/create-db')
api.add_resource(AddTable,'/rigo-remote/add-table')
api.add_resource(NewEntry,'/rigo-remote/new-entry')
api.add_resource(ViewEntries,'/rigo-remote/view-entries')
api.add_resource(EditEntry,'/rigo-remote/edit-entry')
api.add_resource(DeleteEntry,'/rigo-remote/delete-entry')
api.add_resource(DeleteTable,'/rigo-remote/delete-table')
api.add_resource(DeleteDatabase,'/rigo-remote/delete-db')

@app.route('/')
def homepage():
    return redirect("https://www.linkedin.com/in/monty-dimkpa-82506538/",code=302)

@app.route('/rigo-remote/')
def homepage2():
    return redirect("https://www.linkedin.com/in/monty-dimkpa-82506538/",code=302)

if __name__ == "__main__":
    app.run(host="172.31.31.146",port=7737)
