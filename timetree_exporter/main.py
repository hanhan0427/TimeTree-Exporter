#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from icalendar import Calendar
from timetree_exporter import TimeTreeEvent, ICalEventFormatter, __version__
from timetree_exporter.api.auth import login
from timetree_exporter.api.calendar import get_upcoming_events


def main():
    email = os.environ['EMAIL']
    password = os.environ['PASSWORD']
    calendar_id = os.environ['CALENDAR_ID']

    print('Signing in to TimeTree...')
    try:
        token = login(email, password)
    except Exception as e:
        print(f'Failed to sign in: {e}')
        sys.exit(1)

    print('Getting upcoming events...')
    try:
        events = get_upcoming_events(token, calendar_id)
    except Exception as e:
        print(f'Failed to get events: {e}')
        sys.exit(1)

    print(f'Found {len(events)} events')

    cal = Calendar()
    cal.add('prodid', f'-//TimeTree-Exporter//{__version__}//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', 'TimeTree Calendar')
    cal.add('x-wr-timezone', 'UTC')

    formatter = ICalEventFormatter()
    for event in events:
        cal.add_component(formatter.to_ical(TimeTreeEvent.from_dict(event)))

    Path('calendar.ics').write_bytes(cal.to_ical())


if __name__ == '__main__':
    main()
