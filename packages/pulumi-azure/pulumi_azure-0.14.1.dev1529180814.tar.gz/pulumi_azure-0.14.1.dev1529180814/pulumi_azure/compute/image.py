# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import pulumi
import pulumi.runtime

class Image(pulumi.CustomResource):
    """
    Create a custom virtual machine image that can be used to create virtual machines.
    """
    def __init__(__self__, __name__, __opts__=None, data_disks=None, location=None, name=None, os_disk=None, resource_group_name=None, source_virtual_machine_id=None, tags=None):
        """Create a Image resource with the given unique name, props, and options."""
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, basestring):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        if data_disks and not isinstance(data_disks, list):
            raise TypeError('Expected property data_disks to be a list')
        __self__.data_disks = data_disks
        """
        One or more `data_disk` elements as defined below.
        """
        __props__['dataDisks'] = data_disks

        if not location:
            raise TypeError('Missing required property location')
        elif not isinstance(location, basestring):
            raise TypeError('Expected property location to be a basestring')
        __self__.location = location
        """
        Specified the supported Azure location where the resource exists.
        Changing this forces a new resource to be created.
        """
        __props__['location'] = location

        if name and not isinstance(name, basestring):
            raise TypeError('Expected property name to be a basestring')
        __self__.name = name
        """
        Specifies the name of the image. Changing this forces a
        new resource to be created.
        """
        __props__['name'] = name

        if os_disk and not isinstance(os_disk, dict):
            raise TypeError('Expected property os_disk to be a dict')
        __self__.os_disk = os_disk
        """
        One or more `os_disk` elements as defined below.
        """
        __props__['osDisk'] = os_disk

        if not resource_group_name:
            raise TypeError('Missing required property resource_group_name')
        elif not isinstance(resource_group_name, basestring):
            raise TypeError('Expected property resource_group_name to be a basestring')
        __self__.resource_group_name = resource_group_name
        """
        The name of the resource group in which to create
        the image. Changing this forces a new resource to be created.
        """
        __props__['resourceGroupName'] = resource_group_name

        if source_virtual_machine_id and not isinstance(source_virtual_machine_id, basestring):
            raise TypeError('Expected property source_virtual_machine_id to be a basestring')
        __self__.source_virtual_machine_id = source_virtual_machine_id
        """
        The Virtual Machine ID from which to create the image.
        """
        __props__['sourceVirtualMachineId'] = source_virtual_machine_id

        if tags and not isinstance(tags, dict):
            raise TypeError('Expected property tags to be a dict')
        __self__.tags = tags
        """
        A mapping of tags to assign to the resource.
        """
        __props__['tags'] = tags

        super(Image, __self__).__init__(
            'azure:compute/image:Image',
            __name__,
            __props__,
            __opts__)

    def set_outputs(self, outs):
        if 'dataDisks' in outs:
            self.data_disks = outs['dataDisks']
        if 'location' in outs:
            self.location = outs['location']
        if 'name' in outs:
            self.name = outs['name']
        if 'osDisk' in outs:
            self.os_disk = outs['osDisk']
        if 'resourceGroupName' in outs:
            self.resource_group_name = outs['resourceGroupName']
        if 'sourceVirtualMachineId' in outs:
            self.source_virtual_machine_id = outs['sourceVirtualMachineId']
        if 'tags' in outs:
            self.tags = outs['tags']
