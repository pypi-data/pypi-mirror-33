# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import pulumi
import pulumi.runtime

class LocalNetworkGateway(pulumi.CustomResource):
    """
    Manages a new local network gateway connection over which specific connections can be configured.
    """
    def __init__(__self__, __name__, __opts__=None, address_spaces=None, bgp_settings=None, gateway_address=None, location=None, name=None, resource_group_name=None, tags=None):
        """Create a LocalNetworkGateway resource with the given unique name, props, and options."""
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, basestring):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        if not address_spaces:
            raise TypeError('Missing required property address_spaces')
        elif not isinstance(address_spaces, list):
            raise TypeError('Expected property address_spaces to be a list')
        __self__.address_spaces = address_spaces
        """
        The list of string CIDRs representing the
        address spaces the gateway exposes.
        """
        __props__['addressSpaces'] = address_spaces

        if bgp_settings and not isinstance(bgp_settings, dict):
            raise TypeError('Expected property bgp_settings to be a dict')
        __self__.bgp_settings = bgp_settings
        """
        A `bgp_settings` block as defined below containing the
        Local Network Gateway's BGP speaker settings.
        """
        __props__['bgpSettings'] = bgp_settings

        if not gateway_address:
            raise TypeError('Missing required property gateway_address')
        elif not isinstance(gateway_address, basestring):
            raise TypeError('Expected property gateway_address to be a basestring')
        __self__.gateway_address = gateway_address
        """
        The IP address of the gateway to which to
        connect.
        """
        __props__['gatewayAddress'] = gateway_address

        if not location:
            raise TypeError('Missing required property location')
        elif not isinstance(location, basestring):
            raise TypeError('Expected property location to be a basestring')
        __self__.location = location
        """
        The location/region where the local network gatway is
        created. Changing this forces a new resource to be created.
        """
        __props__['location'] = location

        if name and not isinstance(name, basestring):
            raise TypeError('Expected property name to be a basestring')
        __self__.name = name
        """
        The name of the local network gateway. Changing this
        forces a new resource to be created.
        """
        __props__['name'] = name

        if not resource_group_name:
            raise TypeError('Missing required property resource_group_name')
        elif not isinstance(resource_group_name, basestring):
            raise TypeError('Expected property resource_group_name to be a basestring')
        __self__.resource_group_name = resource_group_name
        """
        The name of the resource group in which to
        create the local network gateway.
        """
        __props__['resourceGroupName'] = resource_group_name

        if tags and not isinstance(tags, dict):
            raise TypeError('Expected property tags to be a dict')
        __self__.tags = tags
        """
        A mapping of tags to assign to the resource.
        """
        __props__['tags'] = tags

        super(LocalNetworkGateway, __self__).__init__(
            'azure:network/localNetworkGateway:LocalNetworkGateway',
            __name__,
            __props__,
            __opts__)

    def set_outputs(self, outs):
        if 'addressSpaces' in outs:
            self.address_spaces = outs['addressSpaces']
        if 'bgpSettings' in outs:
            self.bgp_settings = outs['bgpSettings']
        if 'gatewayAddress' in outs:
            self.gateway_address = outs['gatewayAddress']
        if 'location' in outs:
            self.location = outs['location']
        if 'name' in outs:
            self.name = outs['name']
        if 'resourceGroupName' in outs:
            self.resource_group_name = outs['resourceGroupName']
        if 'tags' in outs:
            self.tags = outs['tags']
