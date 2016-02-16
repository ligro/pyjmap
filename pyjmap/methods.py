from flask import current_app
from pyjmap.database import db, Account
from pyjmap import auth

class MethodException(Exception):
    message = None

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class InvalidArguments(MethodException):
    def __init__(self):
        super().__init__('invalidArguments')

# This will contains all methods available in the apis
# always use yield, never return

def getAccounts(sinceState=None):
    if sinceState is not None and type(sinceState) is not str:
        raise InvalidArguments

    current_app.logger.debug(auth.current_user)
    yield ["accounts", Account.getAccountsByUserId(auth.current_user.id)]

def setAccounts(ifInState, create, update, destroy):
    """
    Not in the specs, but follow setFoos guidelines.
    """
    # change this
    for resp in _set('Account', ifInState, create, update, destroy):
        yield resp

def _set(object, ifInState, create, update, destroy):
    """
    setFoos method, see specs.
    """
    # TODO handle ifInState
    newState = current_user.getNextState()
    response = {
        'oldState': None,
        'newState': newState,
        'created': {},
        'updated': [],
        'destroyed': [],
        'notCreated': {},
        'notUpdated': {},
        'notDestroyed': {},
    }
    # create
    for id, data in create:
        try:
            obj = Account()
            obj.setFromArray(data, newState)
            obj.save()
            response['created'][id] = obj.toDict()
        except Exception as e:
            current_app.logger.warning(e)
            response['notCreated'][id] = {
                'type': e,
                'description': e.message
            }

    # update
    for id, data in update:
        try:
            obj = Account.getAccountById(id)
            obj.setFromArray(data, newState)
            obj.save()
            response['updated'].push(id)
        except Exception as e:
            current_app.logger.warning(e)
            response['notUpdated'][id] = {
                'type': e,
                'description': e.message
            }

    # destroy
    for id, data in delete:
        try:
            obj = Account.getAccountById(id)
            obj.markAsDeleted(newState)
            obj.save()
            response['destroyed'].push(id)
        except Exception as e:
            current_app.logger.warning(e)
            response['notDestroyed'][id] = {
                'type': e,
                'description': e.message
            }

    db.commit()
    yield response
