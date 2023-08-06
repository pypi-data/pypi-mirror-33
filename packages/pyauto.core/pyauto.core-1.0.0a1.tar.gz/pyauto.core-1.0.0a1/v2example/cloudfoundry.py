from pyauto.util import yamlutil


kind_deployment = yamlutil.load_dict("""
kind: cloudfoundry.Deployment
module: v2example.cloudfoundry
attributes:
  cloud_controller: url
  user: envvar
  password: envvar
  client_id_env: envvar optional
  client_secret_env: envvar optional
tasks:
- login
""")


def login(dep, **args):
    pass


kind_space = yamlutil.load_dict("""
kind: cloudfoundry.Space
attributes:
  name: string
  organization: string
""")


kind_application = yamlutil.load_dict("""
kind: cloudfoundry.Application
attributes:
  name: string
  instances: int optional
relations:
  space: cloudfoundry.Space
  source: local.Directory
  bindings: cloudfoundry.Service list
""")


kind_service = yamlutil.load_dict("""
kind: cloudfoundry.Service
attributes:
  name: string
relations:
  space: cloudfoundry.Space
""")


kind_deployment_space = yamlutil.load_dict("""
kind: cloudfoundry.DeploymentSpace
module: v2example.cloudfoundry
relations:
  template: cloudfoundry.Space
  deployment: cloudfoundry.Deployment
tasks:
- deploy_space
- destroy_space
""")


def deploy_space(space, **args):
    pass


def destroy_space(space, **args):
    pass


kind_deployment_service = yamlutil.load_dict("""
kind: cloudfoundry.DeploymentService
attributes:
  name: string
relations:
  template: cloudfoundry.Service
  space: cloudfoundry.DeploymentSpace
""")


kind_deployment_application = yamlutil.load_dict("""
kind: cloudfoundry.DeploymentApplication
class: v2example.cloudfoundry.DeploymentApplication
module: v2example.cloudfoundry
attributes:
  name: string
  manifest: path
relations:
  template: cloudfoundry.Application
  space: cloudfoundry.DeploymentSpace
  workspace: local.Directory
  bindings: cloudfoundry.DeploymentService optional
tasks:
- deploy_app
- wait_app
- destroy_app
- push_app_blue_green
- wait_app_blue_green
""")
