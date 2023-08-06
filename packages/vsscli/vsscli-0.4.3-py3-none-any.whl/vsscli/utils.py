import re
import json
import click
import datetime
from pyvss.exceptions import VssError
from tabulate import tabulate
from pyvss.manager import DATETIME_FMT
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

columns_two = "{0:<40} {1:<20}"
columns_two_kv = "{0:<20}: {1:<20}"
columns_two_os = "{0:<40} {1:<20}"
columns_two_comms = "{0:<40} {1:<20}"
columns_three = "{0:<20} {1:<40} {2:<20}"
columns_four = "{0:<20} {1:<30} {2:<30} {3:<20}"
columns_five = "{0:<40} {1:<30} {2:<30} {3:<10} {4:<10} {5:<10} {6:<20}"


def pretty_print(dictionary):
    _lines = json.dumps(dictionary, indent=4, sort_keys=True)
    lines = highlight(_lines, JsonLexer(), TerminalFormatter())
    return lines


def validate_json_type(ctx, param, value):
    try:
        if value is not None:
            return json.loads(value)
    except ValueError as ex:
        click.echo('Error {}'.format(ex), err=True)
        raise click.BadParameter(
            '{} should be a JSON Parameter Input.'.format(param.name))


def validate_phone_number(ctx, param, phone):
    phone_regex = r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|' \
                  r'\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})+'
    if not re.match(phone_regex, phone):
        raise click.BadParameter(
            'Value must be in the following format 416-166-6666')
    return phone


def validate_admin(ctx, param, value):
    if value:
        _value = value.split(':')
        if not value or len(_value) < 2:
            raise click.BadParameter('Admin should be in the '
                                     'following format: '
                                     'FullName:Phone:email')
        validate_email(ctx, param, _value[2])
        validate_phone_number(ctx, param, _value[1])
        return value


def validate_inform(ctx, param, value):
    if value:
        _value = value.split(',')
        if not value:
            raise click.BadParameter('Informational contacts format:'
                                     ' email@utoronto.ca,email2@utoronto.ca')
        for email in _value:
            validate_email(ctx, param, email)
        return value


def validate_schedule(ctx, param, schedule):
    try:
        if schedule is not None:
            datetime.datetime.strptime(schedule, DATETIME_FMT)
            return schedule
    except ValueError:
        raise click.BadParameter(
            'Schedule timestamp must be in {} format.'.format(DATETIME_FMT))


def validate_email(ctx, param, email):
    email_regex = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
    if not re.match(email_regex, email):
        raise click.BadParameter('Value must be in the '
                                 'following format user@utoronto.ca')
    return email


def yes_no(val):
    return 'Yes' if val else 'No'


def capitalize(value):
    return re.sub(r"(\w)([A-Z])", r"\1 \2", value).title()


def print_object(obj, key, attr_list=None):
    lines = []
    _append = lines.append
    if not attr_list:
        dump(obj, _key=key, _list=lines)
    else:
        for attr in attr_list:
            value = yes_no(obj[attr]) \
                if isinstance(obj[attr], bool) \
                else obj[attr]
            _append(columns_two_kv.format(
                capitalize(attr), value))
    return '\n'.join(lines)


def print_objects(obj, no_header, quiet, id, attr_list):
    lines = []
    _append = lines.append
    header = []
    tbfmt = 'plain' if no_header or quiet else 'simple'
    if quiet:
        for o in obj:
            _append([o[id]])
    else:
        header = attr_list
        for o in obj:
            _append([o.get(a) for a in attr_list])
    lines = tabulate(lines, headers=header, tablefmt=tbfmt, missingval='-')
    return lines


def print_morefs(obj, no_header, quiet, table_header=None, **kwargs):
    lines = []
    _append = lines.append
    header = []
    tbfmt = 'plain' if no_header or quiet else 'simple'
    if quiet:
        for o in obj:
            _append([o['moref']])
    else:
        header = ['moref', 'name', 'description'] if not table_header \
            else table_header
        for o in obj:
            row = list()
            for i in table_header:
                row.append(o[i])
            _append(row)
    lines = tabulate(lines, headers=header, tablefmt=tbfmt)
    return lines


def print_vm_events(events, **kwargs):
    lines = []
    _append = lines.append
    events = events['events']
    header = ['username', 'created time', 'message']
    for event in events:
        _append([event['userName'], event['createdTime'], event['message']])
    return tabulate(lines, headers=header)


def print_request(obj):
    lines = []
    _append = lines.append
    try:
        for k, v in obj.items():
            if isinstance(v, dict):
                v = ', '.join(['{}: {}'.format(_k, _v)
                               for _k, _v in v.items()])
            elif isinstance(v, list):
                v = ', '.join([str(_v) for _v in v])
            elif isinstance(v, bool):
                v = yes_no(v)
            elif isinstance(v, type(None)):
                v = ' '
            if k not in ['_links']:
                _append(columns_two_kv.format(k, v))
        return '\n'.join(lines)
    except Exception as ex:
        raise VssError('Invalid response: {}'.format(ex))


def print_tokens(obj, no_header, quiet, **kwargs):
    lines = []
    _append = lines.append
    header = []
    tbfmt = 'plain' if no_header or quiet else 'simple'
    if quiet:
        for o in obj:
            _append([o['id']])
    else:
        header = ['id', 'value', 'valid', 'last_access']
        for o in obj:
            _append([o[header[0]],
                     '{}...'.format(o[header[1]][:60]),
                     o['status']['valid'],
                     o['status'][header[3]]])
        # removing headers if no_header or quiet
        header = [] if no_header or quiet else header
    lines = tabulate(lines, headers=header, tablefmt=tbfmt)
    return lines


def print_messages(obj, no_header, quiet, **kwargs):
    lines = []
    _append = lines.append
    header = []
    tbfmt = 'plain' if no_header or quiet else 'simple'
    if quiet:
        for o in obj:
            _append([o['id']])
    else:
        header = ['id', 'kind', 'subject', 'status']
        for o in obj:
            _append([o[h] for h in header])
    lines = tabulate(lines, headers=header, tablefmt=tbfmt)
    return lines


def print_os(obj, no_header, quiet, table_header=None):
    lines = []
    _append = lines.append
    header = []
    tbfmt = 'plain' if no_header or quiet else 'simple'
    if quiet:
        for o in obj:
            _append([o['id']])
    else:
        header = ['id', 'guestId', 'guestFullName']
        for o in obj:
            _append([o[header[0]], o[header[1]], o[header[2]]])
    lines = tabulate(lines, headers=header, tablefmt=tbfmt)
    return lines


def print_requests(obj, no_header, quiet, table_header=None):
    lines = []
    _append = lines.append
    header = []
    tbfmt = 'plain' if no_header or quiet else 'simple'
    if quiet:
        for r in obj:
            _append([r['id']])
    else:
        header = table_header or ['id', 'created_on', 'updated_on',
                                  'status', 'vm_name', 'vm_uuid']
        for r in obj:
            row = list()
            for h in header:
                row.append(r[h])
            _append(row)
    lines = tabulate(lines, headers=header, tablefmt=tbfmt)
    return lines


def print_vm_attr(obj, uuid=None, attr_list=None, **kwargs):
    lines = []
    _append = lines.append
    _extend = lines.extend
    if uuid:
        _append(columns_two_kv.format('Uuid', uuid))
    if not attr_list:
        for i in obj:
            _extend([columns_two_kv.format(k, v) for k, v in i.items()])
        return lines
    # VM attributes
    for a in attr_list:
        if isinstance(a, tuple):
            value = obj[a[0]][a[1]]
            key = ' '.join(a)
        else:
            _val = obj.get(a)
            # validate value
            if isinstance(_val, bool):
                value = _val
            elif _val is None or not _val:
                value = ' '
            else:
                value = _val
            # set key
            key = a

        if value is None:
            value = ' '
        elif isinstance(value, bool):
            value = yes_no(value)
        elif isinstance(value, list):
            value = ', '.join([str(v) for v in value])
        _append(columns_two_kv.format(capitalize(key), value))
    return '\n'.join(lines)


def print_vm_objects_attr(obj, attr_list, uuid=None, **kwargs):
    lines = []
    _append = lines.append
    if uuid:
        _append(columns_two_kv.format('Uuid', uuid))
    for o in obj:
        for a in attr_list:
            if isinstance(a, tuple):
                value = o[a[0]][a[1]]
                key = ' '.join(a)
            else:
                value = o.get(a) or ' '
                key = a

            if isinstance(value, bool):
                value = yes_no(value)
            elif isinstance(value, list):
                value = ', '.join([str(v) for v in value])
            _append(columns_two_kv.format(capitalize(key), value))
    return '\n'.join(lines)


def print_vm_disks_summary(uuid, disks, **kwargs):
    lines = []
    _append = lines.append
    _append(columns_two_kv.format('Uuid', uuid))
    for disk in disks:
        _append(columns_two_kv.format(
            disk['data']['label'],
            '{} GB'.format(disk['data']['capacityGB'])))
    return lines


def print_vm_cds_summary(uuid, cds, **kwargs):
    lines = []
    _append = lines.append
    _append(columns_two_kv.format('Uuid', uuid))
    for cd in cds:
        _append(columns_two_kv.format(
            cd['data']['label'],
            cd['data']['backing']))
    return lines


def print_vm_snaps_summary(uuid, snaps, **kwargs):
    lines = []
    _append = lines.append
    _append(columns_two_kv.format('Uuid', uuid))
    for snap in snaps:
        _append(columns_two_kv.format(
            'Snapshot {}'.format(snap['id']), snap['name']))
    return lines


def print_vm_nics_summary(uuid, nics, **kwargs):
    lines = []
    _append = lines.append
    _append(columns_two_kv.format('Uuid', uuid))
    for nic in nics:
        _append(columns_two_kv.format(
            nic['data']['label'], nic['data']['macAddress']))
    return lines


def print_vm_info(obj, **kwargs):
    vm = obj
    lines = []
    _append = lines.append
    _append(columns_two_kv.format('Uuid', vm['uuid']))
    _append(columns_two_kv.format('Name', vm['name']['full_name']))
    _append(columns_two_kv.format('Folder', vm['folder']['path']))
    _append(columns_two_kv.format('Guest OS', vm['config']['os']['guestId']))
    _append(columns_two_kv.format('Version', vm['hardware']['version']))
    _append(columns_two_kv.format('Status', vm['state']['overallStatus']))
    _append(columns_two_kv.format('State',
                                  vm['state']['powerState']))
    _append(columns_two_kv.format('Alarms', yes_no(vm['state']['alarms'])))
    _append(columns_two_kv.format('CPU/Memory (GB)', '{}/{}'.format(
        vm['hardware']['cpu']['cpuCount'],
        vm['hardware']['memory']['memoryGB'])))
    _append(columns_two_kv.format('Provisioned (GB)',
                                  vm['storage']['provisionedGB']))
    _append(columns_two_kv.format('Snapshot', yes_no(vm['snapshot']['exist'])))
    _append(columns_two_kv.format('Admin', vm['vss'].get('admin') or 'N/A'))
    disks = vm['hardware']['devices']['disks']
    _append(columns_two_kv.format('Disks', len(disks)))
    nics = vm['hardware']['devices']['nics']
    _append(columns_two_kv.format('NICs', len(nics)))
    return '\n'.join(lines)


def dump(obj, _key=None, _list=None):
    for key, value in obj.items():
        if isinstance(value, list):
            for i in value:
                if isinstance(i, dict):
                    dump(i, key, _list)
                else:
                    _list.append(columns_two_kv.format(key, i))
        elif not isinstance(value, dict) and not isinstance(value, list):
            _k = _key + '.' + key
            if isinstance(value, bool):
                value = yes_no(value)
            _list.append(columns_two_kv.format(_k, value))
        elif key not in ['_links']:
            dump(value, key, _list)


def get_all_inv_attrs():
    return {'admin': 'Admin', 'client': 'Client',
            'clientNotes': 'Client Notes',
            'cpu': 'CPU Count', 'diskCount': 'Disk Count',
            'diskTotalSize': 'Disk Total Size',
            'disks': 'Hard Disks',
            'domain': 'Fault Domain',
            'folder': 'Folder',
            'guestOsId': 'Guest OS Id',
            'haGroup': 'HA Group',
            'hardwareVersion': 'Hardware Version',
            'hostName': 'Host Name',
            'inform': 'Inform',
            'ipAddress': 'IP Address',
            'isTemplate': 'Is Template',
            'memory': 'Memory GB',
            'networkIds': 'Network IDs',
            'nicCount': 'NIC Count',
            'nics': 'NICs',
            'osId': 'OS Id',
            'provisionedSpace': 'Provisioned Space',
            'requested': 'Requested',
            'snapshot': 'Snapshot',
            'state': 'State',
            'status': 'Status',
            'uncommittedSpace': 'Uncommitted Space',
            'usedSpace': 'Used Space',
            'vmtRunning': 'VMware Tools Running Status',
            'vmtVersion': 'VMware Tools Version Status'}
