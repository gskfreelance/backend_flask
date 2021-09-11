import sys

from bson.objectid import ObjectId
from flask import current_app as app
from flask_pymongo import PyMongo
from pymongo import MongoClient


class MongoDB:
    def __init__(self):
        self.log = app.config["log"]
        self.db_config()
        self.connect()

    def connect(self):
        self.mongo = PyMongo(app)

    def db_config(self):
        host = app.config["DB_HOST"]
        # port = app.config["DB_PORT"]
        dbname = app.config["DB_NAME"]
        username = app.config["DB_USER"]
        # password = urllib.parse.quote_plus(os.environ.get("MONGODB_PASSWORD")) # enable if plain password
        password = app.config["DB_PASSWORD"]  # enable this if  pass has no special symbols
        mongo_uri = f"mongodb+srv://{username}:{password}@{host}/{dbname}?retryWrites=true&w=majority"

        app.config["MONGO_URI"] = mongo_uri
        client = MongoClient(mongo_uri)

        try:
            client.server_info()
            self.log.debug("Database connected successfully")
        except Exception as e:
            self.log.error(
                f"MongoDB Connection Error : {e}"
            )
            sys.exit(1)
        finally:
            client.close()

    def find(self, collection, condition=None):
        self.log.info(f"Find {condition} from {collection} collection.")
        if condition:
            try:
                data = self.mongo.db[collection].find(condition)
            except Exception as e:
                self.log.error(f"{e}")
                data = f"No collection found with {collection}"
        else:
            data = self.mongo.db[collection].find()

        results = self.mongo_id_to_str(data)

        return results

    def find_by_id(self, collection, _id):
        results = None
        self.log.info(f"Find by _id {_id} from {collection}")
        if _id:
            try:
                results = self.mongo.db[collection].find_one({"_id": ObjectId(_id)})
                results["_id"] = str(results["_id"])
            except Exception as e:
                self.log.error(f"Something went wrong. Error: {e}")
        else:
            results = self.mongo.db[collection].find()

        return results

    def save(self, collection, obj):
        """
        Takes data obj as input and returns the _id after saving
        """
        self.log.info(f"Insert {obj} into {collection}")
        _id = self.mongo.db[collection].insert_one(obj).inserted_id
        result = self.find_by_id(collection, _id)

        if result:
            result["_id"] = str(result["_id"])

        return result

    def update(self, collection, _id, obj):
        """
        Updates the object based on _id
        Output: (error, message or obj)
        """
        obj = self.remove_empty_keys(obj)
        self.log.info(f"Update {obj} into {collection} by {_id}")
        if _id:
            try:
                inserted_id = self.mongo.db[collection].update_one(
                    {"_id": ObjectId(_id)}, obj
                )
                result = (True, self.find_by_id(collection, _id))
            except Exception as e:
                self.log.error(f"ID is not valid. err: {e}")
                result = (False, f"{e}")

            return result
        else:
            return False, "_id is required"

    def delete(self, collection, _id):
        self.log.info(f"Delete from {collection} by {_id}")
        try:
            self.mongo.db[collection].delete_one({"_id": ObjectId(_id)})
            return True, "Delete Successfully"
        except Exception as e:
            self.log.error(f"Document not deleted using {_id}. err: {e}")
            return False, f"Error in Deleting document using {_id}"

    def remove_empty_keys(self, obj):
        """
        Input: Take an object with key, values
        Ouput: Returns the object by removing keys which has no values
        """
        new_obj = {}
        new_obj["$set"] = {k: v for k, v in obj["$set"].items() if v != ""}
        return new_obj

    def mongo_id_to_str(self, data):
        results = []
        if type(data) == str:
            return False

        for document in data:
            document["_id"] = str(document["_id"])
            results.append(document)

        return results
