#!/usr/bin/env python
import sys
import getopt
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import DictCursor

from tiget.git import transaction
from tiget.scrum.models import Milestone, Sprint, User, Ticket


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

    print('Importing users')
    # there is no user table, so we do our best to collect the user names
    cur.execute('''
        select distinct trim(raw.user) as name
        from (select owner as user from ticket
              union all
              select reporter as user from ticket
              union all
              select author as user from ticket_change
             ) as raw
        where raw.user != '' and raw.user is not null
        order by trim(raw.user)
    ''')
    user_pks = {}
    for row in cur:
        name = row['name']
        default_email = '{}@example.org'.format(name)
        email = input(
            'Email for user "{}" [{}]: '.format(name, default_email)).strip()
        if not email:
            email = default_email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create(email=email, name=name)
        user_pks[name] = user.pk

    print('Importing Tickets')
    cur.execute('''
        select id,
               summary,
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
               end as status,
               trim(reporter) as reporter,
               trim(owner) as owner
        from ticket
        where type in ('idea', 'requirement', 'bug', 'feature', 'wording',
                       'story', 'task', 'training')
    ''')
    ticket_pks = {}
    for row in cur:
        ticket_id = row.pop('id')
        for key in ('reporter', 'owner'):
            name = row[key]
            row[key] = User.objects.get(pk=user_pks[name]) if name else None
        ticket = Ticket.objects.create(**row)
        ticket_pks[ticket_id] = ticket.pk

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
