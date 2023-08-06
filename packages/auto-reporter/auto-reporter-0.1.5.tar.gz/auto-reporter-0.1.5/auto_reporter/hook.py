import sys
import subprocess
import getopt
import re
from .sender import ReportSender
from .sender import ATError

def get_params(argv):
    display_name = ''
    username = ''
    password = ''
    try:
        opts, args = getopt.getopt(
            argv, 
            'hd:u:p:', 
            ['help', 'display-name=', 'username=', 'password=', 'thanks']
        )
    except getopt.GetoptError:
        print('Unknown option')
        print('Type install-auto-reporter --help for more information.')

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('Usage:')
            print('install-auto-reporter -u <username> -p <password> -d <project-display-name>')
            sys.exit(0)
        if opt in ('-d', '--display-name'):
            display_name = arg
        if opt in ('-u', '--username'):
            username = arg
        if opt in ('-p', '--password'):
            password = arg
        if opt == '--thanks':
            print('mua')
            sys.exit(0)

    return (display_name, username, password)

def get_commit_msgs():
    for line in sys.stdin:
        local_ref, local_sha1, remote_ref, remote_sha1 = line.strip().split(' ')
        raw_messages = subprocess.check_output(
            ['git', 'show', '--format=%s', '-s', "%s..%s" % (remote_sha1, local_sha1)]
        )
        return raw_messages.decode('utf-8').splitlines()
    return None

def generate_report(report_array, title, body):
    new_report_array = report_array[:]
    if len(report_array) == 1:
        # no title found
        # append title
        new_report_array.append('\r\n%s' % title)
        new_report_array.append(body)
        return new_report_array
    elif len(report_array) == 2:
        # found title
        new_report_array.insert(1, title)
        new_report_array.insert(2, body)
        return new_report_array
    else:
        raise ATError('More than one title found in old report')

def main(argv, dir_name):
    display_name, username, password = get_params(argv)
    if not username or not password:
        print('username and password must be specificated.')
    if not display_name:
        display_name = dir_name
    commit_msgs = get_commit_msgs()
    if not commit_msgs or len(commit_msgs) == 0:
        print('Nothing to push. Did you commit before pushing?')
    
    try:
        title = '## %s\r\n' % display_name
        AT = ReportSender(username, password)
        AT.get_content()
        report_array = re.split(r'## %s\r\n' % display_name, AT.old_content)

        body_string = ''
        for commit_msg in commit_msgs:
            body_string = body_string + '- %s\r\n' % commit_msg

        new_report_array = generate_report(report_array, title, body_string)
        new_report = ''.join(new_report_array)
        AT.write(new_report)
        print('Success!')
    except ATError as e:
        print('Something bad happens:\n%s' % e)
        print('But you can still trying to push your commit to your remote server.')
        print('Notice: If you choose to continue, auto-reporter will NOT recive these commits next time, you\'ll have to manually add them to your report.')
        continue_push = input('Continue? [Y/n] ').lower()
        valid = {
            '': True,
            'y': True,
            'ye': True,
            'yes': True,
            'n': False,
            'no': False
        }
        if not valid[continue_push]:
            print('Aborting...')
            return 1
        return 0