#!/usr/bin/env python
from os.path import expanduser
import os
import configparser
import random
import json
import time
import logging
from os.path import expanduser
import errno
from logging.handlers import RotatingFileHandler
from csr_cloud import metric_utils
from csr_cloud import file_utils

AI_URLBASE = "https://api.applicationinsights.io/{version}/apps/{appId}/{operation}/"
API_VERSION = 'v1'

instanceType = 'localMachine'
try:
    # this is to be able to run the code in non-CSR device
    import cli
    instanceType = 'csr1000v'
except Exception as e:
    print("Not able to import cli module. Exception {}".format(e))
    pass

class cas():
    def __init__(self):

        self.load_env()

        self.metric = metric_utils.MetricUtils("autoscaler")
        self.fileutils = file_utils.StorageFileUtils(os.environ['AZURE_STORAGE_NAME'], os.environ['AZURE_STORAGE_KEY'], 'azure')
        self.logger = self.setup_logging('autoscaler')

    def load_env(self):

        config = configparser.ConfigParser()
        config.optionxform = str
        home = expanduser("~")
        filename = home + '/.azure/credentials'
        if not os.path.exists(filename):
            self.storage_acct_name = None
            if os.path.isfile("/bootflash/azure/decodedCustomData"):
                decodedFile = "/bootflash/azure/decodedCustomData"
            elif os.path.isfile("/bootflash/azure/decodedCustomData.txt"):
                decodedFile = "/bootflash/azure/decodedCustomData.txt"
            else:
                return False
            with open(decodedFile) as f:
                for line in f:
                    if 'strgacctname' in line:
                       self.storage_acct_name = line.split()[1]
                    if 'strgacckey' in line:
                        self.storage_acct_key = line.split()[1]
                    if 'transitvnetname' in line:
                        self.share_name = line.split()[1]
            if self.storage_acct_name:
                self.fileutils = file_utils.StorageFileUtils(self.storage_acct_name,
                                                             self.storage_acct_key, 'azure')
                self.mkdir_p(expanduser("~")+'/.azure/')
                self.fileutils.get_file_to_path(self.share_name, 'AutoScaler', 'credentials', filename)
            else:
                return False

        if not os.path.isfile(filename):
            return False

        config.read(filename)
        for key in config['default']:
            value = config.get('default', key)
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            if value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            os.environ[key] = str(value)

        return True

    def mkdir_p(self, path):
        try:
            os.makedirs(path, exist_ok=True)  # Python>3.2
        except TypeError:
            try:
                os.makedirs(path)
            except OSError as exc:
                if exc.errno == errno.EEXIST and os.path.isdir(path):
                    pass
                else:
                    raise

    def setup_logging(self, feature):
        try:
            home = expanduser("~")
            directory = home + '/' + feature + '/' + 'logs'
            path = directory + '/'
            self.mkdir_p(path)
            logfile_name = feature + '.log'
            hdlr = RotatingFileHandler(os.path.join(directory, logfile_name), mode='a', maxBytes=5 * 1024 * 1024,
                                       backupCount=2, encoding=None, delay=0)

            formatter = logging.Formatter(
                '%(module)15s:%(funcName)25s:%(lineno)4s %(asctime)s %(levelname)s %(message)s')
            hdlr.setFormatter(formatter)
            log = logging.getLogger(feature)
            if not len(log.handlers):
                log.addHandler(hdlr)
            log.setLevel(logging.DEBUG)
            return log
        except Exception as e:
            print("setup_logging: exception {}. ".format(e))
            pass



    def download_file(self, remote_directory, remote_filename, directory="/bootflash/"):
        try:
            self.fileutils.get_file_to_path(self.share_name, remote_directory, remote_filename, local_path)

        except Exception as e:
            print "Config File Download Failed.  Error: %s" % (e)
            return False
        print "\nDownload Complete"
        return True

    def upload_file(self, containername, filename, directory="/bootflash/"):
        self.fileutils.upload_file_to_container(containername, filename, directory)

    def save_cmd_output(self, cmdlist, filename, container=None, directory="/bootflash/", print_output=False):

        with open(directory + filename, 'w') as f:
            for command in cmdlist:
                cmd_output = cli.execute(command)
                col_space = (80 - (len(command))) / 2
                if print_output is True:
                    print "\n%s %s %s" % ('=' * col_space, command, '=' * col_space)
                    print "%s \n%s" % (cmd_output, '=' * 80)

                f.write("\n%s %s %s\n" %
                        ('=' * col_space, command, '=' * col_space))
                f.write("%s \n%s\n" % (cmd_output, '=' * 80))
        if container is not None:
            self.fileutils.upload_file_to_container(container, filename)

    def get_metric(self, name, instanceId=None):
        dimensions = None
        if id is not None:
            dimensions = { 'InstanceId' : instanceId }
        return self.metric.get_metric(name, dimensions=dimensions)


    def put_metric(self, name, value, instanceId=None, instanceName=None):
        dimensions = {
            "InstanceType" : instanceType,
            "InstanceId" : instanceId,
            "instanceName" : instanceName,

        }
        try:
            self.metric.put_metric(name, value, dimensions)
            return True
        except Exception as e:
            self.logger.exception(e)

    def put_event_metric(self, eventName, value, instanceId=None):
        dimensions = {
            "InstanceType": instanceType,
            "instanceId": instanceId
        }
        try:
            self.metric.put_event(eventName, value, dimensions)
            return True
        except Exception as e:
            self.logger.exception(e)

    def get_event_metrics(self, eventName, eventType='customEvents',
                          period='PT24H', query=None):
        return self.metric.get_event_metrics(eventName, eventType,
                                             period, query)

    def flush_metric_queue(self):
        self.metric.flush_metric_queue()

    def test_metrics(self, name, id = None):
        random_number = random.randint(1, 1000)
        instanceId = "none" if id == None else id
        instanceName = 'myMac'

        self.put_metric(name, random_number, instanceId, instanceName)
        self.flush_metric_queue()
        self.logger.info("Put Metric %d" % random_number)

        y = 0
        while True:
            dict = self.get_metric(name, instanceId)
            print json.dumps(dict, indent=4)
            for segment in dict['value']['segments']:
                print "Value: %d, looking for %d" % (int(segment['customMetrics/%s' % name]['avg']), int(random_number))
                if int(segment['customMetrics/%s' % name]['avg']) == random_number:
                    print "Found it after %d tries" % y
                    return
            y = y + 1
            time.sleep(1)

    def test_event_metrics(self, eventname, devicetype = None, deviceid = None):
        import random
        import json
        import time

        random_number = random.randint(1, 1000)
        devicetype = "1mac" if devicetype == None else devicetype
        deviceid = "none" if deviceid == None else deviceid
        dimensions = {"device": devicetype, "id": deviceid}
        print("sending metric event name {} value {} dimensions {}".format(eventname,
                                                                     random_number,
                                                                     dimensions))
        self.put_event_metrics(eventname, random_number, dimensions)
        self.flush_metric_queue()
        print "Put Metric %d" % random_number

        y = 0
        while True:
            metrics = self.get_event_metrics(eventname)
            if metrics is not None:
                #print "metrics {}".format(metrics)
                d = json.loads(metrics)
                #print json.dumps(d['value'], indent=4)
                for event in d['value']:
                    if event['customDimensions']['id'] == deviceid and \
                       event['customDimensions']['device'] == devicetype:
                        print "Value: %d, looking for %d" % (int(event['customMeasurements']['value']),
                                                                 int(random_number))
                        if int(event['customMeasurements']['value']) == random_number:
                            print "Found it after %d tries" % y
                            return
            y = y + 1
            time.sleep(1)

if __name__ == "__main__":
    foo = cas()
    foo.test_metrics("myMetric", "myID")
    #foo.test_event_metrics("customEventsTest")