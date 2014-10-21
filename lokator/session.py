from django.contrib.sessions.backends.db import SessionStore as DbSessionStore

class SessionStore(DbSessionStore):
    def cycle_key(self):
        "Do not change session keys"
