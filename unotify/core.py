from subprocess import call, getstatusoutput
from threading import Timer
from . import urgencies

BASE_COMMAND = "notify-send"


def _remove_illegal_chars(text: str):
    output = text.replace('"', '"')
    return output

def _get_urgency(number: int) -> str:
    URGENCIES = {
        1: 'low',
        2: 'normal',
        3: 'critical'
    }
    try:
        return URGENCIES[number]
    except Exception:
        return URGENCIES[2]

def _close_notification(number: int):
    call(['dbus-send',
        '--type=method_call',
        '--dest=org.freedesktop.Notifications',
        '/org/freedesktop/Notifications',
        'org.freedesktop.Notifications.CloseNotification',
        'uint32:{}'.format(number)])

def notify(
    title: str,
    message: str,
    app_name: str = None,
    app_icon: str = None,
    hint: str = None,
    category: str = None,
    urgency: int = None,
    replaceid: int = None,
    timeout: int = None,
    returnid: bool = False,
    transient: bool = False,
):
    if not urgency:
        urgency = urgencies.NORMAL

    COMMAND = f'{BASE_COMMAND}\
        "{_remove_illegal_chars(title)}"\
        "{_remove_illegal_chars(message)}"\
        -u {_get_urgency(urgency)} -p'

    if app_name:
        COMMAND += f" -a {_remove_illegal_chars(app_name)}"
    if app_icon:
        COMMAND += f" -i {app_icon}"
    if category:
        COMMAND += f" -c {category}"
    if hint:
        COMMAND += f" -h {_remove_illegal_chars(hint)}"
    if replaceid:
        COMMAND += f" -r {replaceid}"
    if timeout:
        COMMAND += f" -t {timeout*1000}"
    if transient:
        COMMAND += f" -e"

    status, output = getstatusoutput(COMMAND)
    if status != 0:
        raise Exception(output)
    else:
        notifyid = int(output)

    if urgency == urgencies.HIGH and timeout:
        Timer(timeout, _close_notification, args=[notifyid]).start()
   
    if returnid:
        return notifyid
    else:
        return True
