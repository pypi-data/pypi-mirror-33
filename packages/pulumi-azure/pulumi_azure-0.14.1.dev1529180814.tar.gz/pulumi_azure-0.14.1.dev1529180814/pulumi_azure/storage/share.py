# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import pulumi
import pulumi.runtime

class Share(pulumi.CustomResource):
    """
    Create an Azure Storage File Share.
    """
    def __init__(__self__, __name__, __opts__=None, name=None, quota=None, resource_group_name=None, storage_account_name=None):
        """Create a Share resource with the given unique name, props, and options."""
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, basestring):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        if name and not isinstance(name, basestring):
            raise TypeError('Expected property name to be a basestring')
        __self__.name = name
        """
        The name of the share. Must be unique within the storage account where the share is located.
        """
        __props__['name'] = name

        if quota and not isinstance(quota, int):
            raise TypeError('Expected property quota to be a int')
        __self__.quota = quota
        """
        The maximum size of the share, in gigabytes. Must be greater than 0, and less than or equal to 5 TB (5120 GB). Default this is set to 0 which results in setting the quota to 5 TB.
        """
        __props__['quota'] = quota

        if not resource_group_name:
            raise TypeError('Missing required property resource_group_name')
        elif not isinstance(resource_group_name, basestring):
            raise TypeError('Expected property resource_group_name to be a basestring')
        __self__.resource_group_name = resource_group_name
        """
        The name of the resource group in which to
        create the share. Changing this forces a new resource to be created.
        """
        __props__['resourceGroupName'] = resource_group_name

        if not storage_account_name:
            raise TypeError('Missing required property storage_account_name')
        elif not isinstance(storage_account_name, basestring):
            raise TypeError('Expected property storage_account_name to be a basestring')
        __self__.storage_account_name = storage_account_name
        """
        Specifies the storage account in which to create the share.
        Changing this forces a new resource to be created.
        """
        __props__['storageAccountName'] = storage_account_name

        __self__.url = pulumi.runtime.UNKNOWN
        """
        The URL of the share
        """

        super(Share, __self__).__init__(
            'azure:storage/share:Share',
            __name__,
            __props__,
            __opts__)

    def set_outputs(self, outs):
        if 'name' in outs:
            self.name = outs['name']
        if 'quota' in outs:
            self.quota = outs['quota']
        if 'resourceGroupName' in outs:
            self.resource_group_name = outs['resourceGroupName']
        if 'storageAccountName' in outs:
            self.storage_account_name = outs['storageAccountName']
        if 'url' in outs:
            self.url = outs['url']
