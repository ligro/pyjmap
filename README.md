# pyjmap

## init db

need to be improved
```python
python
import index
index.app.app_context().push()
index.db.create_all()
```

## add first user

```python
python
import index
index.app.app_context().push()
import database
user = database.User()
user.username = 'my_username'
user.setPassword('my_password')
user.save()
database.commit()
```
