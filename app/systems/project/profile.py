from systems.project import provisioner
from utility.data import ensure_list


class ProjectProfile(
    provisioner.ConfigProvisionerMixin,
    provisioner.ProjectProvisionerMixin,
    provisioner.NetworkProvisionerMixin
):
    def __init__(self, project, data):
        self.project = project
        self.command = project.command
        self.data = data
        
        self.ensure_configs()
        self.ensure_projects()
        self.load_parents()
        

    def provision(self, params = {}):
        self.data = self.get_schema()

        self.set_config(params)
        self.ensure_networks()
        self.ensure_network_peers()
        self.ensure_firewalls()
        self.ensure_subnets()


    def destroy(self):
        self.data = self.get_schema()
        
        self.destroy_subnets()
        self.destroy_firewalls()
        self.destroy_network_peers()
        self.destroy_networks()


    def load_parents(self):
        self.parents = []
        if 'parents' in self.data:
            for parent in ensure_list(self.data['parents']):
                project = self.get_project(parent['project'])
                self.parents.append(project.provider.get_profile(parent['profile']))

    def get_parents(self):
        parents = []
        for profile in self.parents:
            parents.extend(profile.get_parents())
            parents.append(profile)
        return parents


    def get_schema(self):
        schema = {}
        for profile in self.parents:
            self.merge_schema(schema, profile.get_schema())
        self.merge_schema(schema, self.data)
        return schema

    def merge_schema(self, schema, data):
        for key, value in data.items():
            if isinstance(value, dict):
                schema.setdefault(key, {})
                self.merge_schema(schema[key], value)
            else:
                schema[key] = value
