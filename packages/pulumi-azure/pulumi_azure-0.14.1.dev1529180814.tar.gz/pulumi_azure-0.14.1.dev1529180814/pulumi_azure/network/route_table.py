# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import pulumi
import pulumi.runtime

class RouteTable(pulumi.CustomResource):
    """
    Manages a Route Table
    """
    def __init__(__self__, __name__, __opts__=None, location=None, name=None, resource_group_name=None, routes=None, tags=None):
        """Create a RouteTable resource with the given unique name, props, and options."""
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, basestring):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        if not location:
            raise TypeError('Missing required property location')
        elif not isinstance(location, basestring):
            raise TypeError('Expected property location to be a basestring')
        __self__.location = location
        """
        Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        """
        __props__['location'] = location

        if name and not isinstance(name, basestring):
            raise TypeError('Expected property name to be a basestring')
        __self__.name = name
        """
        The name of the route.
        """
        __props__['name'] = name

        if not resource_group_name:
            raise TypeError('Missing required property resource_group_name')
        elif not isinstance(resource_group_name, basestring):
            raise TypeError('Expected property resource_group_name to be a basestring')
        __self__.resource_group_name = resource_group_name
        """
        The name of the resource group in which to create the route table. Changing this forces a new resource to be created.
        """
        __props__['resourceGroupName'] = resource_group_name

        if routes and not isinstance(routes, list):
            raise TypeError('Expected property routes to be a list')
        __self__.routes = routes
        """
        Can be specified multiple times to define multiple routes. Each `route` block supports fields documented below.
        """
        __props__['routes'] = routes

        if tags and not isinstance(tags, dict):
            raise TypeError('Expected property tags to be a dict')
        __self__.tags = tags
        """
        A mapping of tags to assign to the resource.
        """
        __props__['tags'] = tags

        __self__.subnets = pulumi.runtime.UNKNOWN
        """
        The collection of Subnets associated with this route table.
        """

        super(RouteTable, __self__).__init__(
            'azure:network/routeTable:RouteTable',
            __name__,
            __props__,
            __opts__)

    def set_outputs(self, outs):
        if 'location' in outs:
            self.location = outs['location']
        if 'name' in outs:
            self.name = outs['name']
        if 'resourceGroupName' in outs:
            self.resource_group_name = outs['resourceGroupName']
        if 'routes' in outs:
            self.routes = outs['routes']
        if 'subnets' in outs:
            self.subnets = outs['subnets']
        if 'tags' in outs:
            self.tags = outs['tags']
