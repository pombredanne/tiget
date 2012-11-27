#!/usr/bin/env python
import sys
import getopt
from datetime import datetime, timezone

import psycopg2

from tiget.git import transaction
from tiget.scrum.models import Milestone, Ticket


def make_datetime(timestamp):
    return datetime.fromtimestamp(timestamp, timezone.utc)


@transaction.wrap('agilo import')
def main():
    conn = psycopg2.connect(' '.join(sys.argv[1:]))
    cur = conn.cursor()

    print('Importing Milestones')
    cur.execute('select name, description, completed from milestone')
    for name, description, completed in cur:
        Milestone.objects.create(name=name, description=description,
            completed_at=make_datetime(completed))

    print('TODO: import users')

    print('Importing Tickets')
    cur.execute('select summary, description, milestone from ticket')
    for summary, description, milestone in cur:
        milestone = Milestone.objects.get(name=milestone) if milestone else None
        Ticket.objects.create(summary=summary, description=description,
            milestone=milestone)

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
