import os
from starlette.middleware.sessions import SessionMiddleware

def add_session_middleware(app):
    secret=os.getenv("SECRET_KEY","dev-only-change-this-secret-before-deployment")
    app.add_middleware(SessionMiddleware,secret_key=secret,same_site="lax",https_only=os.getenv("COOKIE_SECURE","0")=="1",max_age=60*60*24*7)
