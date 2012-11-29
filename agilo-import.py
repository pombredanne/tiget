#!/usr/bin/env python
import sys
import getopt
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import DictCursor

from tiget.git import transaction
from tiget.scrum.models import Milestone, Sprint, Ticket


@transaction.wrap('agilo import')
def main():
    conn = psycopg2.connect(' '.join(sys.argv[1:]))
    cur = conn.cursor(cursor_factory=DictCursor)

    print('Importing Milestones')
    cur.execute('''
        select name,
               description,
               to_timestamp(due) as due,
               to_timestamp(completed) as completed_at
        from milestone
    ''')
    for row in cur:
        Milestone.objects.create(**row)

    print('Importing Sprints')
    cur.execute('''
        select name,
               description,
               case milestone when '' then null else milestone end as milestone,
               to_timestamp(start) as start,
               to_timestamp(sprint_end) as end
        from agilo_sprint
    ''')
    for row in cur:
        Sprint.objects.create(**row)

    print('TODO: import users')

    print('Importing Tickets')
    cur.execute('''
        select summary,
               description,
               case milestone when '' then null else milestone end as milestone,
               case type when 'task' then 'feature' else type end as ticket_type,
               case when status in ('assigned', 'accepted', 'reopened') then 'new'
                    when status in ('info_needed', 'undecided') then 'wtf'
                    when status = 'closed' then
                        case resolution when 'invalid' then 'invalid'
                                        when 'worksforme' then 'invalid'
                                        when 'duplicate' then 'duplicate'
                                        when 'wontfix' then 'wontfix'
                                        else 'fixed'
                        end
                    else status
               end as status
        from ticket
        where type in ('idea', 'requirement', 'bug', 'feature', 'wording',
                       'story', 'task', 'training')
    ''')
    for row in cur:
        Ticket.objects.create(**row)

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
