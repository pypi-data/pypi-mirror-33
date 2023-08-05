# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import pulumi
import pulumi.runtime

class Blob(pulumi.CustomResource):
    """
    Create an Azure Storage Blob.
    """
    def __init__(__self__, __name__, __opts__=None, attempts=None, name=None, parallelism=None, resource_group_name=None, size=None, source=None, source_uri=None, storage_account_name=None, storage_container_name=None, type=None):
        """Create a Blob resource with the given unique name, props, and options."""
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, basestring):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        if attempts and not isinstance(attempts, int):
            raise TypeError('Expected property attempts to be a int')
        __self__.attempts = attempts
        """
        The number of attempts to make per page or block when uploading. Defaults to `1`.
        """
        __props__['attempts'] = attempts

        if name and not isinstance(name, basestring):
            raise TypeError('Expected property name to be a basestring')
        __self__.name = name
        """
        The name of the storage blob. Must be unique within the storage container the blob is located.
        """
        __props__['name'] = name

        if parallelism and not isinstance(parallelism, int):
            raise TypeError('Expected property parallelism to be a int')
        __self__.parallelism = parallelism
        """
        The number of workers per CPU core to run for concurrent uploads. Defaults to `8`.
        """
        __props__['parallelism'] = parallelism

        if not resource_group_name:
            raise TypeError('Missing required property resource_group_name')
        elif not isinstance(resource_group_name, basestring):
            raise TypeError('Expected property resource_group_name to be a basestring')
        __self__.resource_group_name = resource_group_name
        """
        The name of the resource group in which to
        create the storage container. Changing this forces a new resource to be created.
        """
        __props__['resourceGroupName'] = resource_group_name

        if size and not isinstance(size, int):
            raise TypeError('Expected property size to be a int')
        __self__.size = size
        """
        Used only for `page` blobs to specify the size in bytes of the blob to be created. Must be a multiple of 512. Defaults to 0.
        """
        __props__['size'] = size

        if source and not isinstance(source, basestring):
            raise TypeError('Expected property source to be a basestring')
        __self__.source = source
        """
        An absolute path to a file on the local system. Cannot be defined if `source_uri` is defined.
        """
        __props__['source'] = source

        if source_uri and not isinstance(source_uri, basestring):
            raise TypeError('Expected property source_uri to be a basestring')
        __self__.source_uri = source_uri
        """
        The URI of an existing blob, or a file in the Azure File service, to use as the source contents
        for the blob to be created. Changing this forces a new resource to be created. Cannot be defined if `source` is defined.
        """
        __props__['sourceUri'] = source_uri

        if not storage_account_name:
            raise TypeError('Missing required property storage_account_name')
        elif not isinstance(storage_account_name, basestring):
            raise TypeError('Expected property storage_account_name to be a basestring')
        __self__.storage_account_name = storage_account_name
        """
        Specifies the storage account in which to create the storage container.
        Changing this forces a new resource to be created.
        """
        __props__['storageAccountName'] = storage_account_name

        if not storage_container_name:
            raise TypeError('Missing required property storage_container_name')
        elif not isinstance(storage_container_name, basestring):
            raise TypeError('Expected property storage_container_name to be a basestring')
        __self__.storage_container_name = storage_container_name
        """
        The name of the storage container in which this blob should be created.
        """
        __props__['storageContainerName'] = storage_container_name

        if type and not isinstance(type, basestring):
            raise TypeError('Expected property type to be a basestring')
        __self__.type = type
        """
        The type of the storage blob to be created. One of either `block` or `page`. When not copying from an existing blob,
        this becomes required.
        """
        __props__['type'] = type

        __self__.url = pulumi.runtime.UNKNOWN
        """
        The URL of the blob
        """

        super(Blob, __self__).__init__(
            'azure:storage/blob:Blob',
            __name__,
            __props__,
            __opts__)

    def set_outputs(self, outs):
        if 'attempts' in outs:
            self.attempts = outs['attempts']
        if 'name' in outs:
            self.name = outs['name']
        if 'parallelism' in outs:
            self.parallelism = outs['parallelism']
        if 'resourceGroupName' in outs:
            self.resource_group_name = outs['resourceGroupName']
        if 'size' in outs:
            self.size = outs['size']
        if 'source' in outs:
            self.source = outs['source']
        if 'sourceUri' in outs:
            self.source_uri = outs['sourceUri']
        if 'storageAccountName' in outs:
            self.storage_account_name = outs['storageAccountName']
        if 'storageContainerName' in outs:
            self.storage_container_name = outs['storageContainerName']
        if 'type' in outs:
            self.type = outs['type']
        if 'url' in outs:
            self.url = outs['url']
