from subprocess import PIPE, Popen
from threading import Timer
from uuid import getnode
import os
import psutil


SMART_MODEL_ID = 2795


class NoUIDException(Exception):
    pass


def _get_mac():
    return str(getnode())


def _get_serial():
    # Extract serial from cpuinfo file
    cs = None

    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            if line[0:6] == 'Serial':
                cs = line[14:26]
    f.close()
    if cs:
        cs = ''.join(['AAA', cs.upper()])
    return cs


def _get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE,
                    universal_newlines=True)
    output, _error = process.communicate()
    temp = float(output.split('=')[1].split("'")[0])
    return temp if not _error else None


def _get_voltage():
    process = Popen(['vcgencmd', 'measure_volts', 'core'], stdout=PIPE,
                    universal_newlines=True)
    output, _error = process.communicate()
    volts = float(output.split('=')[1].split('V')[0])
    return volts if not _error else None


def _get_top_5_processes():
    # Top-5 processes in terms of virtual memory usage.
    processes = sorted(
        ((p.memory_info().vms, p) for p in psutil.process_iter()),
        key=lambda x: x[0],
        reverse=True
    )
    return [[p[0], p[1].pid, p[1].name()] for p in processes[:5]]


def _get_mem_usage(basic=False):
    vm = psutil.virtual_memory()
    if basic:
        return {
            'percent': vm.percent
        }
    return {
        'total': vm.total,
        'used': vm.used,
        'free': vm.free,
        'percent': vm.percent
    }


def _get_disk_usage(basic=False):
    disk = psutil.disk_usage('/')
    if basic:
        return {
            'percent': disk.percent,
        }
    return {
        'total': disk.total,
        'used': disk.used,
        'free': disk.free,
        'percent': disk.percent,
    }


# ------------------------------------------------------------------[ Public ]--
def _do_reboot(mqttc):
    mqttc.disconnect()
    os.system('sudo reboot')


def reboot(mqttc):
    Timer(10, _do_reboot, [mqttc]).start()


def get_uid():
    uid = _get_serial()
    if not uid:
        uid = _get_mac()
    if not uid:
        raise NoUIDException
    return uid


def collect_data(basic=False):

    try:
        result = {
            'volts': _get_voltage(),
            'cpu_tmp': _get_cpu_temperature(),
            'cpu_usg': psutil.cpu_percent(),
            'mem': _get_mem_usage(basic=basic),
            'disk': _get_disk_usage(basic=basic),
        }
        # if not basic:
        #     result['top_5_proc'] = _get_top_5_processes()
    except FileNotFoundError:
        result = {}
    return result
