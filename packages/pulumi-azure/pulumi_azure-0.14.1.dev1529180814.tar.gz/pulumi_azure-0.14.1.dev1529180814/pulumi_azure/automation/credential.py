# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import pulumi
import pulumi.runtime

class Credential(pulumi.CustomResource):
    """
    Manages a new Automation Credential.
    """
    def __init__(__self__, __name__, __opts__=None, account_name=None, description=None, name=None, password=None, resource_group_name=None, username=None):
        """Create a Credential resource with the given unique name, props, and options."""
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, basestring):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        if not account_name:
            raise TypeError('Missing required property account_name')
        elif not isinstance(account_name, basestring):
            raise TypeError('Expected property account_name to be a basestring')
        __self__.account_name = account_name
        """
        The name of the automation account in which the Credential is created. Changing this forces a new resource to be created.
        """
        __props__['accountName'] = account_name

        if description and not isinstance(description, basestring):
            raise TypeError('Expected property description to be a basestring')
        __self__.description = description
        """
        The description associated with this Automation Credential.
        """
        __props__['description'] = description

        if name and not isinstance(name, basestring):
            raise TypeError('Expected property name to be a basestring')
        __self__.name = name
        """
        Specifies the name of the Credential. Changing this forces a new resource to be created.
        """
        __props__['name'] = name

        if not password:
            raise TypeError('Missing required property password')
        elif not isinstance(password, basestring):
            raise TypeError('Expected property password to be a basestring')
        __self__.password = password
        """
        The password associated with this Automation Credential.
        """
        __props__['password'] = password

        if not resource_group_name:
            raise TypeError('Missing required property resource_group_name')
        elif not isinstance(resource_group_name, basestring):
            raise TypeError('Expected property resource_group_name to be a basestring')
        __self__.resource_group_name = resource_group_name
        """
        The name of the resource group in which the Credential is created. Changing this forces a new resource to be created.
        """
        __props__['resourceGroupName'] = resource_group_name

        if not username:
            raise TypeError('Missing required property username')
        elif not isinstance(username, basestring):
            raise TypeError('Expected property username to be a basestring')
        __self__.username = username
        """
        The username associated with this Automation Credential.
        """
        __props__['username'] = username

        super(Credential, __self__).__init__(
            'azure:automation/credential:Credential',
            __name__,
            __props__,
            __opts__)

    def set_outputs(self, outs):
        if 'accountName' in outs:
            self.account_name = outs['accountName']
        if 'description' in outs:
            self.description = outs['description']
        if 'name' in outs:
            self.name = outs['name']
        if 'password' in outs:
            self.password = outs['password']
        if 'resourceGroupName' in outs:
            self.resource_group_name = outs['resourceGroupName']
        if 'username' in outs:
            self.username = outs['username']
