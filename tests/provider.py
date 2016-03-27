import pyjmap
from pyjmap.database import User, Device, commit

def func_name(depth = 2):
    import traceback
    from pprint import pprint
    return traceback.extract_stack(limit=depth)[0][2]

def user(password = None):
    user = User()
    user.username = func_name(depth=3)

    if not password :
        password = user.username + 'password'

    user.setPassword(password)
    user.save()
    commit()
    return user

def deviceData(username):
    return {
        'username' : username,
        'clientVersion' : '2.8.7',
        'clientName' : 'py.test',
        'deviceName' : 'terminal'
    }

def deviceForUser(user):
    data = deviceData(user.username)
    device = Device._createFromTokenData(user.id, data)
    device.save()
    commit()
    return device

def getAccessTokenForUser(user):
    device = deviceForUser(user)
    return pyjmap.auth._createAccessToken(user, device)


