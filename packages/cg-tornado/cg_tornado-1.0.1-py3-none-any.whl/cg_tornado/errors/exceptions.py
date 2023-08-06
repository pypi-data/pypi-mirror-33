
"""
# Filename: exceptions.py
"""

from .errorcodes import ErrorCodes


class CgBaseException(Exception):
    def __init__(self, errorCode, errorMessage, *args):
        super().__init__()
        self.ErrorCode = errorCode
        self.ErrorMessage = errorMessage
        self.Args = args


class PermissionDenied(CgBaseException):
    def __init__(self):
        super().__init__(ErrorCodes.ERROR_PERMISSION_DENIED, 'You do not have permissions to perform the action you are attempting')


class UserPasswordMismatch(CgBaseException):
    def __init__(self):
        super().__init__(ErrorCodes.ERROR_USERPASS_MISMATCH, 'Username/Email Password combination mismatch')


class IncorrectCurrentPassword(CgBaseException):
    def __init__(self):
        super().__init__(ErrorCodes.ERROR_INCORRECT_PASSWORD, 'Incorrect current password')


class UserBlocked(CgBaseException):
    def __init__(self, reason):
        super().__init__(ErrorCodes.ERROR_USER_BLOCKED, "Your account is blocked due to following reason: '{}'".format(reason))


class UserNotActivated(CgBaseException):
    def __init__(self):
        super().__init__(ErrorCodes.ERROR_ACCOUNT_NOT_ACTIVE, "Your account is not yet activated")


class DeviceNotAuthorized(CgBaseException):
    def __init__(self):
        super().__init__(ErrorCodes.ERROR_DEVICE_NOT_AUTHORIZED, "Current device is not authorized")


class InvalidVerificationCode(CgBaseException):
    def __init__(self):
        super().__init__(ErrorCodes.ERROR_VERIFICATION_CODE_INVALID, 'Invalid Verification Code')


class VerificationCodeExpired(CgBaseException):
    def __init__(self):
        super().__init__(ErrorCodes.ERROR_VERIFICATION_CODE_EXPIRED, 'Verification Code Expired')


class SessionExpired(CgBaseException):
    def __init__(self, UID=None):
        super().__init__(ErrorCodes.SESSION_EXPIRED, 'Session Expired', 'Id', UID)


class ExceptionWithMessage(CgBaseException):
    def __init__(self, message):
        super().__init__(ErrorCodes.ERROR_UNKNOWN, '{}'.format(message))


class TableNotFound(CgBaseException):
    def __init__(self, tableName):
        super().__init__(ErrorCodes.ERROR_TABLE_NOT_FOUND, "Table '{}' not found".format(tableName))


class RequiredFieldMissing(CgBaseException):
    def __init__(self, fieldName):
        super().__init__(ErrorCodes.ERROR_REQUIRED_FIELD_MISSING, "Field '{}' is missing".format(fieldName))


class RequiredFieldEmpty(CgBaseException):
    def __init__(self, fieldName):
        super().__init__(ErrorCodes.ERROR_REQUIRED_FIELD_EMPTY, "Field '{}' is empty".format(fieldName))


class ChildRecordExists(CgBaseException):
    def __init__(self):
        super().__init__(ErrorCodes.ERROR_FOREIGN_KEY_CONSTRAINT_FAILED, "Failed to delete given record(s), child records exist.")


class InvalidColumn(CgBaseException):
    def __init__(self, columnName):
        super().__init__(ErrorCodes.ERROR_INVALID_COLUMN, "Column '{}' is not a valid column".format(columnName))


class TableColumnNotFound(CgBaseException):
    def __init__(self, columnName):
        super().__init__(ErrorCodes.ERROR_TABLE_COLUMN_NOT_FOUND, "Column '{}' not found".format(columnName))


class RecordNotFound(CgBaseException):
    def __init__(self, recType, ids, values):
        super().__init__(ErrorCodes.ERROR_RECORD_NOT_FOUND, "{} with '{}' = '{}' not found".format(recType, ids, values))
