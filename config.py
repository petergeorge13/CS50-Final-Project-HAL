ICAL_FEED = 'https://www.gocrimson.com/composite?print=ical'

# the ID of the calendar to use for iCal events, should be of the form
# 'ID@group.calendar.google.com', check the calendar settings page to find it.
# (can also be 'primary' to use the default calendar)
CALENDAR_ID = 'primary'

# must use the OAuth scope that allows write access
SCOPES = 'https://www.googleapis.com/auth/calendar'

# API secret stored in this file
CLIENT_SECRET_FILE = 'HAL_secret.json'

# Location to store API credentials
CREDENTIAL_PATH = 'HAL.json'

# Application name for the Google Calendar API
APPLICATION_NAME = 'Harvard Athletics Link (HAL)'

# File to use for logging output
LOGFILE = 'Harvard_Athletics_Link.txt'

# Time to pause between successive API calls that may trigger rate-limiting protection
API_SLEEP_TIME = 0.05
