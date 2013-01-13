from os.path import expanduser

from cryptacular.bcrypt import BCRYPTPasswordManager
from tiget.conf import settings


MANAGER = BCRYPTPasswordManager()


def open_passwd(mode):
    conf_file = expanduser(settings.scrumweb.password_file)
    return open(conf_file, mode)


def set_password(user, password):
    hashed = MANAGER.encode(password)
    with open_passwd('a+') as f:
        f.seek(0)
        lines = [
            line for line in f.readlines() if not line.startswith(user + ' ')]
        lines.append('{} {}\n'.format(user, hashed))
        f.truncate(0)
        f.write(''.join(lines))


def check_password(target_user, password):
    with open_passwd('r') as f:
        pw_ok = False
        for line in f:
            user, hashed = line.rstrip('\n').split(' ', 1)
            if user == target_user:
                pw_ok = MANAGER.check(hashed, password)
        return pw_ok
