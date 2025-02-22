#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from icalendar import Calendar
from timetree_exporter import TimeTreeEvent, ICalEventFormatter, __version__
from timetree_exporter.api.auth import TimeTreeAuth
from timetree_exporter.api.calendar import TimeTreeCalendar


def main():
    # Get login credentials from environment variables
    email = os.environ['EMAIL']
    password = os.environ['PASSWORD']
    calendar_id = os.environ['CALENDAR_ID']

    # Sign in to TimeTree
    print("Signing in to TimeTree...")
    try:
        api_access_token = get_token(email, password)
        print("Successfully signed in!")
    except Exception as e:
        print(f"Failed to sign in: {e}")
        sys.exit(1)

    # Get upcoming events
    print("Getting upcoming events...")
    try:
        events = get_upcoming_events(api_access_token, calendar_id)
        print(f"Found {len(events)} events")
    except Exception as e:
        print(f"Failed to get events: {e}")
        sys.exit(1)

    # Create calendar
    cal = Calendar()
    cal.add('prodid', f'-//TimeTree Calendar Exporter v{__version__}//')
    cal.add('version', '2.0')

    # Add events to calendar
    formatter = ICalEventFormatter()
    for event in events:
        e = TimeTreeEvent(event)
        cal.add_component(formatter.format(e))

    # Save calendar
    output_dir = Path('calendars')
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f'calendar_{calendar_id}.ics'
    with open(output_path, 'wb') as f:
        f.write(cal.to_ical())
    print(f"Calendar saved to {output_path}")

    # Save metadata
    metadata = {
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'version': __version__,
        'event_count': len(events)
    }
    metadata_path = output_dir / f'calendar_{calendar_id}.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Metadata saved to {metadata_path}")

if __name__ == "__main__":
    main()
