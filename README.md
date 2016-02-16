# pyjmap

## init db

need to be improved
```python
python
import pyjmap
pyjmap.app.app_context().push()
pyjmap.db.create_all()
```

## add first user

```python
python
import pyjmap
pyjmap.app.app_context().push()
import database
user = database.User()
user.username = 'my_username'
user.setPassword('my_password')
user.save()
database.commit()
```
