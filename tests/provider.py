import pyjmap

def user(username, password):
    user = pyjmap.database.User()
    user.username = username
    user.setPassword(password)
    user.save()
    pyjmap.database.commit()
    return user

def deviceData(username):
    return {
        'username' : username,
        'clientVersion' : '2.8.7',
        'clientName' : 'py.test',
        'devicename' : 'terminal'
    }

