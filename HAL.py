from __future__ import print_function

import logging
import time
import string
import re
import sys

import googleapiclient
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import requests
import ics
import arrow
import httplib2

from config import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=LOGFILE, mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s|[%(levelname)s] %(message)s'))
logger.addHandler(handler)

def get_current_events():
    """Retrieves data from iCal iCal feed and returns an ics.Calendar object 
    containing the parsed data.
    Returns the parsed Calendar object or None if an error occurs.
    """
    resp = requests.get(ICAL_FEED)
    if resp.status_code != 200:
        logger.error('> Error retrieving iCal feed!')
        return None

    try:
        cal = ics.Calendar(resp.text)
    except Exception as e:
        logger.error('> Error parsing iCal data ({})'.format(e))
        return None

    return cal

# modified from Google Calendar API quickstart example
def get_credentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
    """
    store = Storage(CREDENTIAL_PATH)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, None)
    return credentials

def get_gcal_events(service, from_time):
    """Retrieves the current set of Google Calendar events from the selected
    user calendar. Only includes upcoming events (those taking place from start
    of the current day. 
    Returns a dict containing the event(s) existing in the calendar.
    """

    # The list() method returns a dict containing various metadata along with the actual calendar entries (if any). 
    # It is not guaranteed to return all available events in a single call, and so may need called multiple times
    # until it indicates no more events are available, signalled by the absence of "nextPageToken" in the result dict

    logger.debug('Retrieving Google Calendar events')

    # make an initial call, if this returns all events we don't need to do anything else,,,
    eventsResult = service.events().list(calendarId=CALENDAR_ID, 
                                         timeMin=from_time, 
                                         singleEvents=True, 
                                         orderBy='startTime', 
                                         showDeleted=True).execute()

    events = eventsResult.get('items', [])
    # if nextPageToken is NOT in the dict, this should be everything
    if 'nextPageToken' not in eventsResult:
        logger.info('> Found {:d} upcoming events in Google Calendar (single page)'.format(len(events)))
        return events

    # otherwise keep calling the method, passing back the nextPageToken each time
    while 'nextPageToken' in eventsResult:
        token = eventsResult['nextPageToken']
        eventsResult = service.events().list(calendarId=CALENDAR_ID, 
                                             timeMin=from_time, 
                                             pageToken=token, 
                                             singleEvents=True, 
                                             orderBy='startTime', 
                                             showDeleted=True).execute()
        newevents = eventsResult.get('items', [])
        events.extend(newevents)
        logger.debug('> Found {:d} events on new page, {:d} total'.format(len(newevents), len(events)))
    
    logger.info('> Found {:d} upcoming events in Google Calendar (multi page)'.format(len(events)))
    return events

def get_gcal_datetime(arrow_datetime, gcal_timezone):
    arrow_datetime = arrow_datetime.to(gcal_timezone)
    return {u'dateTime': arrow_datetime.format('YYYY-MM-DDTHH:mm:ssZZ'), 'timeZone': gcal_timezone}

def get_gcal_date(arrow_datetime):
    return {u'date': arrow_datetime.format('YYYY-MM-DD')}

def create_id(uid, begintime, endtime):
    """ Converts ical UUID, begin and endtime to a valid Gcal ID
    Characters allowed in the ID are those used in base32hex encoding, i.e. lowercase letters a-v and digits 0-9, see section 3.1.2 in RFC2938
    Te length of the ID must be between 5 and 1024 characters
    https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/calendar_v3.events.html
    Returns:
        ID
    """
    allowed_chars = string.ascii_lowercase[:22] + string.digits
    temp = re.sub('[^{}]'.format(allowed_chars), '', uid.lower())
    return re.sub('[^{}]'.format(allowed_chars), '', uid.lower()) + str(arrow.get(begintime).timestamp) + str(arrow.get(endtime).timestamp)

if __name__ == '__main__':
    # setting up Google Calendar API for use
    logger.debug('> Loading credentials')
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # retrieve events from Google Calendar, starting from beginning of current day
    today = arrow.now().replace(hour=0, minute=0, second=0, microsecond=0)
    logger.info('> Retrieving events from Google Calendar')
    gcal_events = get_gcal_events(service, today.isoformat())

    # retrieve events from the iCal feed
    logger.info('> Retrieving events from iCal feed')
    ical_cal = get_current_events()

    if ical_cal is None:
        sys.exit(-1)

    # convert iCal event list into a dict indexed by (converted) iCal UID
    ical_events = {}
    for ev in ical_cal.events:
        # filter out events in the past, don't care about syncing them
        if arrow.get(ev.begin) > today:
            ical_events[create_id(ev.uid, ev.begin, ev.end)] = ev

    logger.debug('> Collected {:d} iCal events'.format(len(ical_events)))

    # retrieve the Google Calendar object itself
    gcal_cal = service.calendars().get(calendarId=CALENDAR_ID).execute()

    logger.info('> Processing Google Calendar events...')
    gcal_event_ids = [ev['id'] for ev in gcal_events]

    # now add any iCal events not already in the Google Calendar 
    logger.info('> Processing iCal events...')
    for ical_event in ical_events.values():
        if create_id(ical_event.uid, ical_event.begin, ical_event.end) not in gcal_event_ids:
            gcal_event = {}
            gcal_event['summary'] = ical_event.name
            gcal_event['id'] = create_id(ical_event.uid, ical_event.begin, ical_event.end)
            gcal_event['description'] = '%s (Imported from mycal.py)' % ical_event.description
            gcal_event['location'] = ical_event.location
            gcal_event['reminders'] = {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 120},
                    {'method': 'popup', 'minutes': 120},
                ],
            }

            # check if no time specified in iCal, treat as all day event if so
            delta = arrow.get(ical_event.end) - arrow.get(ical_event.begin)
            # TODO multi-day events?
            if delta.days >= 1:
                gcal_event['start'] = get_gcal_date(ical_event.begin)
                logger.info('iCal all-day event {} to be added at {}'.format(ical_event.name, ical_event.begin))
                if ical_event.has_end:
                    gcal_event['end'] = get_gcal_date(ical_event.end)
            else:
                gcal_event['start'] = get_gcal_datetime(ical_event.begin, gcal_cal['timeZone'])
                logger.info('iCal event {} to be added at {}'.format(ical_event.name, ical_event.begin))
                if ical_event.has_end:
                    gcal_event['end'] = get_gcal_datetime(ical_event.end, gcal_cal['timeZone'])

            try:
                time.sleep(API_SLEEP_TIME)
                service.events().insert(calendarId=CALENDAR_ID, body=gcal_event).execute()
            except:
                time.sleep(API_SLEEP_TIME)
                service.events().update(calendarId=CALENDAR_ID, eventId=gcal_event['id'], body=gcal_event).execute()
    
