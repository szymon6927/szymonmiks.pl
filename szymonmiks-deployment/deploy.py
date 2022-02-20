from szymonmiks_deployment.factory import DeploymentManagerFactory

if __name__ == "__main__":
    deployment_manager = DeploymentManagerFactory.create()
    deployment_manager.deploy()
