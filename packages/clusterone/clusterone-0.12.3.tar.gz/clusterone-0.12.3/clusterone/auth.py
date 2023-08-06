from clusterone.persistance.session import Session

import functools


def authenticate():
    def decorator(f):

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                session = args[0].config
            except:
                session = Session()
                session.__init__()
                session.load()

            username = session.get('username')
            token = session.get('token')
            if username == '' or token == '':
                print("You are not logged in yet. Use 'just login'.")
                return
            return f(*args, **kwargs)

        return wrapper

    return decorator

