#!/usr/bin/python
import socket, threading, time, os, datetime, math, sys, getopt, operator, json
from decimal import Decimal
from functools import reduce

class Server(object):
    def __init__(self, host, port, file):
        self.host = host
        self.port = port
        self.file = file
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def stop(self, running):
        if running:
            self.running = False
        print('\nSERVER: Stopping')
        return True

    def listen(self):
        self.sock.listen(5)
        while True:
            # print('SERVER: Waiting for new connection')
            client, address = self.sock.accept()
            client.settimeout(5)
            threading.Thread(target = self.listenToClient,args = (client,)).start()

    def send(self, client):
        ip, port = client.getpeername()
        content = open(self.file, 'rb')
        content = content.read()
        try:
            # print('SERVER: Sent data to '+ip+':'+str(port))
            client.sendall(content)
            return True
        except KeyboardInterrupt:
            print('SERVER: User aborted server in send')
        except Exception as e:
            print('SERVER: Failed connection for '+ip+':'+str(port))
            print(e)
            return False

    def listenToClient(self, client):
        # print('SERVER: Client connected')
        while True:
            try:
                if not self.send(client):
                    client.close()
                    break
            except KeyboardInterrupt:
                print('SERVER: User aborted server in listenToClient')
            except Exception as e:
                # print('SERVER: Client disconnected')
                print(e)
                client.close()
                return False
            time.sleep(2)
            if not self.running:
                break


class SNMP(object):
    def __init__(self, type, host, port, community, file, interval):
        self.type = type
        self.host = host
        self.port = port
        self.community = community
        self.file = file
        self.interval = int(interval)
        self.running = True
        self.acu_models = {
            'intellian_v100': {
                'latitude': '.1.3.6.1.4.1.13745.100.1.1.4.0',
                'longitude': '.1.3.6.1.4.1.13745.100.1.1.5.0',
                'heading': '.1.3.6.1.4.1.13745.100.1.1.6.0',
                'speed': False
            },
            'sailor_900': {
                'latitude': '.1.3.6',
                'longitude': '.1.3.6',
                'heading': '.1.3.6',
                'speed': False
            },
            'seatel_x': {
                'latitude': '.1.3.6',
                'longitude': '.1.3.6',
                'heading': '.1.3.6',
                'speed': False
            }
        }

    def stop(self, running):
        if running:
            self.running = False
        print('\nSNMP: Stopping')
        return True

    def start(self):
        try:
            while self.running:
                # Get data from source
                data = self.collect()

                # Generate NMEA string content
                string = self.nmea(data)

                # Generate NMEA string checksum
                check = self.checksum(string)

                # Build full NEMEA string
                nmeastring = '$'+string+'*'+check

                # Print for debug
                # print('NMEA: '+nmeastring)

                # Save full NMEA string to file
                self.write(nmeastring)

                # Wait for new interval
                for i in range(1, self.interval):
                    i += 1
                    if not self.running:
                        break
                    time.sleep(1)

        except KeyboardInterrupt:
            print('SNMP: Fetching aborted')
            sys.exit(2)
        except Exception as e:
            print('SNMP: Unknown error occured')
            print(e)
            sys.exit(2)

    def get(self, oid):
        try:
            stream = os.popen('/etc/pymea/snmpget -v2c -Ovq -c'+self.community+' '+self.host+' '+oid+' 2>/dev/null')
            output = stream.read().strip().strip('"')
        except Exception as e:
            output = '00.0000 X'
            print('failed to get snmp from acu')
            print(e)
        return output

    def write(self, nmeastring):
        nmeafile = open(self.file, 'w')
        nmeafile.write(nmeastring)
        nmeafile.write('\n')
        nmeafile.close()

    def collect(self):
        data = {}
        values = ['heading', 'latitude', 'longitude', 'speed']
        for value in values:
            if self.acu_models[self.type][value]:
                data[value] = self.get(self.acu_models[self.type][value])
            else:
                data[value] = ''
        #check if acu output needs conversion
        # Rewrite data if not type = intellian_v100
        if not self.type == 'intellian_v100':
            print('SNMP: Trying to rewrite data')
            data_new = 'rewrite data format'
            data = data_new
        return data

    def dms(self, decimal):
        fract,whole = math.modf(decimal)
        seconds,minutes = math.modf(abs(fract) * 60)
        degree = whole*100+minutes
        result = degree+minutes+seconds
        array = str(Decimal(result)).split('.')
        prefix = array[0]
        if len(array) != 2:
            suffix = '0000'
        else:
            if len(array[1]) < 4:
                suffix = str(array[1]).ljust(4, '0')
            if len(array[1]) > 4:
                suffix = str(array[1][0:4])
        return prefix+'.'+suffix

    def checksum(self, string):
        string = string.strip().strip('$\n')
        checksum = reduce(operator.xor, (ord(s) for s in string), 0)
        return '{:02x}'.format(checksum).upper()

    def nmea(self, data):
        TYPE      = 'GPRMC'
        TIMESTAMP = datetime.datetime.now().strftime('%H%M%S') #HHMMSS
        STATUS    = 'A' #A=Valid, V=Invalid
        LATITUDE  = str(self.dms(float(data['latitude'].split(' ')[0]))) #ddmm.mmmm
        LATIND    = data['latitude'].split(' ')[1] #N=North, S=South
        LONGITUDE = str(self.dms(float(data['longitude'].split(' ')[0]))) #dddmm.mmmm
        LONGIND   = data['longitude'].split(' ')[1] #W=West, E=East
        SPEED     = str(data['speed']) #Speed over ground
        COURSE    = str(data['heading']) #Course over ground (heading?)
        DATE      = str(datetime.datetime.now().strftime('%d%m%y')) #DDMMYY
        MAGNETIC  = str(0) #Magnetic Variation in degrees (E=East, W=West)
        MODE      = 'A' #A=Autonomous, D=DGPS, E=DR

        string = TYPE+','+TIMESTAMP+','+STATUS+','+LATITUDE+','+LATIND+','+LONGITUDE+','+LONGIND+','+SPEED+','+COURSE+','+DATE+','+MAGNETIC+','+MODE+','
        return string

if __name__ == '__main__':
    print('MAIN: Starting')
    lfile = '/tmp/data.file'
    lport = int(5555)
    file = False

    try:
        opts, args = getopt.getopt(sys.argv[1:],'h:c:a:p:f:i:',['host=','community=','acu=','port=','file','interval'])
    except getopt.GetoptError:
        print('ERROR: Bad arguments. See below example:')
        print('getgps.py -h 10.224.77.2 -c public -a intellian_v100 -p 161')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--host'):
            host = arg
        elif opt in ('-c', '--community'):
            community = arg
        elif opt in ('-a', '--acu'):
            acu = arg
        elif opt in ('-p', '--port'):
            port = arg
        elif opt in ('-f', '--file'):
            file = arg
        elif opt in ('-i', '--interval'):
            interval = arg

    # Init PID file
    with open('/var/run/pymea.pid', 'w') as pidfile:
        try:
            pid = str(os.getpid())
        except Exception as e:
            print('ERROR: Failed to get PID')
            print(e)
            sys.exit(2)
        try:
            pidfile.write(pid)
            pidfile.close()
        except Exception as e:
            print('ERROR: Failed to save PID')
            print(e)
            sys.exit(2)

    # Check if config file has been specified
    if file:
        # Read values from config file
        try:
            configdata = open(file, 'r')
        except FileNotFoundError:
            print('ERROR: Config file not found ('+file+')')
            sys.exit(2)
        except Exception as e:
            print('ERROR: Could not read config file')
            print(e)
            sys.exit(2)
        try:
            config = json.loads(configdata.read().replace('\n', ''))
            configdata.close()
        except Exception as e:
            print('ERROR: Failed to load config data')
            print(e)
            sys.exit(2)
        # Transalte config to variables
        acu = config['acu']
        host = config['host']
        port = config['port']
        community = config['community']
        interval = config['interval']
    else:
        # If not config file check amount of parameters
        if len(sys.argv) != 11:
            print('ERROR: Missing arguments. See below example:')
            print('getgps.py -h 10.224.77.2 -c public -a intellian_v100 -p 161')
            sys.exit(2)


    # Init SNMP
    print('MAIN: Configure SNMP')
    snmp = SNMP(acu, host, port, community, lfile, interval)

    # Start thread to fetch data
    print('MAIN: Setup thread for fetching')
    snmpthread = threading.Thread(target = snmp.start)
    print('MAIN: Start SNMP')
    try:
        snmpthread.start()
    except KeyboardInterrupt:
        print('\nMAIN: SNMP fetching aborted by user')
        snmp.stop(True)
    except Exception as e:
        print('\nMAIN: SNMP fetching error')
        print(e)
        snmp.stop(True)

    print('MAIN: Configure SERVER')
    server = Server('', lport, lfile)
    print('MAIN: Start SERVER')
    try:
        server.listen()
    except KeyboardInterrupt:
        snmp.stop(True)
        server.stop(True)
    except Exception as e:
        print('\nMAIN: SERVER had an unknown error')
        print(e)
        snmp.stop(True)
        server.stop(True)

    print('\nMAIN: Application has stopped')
