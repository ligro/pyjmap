from flask import current_app
from pyjmap.database import db, Account
from pyjmap import database, auth

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

    yield ["accounts", [account.toDict() for account in Account.getAccountsByUserId(auth.current_user.id)]]

def setAccounts(ifInState, create, update, destroy):
    """
    Not in the specs, but follow setFoos guidelines.
    """
    # change this
    for resp in _set(Account, ifInState, create, update, destroy):
        yield resp

def _set(className, ifInState, create, update, destroy):
    """
    setFoos method, see specs.
    """
    # TODO handle ifInState
    newState = auth.current_user.getNextState()
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
    for id in create:
        try:
            obj = className()
            obj.data = create[id]
            obj.userId = auth.current_user.id
            obj.save()
            response['created'][id] = obj.toDict()
        except Exception as e:
            current_app.logger.warning(e)
            response['notCreated'][id] = {
                'type': e,
                'description': str(e)
            }

    # update
    for id, data in update:
        try:
            # doesn't work
            obj = className.getById(id, auth.current_user.id)
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
    for id, data in destroy:
        try:
            obj = className.getById(id)
            obj.markAsDeleted(newState)
            obj.save()
            response['destroyed'].push(id)
        except Exception as e:
            current_app.logger.warning(e)
            response['notDestroyed'][id] = {
                'type': e,
                'description': e.message
            }

    database.commit()
    current_app.logger.debug(response)
    yield ['accounts', response]
