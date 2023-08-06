from Cryptodome.Hash import SHA1
from binascii import unhexlify
import base64
import struct
import time
import datetime
import os
import errno
import json
# noinspection PyCompatibility
from http.client import HTTPSConnection
from base64 import b64encode


HOST = 'smart.trintel.co.za'
PATH = '/api/device_management/mqtt_auto_reg'



def get_now_timestamp():
    d = datetime.datetime.now()
    return int(time.mktime(d.timetuple()))


def to_little_endian(i):
    return struct.pack('<I', i)


def get_salt():
    sys_ts = int(get_now_timestamp())
    return to_little_endian(sys_ts)


def hash_password(password):
    salt = get_salt()
    sha1 = SHA1.new()
    sha1.update(salt + password)
    s1 = salt + sha1.digest()
    hash_pw = base64.b64encode(s1)
    return hash_pw.decode('utf-8')


def _gen_unit_key(pk, pid, uid, msg):

    loc = '/opt/trinity/trinqtt'
    dir_name = os.path.dirname(loc)
    try:
        os.makedirs(dir_name)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    if not os.path.exists(loc):
        os.mknod(loc)

    # Write the password
    password = unhexlify(pk)
    with open(loc, 'bw+') as f:
        f.write(password)
    f.close()
    os.chmod(loc, 0o644)

    # Write the Customer ID (Profile key)
    cid_loc = loc + '.cid'
    with open(cid_loc, 'w+') as cid_f:
        cid_f.write(pid)
    cid_f.close()
    os.chmod(loc, 0o644)

    print("""
Done.
Your PROFILE_ID is: {pid} 
Your UID(Device Unique ID) is: {uid} 
{msg}""".format(uid=uid, pid=pid, msg=msg))


def _auto_reg(u, p, uid, customer_id, model_id):
    conn = HTTPSConnection(HOST)

    payload = {'model_id': model_id}
    if customer_id:
        payload["target_customer_id"] = customer_id

    headers = {
        'content-type': 'application/json',
        'authorization': 'Basic {auth}'.format(
            auth=b64encode(bytes('{u}:{p}'.format(u=u, p=p), 'utf-8')).decode(
                'ascii')),
        'cache-control': 'no-cache'}
    conn.request(
        'POST', '{p}/{u}/'.format(p=PATH, u=uid),
        json.dumps(payload),
        headers
    )
    res = conn.getresponse()
    data = json.loads(res.read().decode('utf-8'))
    return data


def auto_register(username, password, model, customer_id=None):
    uid = model.get_uid()
    model_id = model.SMART_MODEL_ID

    if uid and model_id:
        print('UID={u}'.format(u=uid))
        rep = None
        try:
            rep = _auto_reg(username, password, uid, customer_id, model_id)
            if rep:
                err = rep.get('err', None)
                if err:
                    print(err)
                else:
                    uid = rep.get('uid', None)
                    pk = rep.get('pk', None)
                    pid = rep.get('pid', None)
                    msg = rep.get('msg', None)
                    if pk and pid and uid:
                        _gen_unit_key(pk, pid, uid, msg)
                    else:
                        print('Could not generate password')
        except Exception as x:
            print('Could not register and create password: {x}:{rep}'.format(
                x=x, rep=rep))
    else:
        print('Could not find unit UID or Model ID')


def read_password():
    LOC = '/opt/trinity/trinqtt'
    with open(LOC, 'br') as f:
        pw = f.readline().strip()
    f.close()
    return pw


def read_cid():
    LOC = '/opt/trinity/trinqtt.cid'
    with open(LOC, 'r') as f:
        cid = f.readline().strip()
    f.close()
    return cid


def get_password():
    h = hash_password(read_password())
    return h