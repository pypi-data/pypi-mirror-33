# Filename: httperrors.py
# Updated Error messages from following URL
# https://www.smartlabsoftware.com/ref/http-status-codes.htm

HttpErrors = {
    "400": {
        "title": "Bad Request",
        "message": "The server cannot process the request due to something that is perceived to be a client error."
    },
    "401": {
        "title": "Unauthorized",
        "message": "The requested resource requires an authentication."
    },
    "403": {
        "title": "Access Denied",
        "message": "The requested resource requires an authentication."
    },
    "404": {
        "title": "Resource not found",
        "message": "The requested resource could not be found but may be available again in the future."
    },
    "500": {
        "title": "Webservice currently unavailable",
        "message": "An unexpected condition was encountered.\nOur service team has been dispatched to bring it back online."
    },
    "501": {
        "title": "Not Implemented",
        "message": "The Webserver cannot recognize the request method."
    },
    "502": {
        "title": "Webservice currently unavailable",
        "message": "We've got some trouble with our backend upstream cluster.\nOur service team has been dispatched to bring it back online."
    },
    "503": {
        "title": "Webservice currently unavailable",
        "message": "We've got some trouble with our backend upstream cluster.\nOur service team has been dispatched to bring it back online."
    },
    "520": {
        "title": "Origin Error - Unknown Host",
        "message": "The requested hostname is not routed. Use only hostnames to access resources."
    },
    "521": {
        "title": "Webservice currently unavailable",
        "message": "We've got some trouble with our backend upstream cluster.\nOur service team has been dispatched to bring it back online."
    },
    "533": {
        "title": "Scheduled Maintenance",
        "message": "This site is currently down for maintenance.\nOur service team is working hard to bring it back online soon."
    },
    "550": {
        "title": "Permission Denied",
        "message": "The server is stating the account you have currently logged in as does not have permission to perform the action you are attempting."
    }
}
