import firebase_admin
import requests
from firebase_admin import db
from traceback import format_exc

from libs.logger import LOGS


def firebase_auth(Var):
    if Var.FIREBASE_SERVICE_ACCOUNT_FILE and Var.FIREBASE_URL:
        if not Var.FIREBASE_SERVICE_ACCOUNT_FILE.startswith(
            "https://"
        ):
            LOGS.error("Firebase Service Account File Link is Wrong!")
            exit()

        service_acc = requests.get(Var.FIREBASE_SERVICE_ACCOUNT_FILE).json()

        try:
            cred = firebase_admin.credentials.Certificate(service_acc)
            firebase_admin.initialize_app(cred, {"databaseURL": Var.FIREBASE_URL})
            return db.reference()
        except BaseException:
            try:
                return db.reference()
            except BaseException:
                LOGS.error(str(format_exc()))
                exit()


class FireDB:
    def __init__(self, Var):
        self.db = firebase_auth(Var)
        if not self.db:
            LOGS.info("Something Went Wrong With FireBase")
            exit()
        
    def getall(self):
        return self.db.get() or {}
    
    @property
    def og(self):
        return self.db

    def create_data(self, path, data):
        return self.db.child(path).set(data)

    def read_data(self, path):
        value = self.db.child(path).get()
        if type(value) == list: # isort: skip
            value = list(filter(lambda item: item is not None, value)) # isort: skip
        return value

    def update_data(self, path, data):
        return self.db.child(path).update(data)
    
    def delete_data(self, path):
        return self.db.child(path).delete()