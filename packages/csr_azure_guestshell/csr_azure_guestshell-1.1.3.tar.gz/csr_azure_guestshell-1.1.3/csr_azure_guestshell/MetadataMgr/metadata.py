#!/usr/bin/env python

import os
import json
import urllib2

metadata_file = '/home/guestshell/azure/tools/MetadataMgr/metadata.json'


class MetaData:

    metadata_json = None

    def __init__(self):
        if os.path.exists(metadata_file):
#            print "Found existing metadata in file"
            self.read_metadata_from_file()
#            self.dump_metadata()
        else:
            MetaData.metadata_json = self.get_metadata()
            self.write_metadata_to_file()


    def get_metadata(self):
        headers = {'Metadata': 'true'}
        metadata_url = 'http://169.254.169.254/metadata/instance?api-version=2017-04-02'
        req = urllib2.Request(metadata_url, headers=headers)
        resp = urllib2.urlopen(req)
        resp_read = resp.read()
        data = json.loads(resp_read)
        return data


    def dump_metadata(self):
        print(json.dumps(MetaData.metadata_json, indent=2))

    def write_metadata_to_file(self):
        with open(metadata_file, 'w') as fh:
            fh.write(json.dumps(MetaData.metadata_json, indent=2))

    def read_metadata_from_file(self):
        with open(metadata_file, 'r') as fh:
            MetaData.metadata_json = json.load(fh)

    def pretty_metadata(self):
        for i, interface in enumerate(MetaData.metadata_json["network"]["interface"]):
            print "Port %d" % i
            print "Mac is %s" % interface["macAddress"]
            for j, ip in enumerate(interface["ipv4"]["ipAddress"]):
                print "Public ip is %s" % ip["publicIpAddress"]
                print "Private ip is %s" % ip["privateIpAddress"]
            for s, subnet in enumerate(interface["ipv4"]["subnet"]):
                print "subnet is %s/%s" % (subnet["address"], subnet["prefix"])

    def get_subscriptionId(self):
        subid = ''
        try:
            subid = MetaData.metadata_json["compute"]["subscriptionId"]
        except KeyError:
            subid = ''
        finally:
            return subid

    def get_resourceGroup(self):
        rg = ''
        try:
            rg = MetaData.metadata_json["compute"]["resourceGroupName"]
        except KeyError:
            rg = ''
        finally:
            return rg

    def get_compute_param(self, param):
        param_value = ''
        try:
            param_value =MetaData.metadata_json["compute"][param]
        except KeyError:
            param_value = ''
        finally:
            return param_value

    def get_private_ipaddr(self):
        ipAddr = ''
        try:
            private_interface = MetaData.metadata_json["network"]["interface"][1]
            addr_desc = private_interface["ipv4"]["ipAddress"][0]
            ipAddr =  addr_desc["privateIpAddress"]
        except KeyError:
            ipAddr = ''
        finally:
            return ipAddr


