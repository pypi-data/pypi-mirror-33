API_VALIDATION_FAILED = 'E0000001'
AUTHENTICATION_FAILED = 'E0000004'
INVALID_SESSION = 'E0000005'
PERMISSION_DENIED = 'E0000006'
NOT_FOUND = 'E0000007'
INVALID_TOKEN = 'E0000011'
USER_ALREADY_ACTIVATED = 'E0000016'
ROLE_ALREADY_ASSIGNED = 'E0000090'

class Error(Exception):
    def __init__(self, error):
        if error is None:
            error = {}

        Exception.__init__(self, error.get('errorSummary'))

        self.error = error
        self.causes = error.get('errorCauses')
        self.code = error.get('errorCode')
        self.id = error.get('errorId')
        self.link = error.get('errorLink')
        self.summary = error.get('errorSummary')

    def __repr__(self):
        return str(self.error)


class NotFound(Error):
    def __init__(self, error):
        super(NotFound, self).__init__(error)


class RoleAlreadyAssigned(Error):
    def __init__(self, error):
        super(RoleAlreadyAssigned, self).__init__(error)


class UserAlreadyActivated(Error):
    def __init__(self, error):
        super(UserAlreadyActivated, self).__init__(error)


def factory(error):
    if error is None or not error.get('errorCode'):
        return Error(error)
    ec = error['errorCode']
    if ec == NOT_FOUND:
        return NotFound(error)
    if ec == ROLE_ALREADY_ASSIGNED:
        return RoleAlreadyAssigned(error)
    if ec == USER_ALREADY_ACTIVATED:
        return UserAlreadyActivated(error)
    return Error(error)
