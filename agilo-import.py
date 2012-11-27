#!/usr/bin/env python
import sys
import getopt
from datetime import datetime, timezone

import psycopg2

from tiget.git import transaction
from tiget.simple_workflow.models import Milestone, Ticket


@transaction.wrap('agilo import')
def main():
    conn = psycopg2.connect(' '.join(sys.argv[1:]))
    cur = conn.cursor()

    print('Importing Milestones')
    cur.execute('select name, description, completed from milestone')
    for name, description, completed in cur:
        completed_at = datetime.fromtimestamp(completed, timezone.utc)
        Milestone.objects.create(name=name, description=description,
            completed_at=completed_at)

    print('TODO: import users')

    print('Importing Tickets')
    cur.execute('select summary, description from ticket')
    for summary, description in cur:
        Ticket.objects.create(summary=summary, description=description)

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
