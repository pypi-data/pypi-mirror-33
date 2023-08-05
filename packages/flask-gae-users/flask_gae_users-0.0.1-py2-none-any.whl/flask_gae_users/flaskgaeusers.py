# -*- coding: utf-8 -*-

import functools
import logging

from google.appengine.api import users



logger = logging.getLogger( __name__ )



class GAEUserException( Exception ):
    pass

class GAENoUserException( GAEUserException ):
    pass

class GAENotAdminException( GAENoUserException ):
    pass



class GAEUsers( object ):

    def __init__( self, app ):
        self.app = app
        self.init_app( app )

    def init_app( self, app ):
        app.extensions[ 'flaskgaeusers' ] = self
        app.get_login_url = self.get_login_url
        app.get_logout_url = self.get_logout_url
        app.require_user = self.require_user
        app.require_admin = self.require_admin

    def get_user( self ):
        return users.get_current_user()

    def get_login_url( self, redirect = '/' ):
        return users.create_login_url( redirect )

    def get_logout_url( self, redirect = '/' ):
        return users.create_logout_url( redirect )

    def require_user( self ):
        def wrapper( func ):
            @functools.wraps( func )
            def decorated( *args, **kwargs ):
                user = users.get_current_user()
                if user:
                    return func( *args, **kwargs )
                else:
                    raise GAENoUserException( "The user is not logged in" )
            return decorated
        return wrapper

    def require_admin( self ):
        def wrapper( func ):
            @functools.wraps( func )
            def decorated( *args, **kwargs ):
                user = users.get_current_user()
                if user:
                    if users.is_current_user_admin():
                        return func( *args, **kwargs )
                    else:
                        raise GAENotAdminException( "The user is not an administrator" )
                else:
                    raise GAENoUserException( "The user is not logged in" )
            return decorated
        return wrapper
