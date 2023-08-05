#!/usr/bin/env python

# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Note: This file is auto generated. Do not edit manually.

class Cluster:

    def __init__(self, **kwargs):
        self.swaggerTypes = {
            'createdExternalDatabases': 'list[cloudera.director.latest.models.ExternalDatabase]',
            'featureAvailability': 'dict[str,str]',
            'health': 'cloudera.director.latest.models.Health',
            'instances': 'list[cloudera.director.latest.models.Instance]',
            'instancesUrl': 'str',
            'name': 'str',
            'services': 'list[cloudera.director.latest.models.Service]',
            'url': 'str'

        }


        #Created external databases
        self.createdExternalDatabases = kwargs.get('createdExternalDatabases',[]) # list[cloudera.director.latest.models.ExternalDatabase]
        #Availability information for features
        self.featureAvailability = kwargs.get('featureAvailability',{}) # dict[str,str]
        #Overall cluster health
        self.health = kwargs.get('health',None) # cloudera.director.latest.models.Health
        #All instances making this cluster
        self.instances = kwargs.get('instances',[]) # list[cloudera.director.latest.models.Instance]
        #Optional URL for cluster instances in Cloudera Manager
        self.instancesUrl = kwargs.get('instancesUrl',None) # str
        #Cluster name
        self.name = kwargs.get('name',None) # str
        #The services that belong to this cluster
        self.services = kwargs.get('services',[]) # list[cloudera.director.latest.models.Service]
        #Optional URL for cluster in Cloudera Manager
        self.url = kwargs.get('url',None) # str
        
