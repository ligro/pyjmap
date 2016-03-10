import pytest
import pyjmap

@pytest.fixture
def app():
    pyjmap.app.testing = True
    pyjmap.app.debug = True

    return pyjmap.app

print('setup_module')

pyjmap.app.app_context().push()
pyjmap.database.db.drop_all()
pyjmap.database.db.create_all()

