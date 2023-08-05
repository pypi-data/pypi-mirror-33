# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import pulumi
import pulumi.runtime

class AnalyticsSolution(pulumi.CustomResource):
    """
    Manages a new Log Analytics (formally Operational Insights) Solution.
    """
    def __init__(__self__, __name__, __opts__=None, location=None, plan=None, resource_group_name=None, solution_name=None, workspace_name=None, workspace_resource_id=None):
        """Create a AnalyticsSolution resource with the given unique name, props, and options."""
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

        if not plan:
            raise TypeError('Missing required property plan')
        elif not isinstance(plan, dict):
            raise TypeError('Expected property plan to be a dict')
        __self__.plan = plan
        """
        A `plan` block as documented below.
        """
        __props__['plan'] = plan

        if not resource_group_name:
            raise TypeError('Missing required property resource_group_name')
        elif not isinstance(resource_group_name, basestring):
            raise TypeError('Expected property resource_group_name to be a basestring')
        __self__.resource_group_name = resource_group_name
        """
        The name of the resource group in which the Log Analytics solution is created. Changing this forces a new resource to be created. Note: The solution and it's related workspace can only exist in the same resource group.
        """
        __props__['resourceGroupName'] = resource_group_name

        if not solution_name:
            raise TypeError('Missing required property solution_name')
        elif not isinstance(solution_name, basestring):
            raise TypeError('Expected property solution_name to be a basestring')
        __self__.solution_name = solution_name
        """
        Specifies the name of the solution to be deployed. See [here for options](https://docs.microsoft.com/en-us/azure/log-analytics/log-analytics-add-solutions).Changing this forces a new resource to be created.
        """
        __props__['solutionName'] = solution_name

        if not workspace_name:
            raise TypeError('Missing required property workspace_name')
        elif not isinstance(workspace_name, basestring):
            raise TypeError('Expected property workspace_name to be a basestring')
        __self__.workspace_name = workspace_name
        __props__['workspaceName'] = workspace_name

        if not workspace_resource_id:
            raise TypeError('Missing required property workspace_resource_id')
        elif not isinstance(workspace_resource_id, basestring):
            raise TypeError('Expected property workspace_resource_id to be a basestring')
        __self__.workspace_resource_id = workspace_resource_id
        """
        The full resource ID of the Log Analytics workspace with which the solution will be linked. Changing this forces a new resource to be created.
        """
        __props__['workspaceResourceId'] = workspace_resource_id

        super(AnalyticsSolution, __self__).__init__(
            'azure:operationalinsights/analyticsSolution:AnalyticsSolution',
            __name__,
            __props__,
            __opts__)

    def set_outputs(self, outs):
        if 'location' in outs:
            self.location = outs['location']
        if 'plan' in outs:
            self.plan = outs['plan']
        if 'resourceGroupName' in outs:
            self.resource_group_name = outs['resourceGroupName']
        if 'solutionName' in outs:
            self.solution_name = outs['solutionName']
        if 'workspaceName' in outs:
            self.workspace_name = outs['workspaceName']
        if 'workspaceResourceId' in outs:
            self.workspace_resource_id = outs['workspaceResourceId']
