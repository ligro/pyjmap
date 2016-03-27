import pyjmap

def func_name(depth = 2):
    import traceback
    from pprint import pprint
    return traceback.extract_stack(limit=depth)[0][2]

def user(password = None):
    user = pyjmap.database.User()
    user.username = func_name(depth=3)

    if not password :
        password = user.username + 'password'

    user.setPassword(password)
    user.save()
    pyjmap.database.commit()
    return user

def deviceData(username):
    return {
        'username' : username,
        'clientVersion' : '2.8.7',
        'clientName' : 'py.test',
        'deviceName' : 'terminal'
    }

