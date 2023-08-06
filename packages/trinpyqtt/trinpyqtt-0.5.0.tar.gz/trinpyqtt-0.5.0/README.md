# README #

trinpyqtt is a wrapper around the Paho MQTT python client, and simply extends
it with some convenience functions to facilitate building Smart-MQTT compliant
topics and data structures.
It furthermore contains some crypto tools to manage the username and
passwords as required by the Smart-MQTT brokers.


### What is this repository for? ###

* Use it when you need to connect to a Smart-MQTT broker from a python application
* [Trinity Smart](www.trintel.co.za)

With this client installed, you will be able to:

* Send commands directly to an identifiable RaspberryPi regardless of the connectivity layer. These commands can be sent via the Smart Web UI, or alternatively, via a REST API we can make available to you.
* Write your own code to act on custom built commands particular to your requirements
* If so configured, the client can also regularly posts health data to Smart - data about the underlying hardware. This includes stuff like the CPU temperature, the available disk space, and the top 5 processes currently running on the PI, and memory consumption.
* You can write your own client side checks to monitor the equipment you have connected to the Pi, and make that report to Smart as well
* You can send Smart events when something noteworthy happens at your application layer. These unsolicited events are logged by Smart, but:
* Smart also provides the tools - on the platform side - to build workflow pipelines for events. This can be things like writing the event to one of your Google spreadsheets, sending a Telegram, Pushbullet, Hipchat, or Pushover message to your phone. Or sending an SMS. In fact, our pipeline system is *very* flexible, and we would be able to on-route formatted versions of the events to just about anywhere (with a published API) 

### How do I get set up? ###
To install:
```bash
pip3 install --upgrade trinpyqtt
```
In order for your Raspberry Pi to be able to join the Smart MQTT broker, it need
to pe able to generate a compliant password. This library provides some utility functions
to help you do that:

#### Password ####
In order to connect to the Smart-MQTT brokers, your MQTT client needs to present
a unique username and password.

After you installed the library, but before you can run the sample code, you 
would need to create a password directly on the RaspPi: This needs to be run as 
root, as it needs to write into the /opt directory directly.

__NOTE:__ You need an account on SMART, and your user needs to have "Auto Provision" 
privileges enabled in order for you to perform the next steps.

```bash
sudo python3
```
Then from inside the interpreter
```
Python 3.5.3 (default, Jan 19 2017, 14:11:04) 
[GCC 6.3.0 20170118] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from trinpyqtt.tools.cryptools import auto_register
>>> from trinpyqtt.models import raspberrypi as model
>>> USERNAME = 'your_username_on_smart'
>>> PASSWORD = 'your_login_password_on_smart'
>>> auto_register(USERNAME, PASSWORD, model)
```
it should reply with:
```
    Done. 
    Your PROFILE_ID is: NNNNNNNN 
    Your UID(Device Unique ID) is: XXXXXXXXXXXXXXX 
    This should be added to SMART.
```

Once done, you should (for security purposes) zap your local Python history file. From your terminal just issue:

```bash
> .python_history
```

The above steps will:

* create a password unique to that particular Pi on the /opt/trinity directory (which is why you need root).
That password is read and hashed by the trinpyqtt client every time it connects
to the broker. You should not need to worry about it further. It also will only
work from the hardware on which it was generated. It is not portable.
* create a world readable file with your PROFILE_ID in it. In the past this needed to be passed
into the constructor of the client, but is now read directly from the file system.

#### Identity ####
The client reads some hardware information, to identify itself.
This identity should be seeded on Smart in order to start using Smart.
On a RaspberryPI the identity is derived from the hardware serial number, and
on an Linux box it is derived from the MAC addresses of the NICs.

##### UID #####
To read the identity of the unit:
```bash
python3
```
```python
from trinpyqtt.models.raspberrypi import get_uid
get_uid() # 'XXXXXXXXXXXXXXX'
```
This ID is used by Smart to uniquely identify this hardware, and is called 
the 'Device Unique ID' on that platform.

##### PROFILE_ID #####
To read your PROFILE_ID:
```bash
python3
```
```python
from trinpyqtt.tools.cryptools import read_cid
read_cid() # 'NNNNNNNN'
```
This ID is part of the comms security, and is used to identify all the units on the system
that belong to you. It is sometimes also called a "CID" or "Customer ID."
It has no direct user-application usefulness, and is mentioned here for interest only.

# Sample Application #
This is a sample application showing the use of the client, along with your
own logic. Take note:

* The *APP_ID* constant can be chosen to be any string, but ultimatly needs to tie up with an ASSET_ID on Smart
* When running this application for the first time an __ini__ file will be created in the user's home directory. This file will contain the settings passed in during the constructor (when run the first time). When the application is stopped and restarted, the ini file is read, and takes precedence over the constructor argumants. This is to ensure that any user settings passed to the appplication via a command from Smart is persisted accross reboots.

### Note ###
Once the ini file is created, you need to clear it by hand if you want to start fresh. For instance, if you 
change the broker host in your code, then you need to clear the ini file, as the host setting is persisted there, 
and takes precedence over the arguments passed to the TrinClient constructor.

```python
from trinpyqtt.client import TrinClient
import trinpyqtt.models.raspberrypi as model
import trinpyqtt.tools.constants as MSG_CODES
from time import sleep

# To enable debug logging, in your client uncomment this
# import logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)


# This is used to identify to origin of the messages on the Smart Platform
# It can also called asset id or peripheral id and can be any value, as long as
# it is unique on this particular TrinClient instance. When you want to
# track data and events published from this app, or use Smart to send commands
# to this app, you need to create an 'asset' on Smart with this as
# it's asset id.
APP_ID = 'my_app_id'

# The MQTT broker you are connecting to
HOST = 'localhost'
# HOST = 'mqttdev.trintel.co.za'


# A simple sample RPC
# Given some numbers return their sum
def sum_these(*args):
    code = MSG_CODES.SUCCESS
    try:
        reply = sum(list(args))
    except Exception as ex:
        reply = 'NAC {ex}'.format(ex=ex)
        code = MSG_CODES.F_EXCEPTION
    return code, reply


# The TrinClient is the primary receiver of all messages from the broker,
# and filter those to only expose commands related to this app to be sent to
# this app. A command receiver dictionary can be passed in during construction
# that will map the handling function in your app to its id.
# It is guaranteed that the normalised data that arrives here has been vetted
# for correctness. If the nld data key "code" has any value other than
# a 0 (zero), the given message had errors when vetted.
def process_msg(client, nld, topic, payload, sender):
    if sender == '00000000':
        sender_name = 'Trinity Server'
    else:
        sender_name = sender
    print("""Received command:
    Topic: {topic}
    Payload: {payload}
    From Sender: {sender_name}
    NLD: {nld}
    """.format(topic=topic, payload=payload, nld=nld, sender_name=sender_name))

    # A map of local valid RPCs
    rpcs = {
        'sum_these': sum_these
    }

    # The code will be 0 if the message parse OK
    if nld['code'] > -1:
        if nld['type'] == 'c':
            tct = nld['tct']
            for c, args in nld['command'].items():
                code, result = rpcs[c](*args)
                if tct:
                    client.publish_reply(tct, code, result)


# Instantiate the client
# When 'use_rtc' is set to True the local time on this system will be used
# when publishing. When set to false, the server will use the time it
# receives the message as the canonical timestamp.
daily = 60 * 60 * 24
tc = TrinClient(
    clean_session=False,  # When set to False, the holds on to QoS1 and QoS2
                          # messages destined for this client even after the
                          # client disconnected. When the client then re-
                          # connects, those messages are delivered. When set to
                          # True, the broker discards messages for this client
                          # when it is not connected. Optional, and defaults
                          # to True.
    model=model,          # The type of hardware this is running on. Required
    host=HOST,            # One of Trinity's Smart-MQTT broker urls
    iah_interval=0,       # When set, publish an IaH message this (sec) often
    pdr_interval=daily,   # Ditto for 'device' data messages
    ping_interval=60,     # Set the standard MQTT keepalive (PINGREQ) interval
    use_rtc=False,)       # Let the server manage timestamps

# This can be called once for each 'Asset' on this client.
tc.register_command_receiver(APP_ID, process_msg)

# Un-comment this to enable debug logging
# tc.enable_logger(logger)

# Start the client.
tc.run()

# Simply keep the process running, and publish an event ever so often
counter = 0
while True:
    counter += 1
    print(counter)

    # Once in a while publish an event (Example)
    if not divmod(counter, 15)[1]:
        sse = 0  # Seconds since event occurred. Should be 0 or negative
        event_code = 123  # Should be mapped to your model
        event_description = 'Loop Counter: {c}'.format(c=counter)
        tc.publish_event([sse, event_code, event_description], pid=APP_ID)
        print('Sent event:', event_description)
    sleep(10)

```

To test this setup, assume that this client is connected to a MQTT server on
your local box, then issue this command to produce a "c" message that will
be processed by the example script above:
```bash
mosquitto_pub -d -h localhost -p 1883 -t 'NNNNNNNN/XXXXXXXXXXXXXXX/my_app_id/</' -m '{"c": [123456789,">a_tct", ["sum_these",1,2,3]]}' -q 1
```

# Run as a service #
These are guidelines that worked for us, but you may have wildly differing views
on how to achieve the same. We chose to run this as a _systemd_ service, and these
guidelines may be followed to do the same. However your mileage may vary.

With the setup below, our application is started on system boot, and is run
with the pi user privileges. We furthermore log client messages to 
'/var/log/trinmqtt/trinmqtt.log'

Create a systemd startup service file called "trinmqtt.service"
```bash
sudo vi /etc/systemd/system/trinmqtt.service
```
and add this to the file
```bash
[Unit]
Description=Trinity Smart MQTT Client

[Service]
WorkingDirectory=/home/pi/Workspace
ExecStart=/usr/bin/python3 /home/pi/Workspace/mqtt.py
Restart=always
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=trinmqtt
User=pi
Group=pi

[Install]
WantedBy=multi-user.target
```

Once done and saved enable it by issuing:
```bash
sudo systemctl enable trinmqtt
```

You should now be able to start the service with:
```bash
sudo systemctl start trinmqtt
```

or see its status with:
```bash
sudo systemctl status trinmqtt
```

or to see its logs:
```bash
journalctl -u trinmqtt
```

#### Logging (When run as a service) ####
To make this log out to somewhere else (in addition to the systemd journal):
Choose and create where you would want to log to:
```bash
sudo mkdir /var/log/trinmqtt
sudo touch /var/log/trinmqtt/trinmqtt.log
sudo chown -R pi:pi /var/log/trinmqtt
```
then add a file to the rsyslog.d directory
```bash
sudo vi /etc/rsyslog.d/trinmqtt.conf
```
then in that file tie the name of your service to the required log file
```
if $programname == 'trinmqtt' then /var/log/trinmqtt/trinmqtt.log
if $programname == 'trinmqtt' then stop
```

then restart both the rsyslog service and the trinmqtt service
```bash
sudo systemctl restart rsyslog
sudo systemctl restart trinmqtt
```

You can check that the log file is being written here...
```bash
tail -100f /var/log/trinmqtt/trinmqtt.log 
```

To check the ini file is in the user's directory
```bash
cat ~/.config/trinmqtt/trinmqtt.ini
```


### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* jan@trintel.co.za