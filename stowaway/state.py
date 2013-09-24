# -*- coding: utf-8 -*-
import os
import datetime
import uuid

from fabric.api import env

import micromodels
from microcollections.collections import Collection, RawCollection
from microcollections.filestores import DirectoryFileStore

from .datastores import JSONFileDataStore


class Node(micromodels.Model):
    name = micromodels.CharField()
    hostname = micromodels.CharField()
    created = micromodels.DateTimeField(default=datetime.datetime.now)
    memory_capacity = micromodels.IntegerField(required=False, help_text='In bytes')
    cpu_capacity = micromodels.IntegerField(required=False, help_text='CPU Shares')

    def get_instances(self):
        return appCollection.find(node=self.hostname)

    def can_fit(self, memory, cpu):
        instances = self.get_instances()

        for instance in instances:
            memory += instance.memory or 0

        for instance in instances:
            cpu += instance.cpu or 0

        if self.memory_capacity and self.memory_capacity < memory:
            return False

        if self.cpu_capacity and self.cpu_capacity < cpu:
            return False

        return True


class DockerInstance(micromodels.Model):
    container_id = micromodels.CharField()
    machine_name = micromodels.CharField()
    image_name = micromodels.CharField()
    memory = micromodels.IntegerField(required=False, help_text='In bytes')
    cpu = micromodels.IntegerField(required=False, help_text='CPU Shares')
    paths = micromodels.FieldCollectionField(micromodels.CharField())


class AppInstance(DockerInstance):
    appname = micromodels.CharField()


class Balancer(micromodels.Model):
    name = micromodels.CharField()
    endpoint_uri = micromodels.CharField()
    redis_uri = micromodels.CharField()


class Application(micromodels.Model):
    name = micromodels.CharField()
    image_name = micromodels.CharField()
    balancer_name = micromodels.CharField()
    #environ = micromodels.PrimitiveField(default=dict)


def id_maker():
    return uuid.uuid4().hex


#CONSIDER: make lazy
datastore = JSONFileDataStore(path=os.path.join(env.WORK_DIR, 'db'))
filestore = DirectoryFileStore(os.path.join(env.WORK_DIR, 'filestore'))
nodeCollection = Collection(Node, data_store=datastore, file_store=filestore,
    object_id_field='name')
instanceCollection = Collection(DockerInstance, data_store=datastore,
    file_store=filestore, object_id_field='container_id')
configCollection = RawCollection(name='config', data_store=datastore,
    file_store=filestore)
balancerCollection = Collection(Balancer, data_store=datastore,
    file_store=filestore, object_id_field='name')
appCollection = Collection(Application, data_store=datastore,
    file_store=filestore, id_generator=id_maker)

