import typer
from dotenv import load_dotenv

from szymonmiks_deployment.factory import DeploymentManagerFactory


def main(deployment_type: str) -> None:
    """
    deployment_type - two possible values: blog or website
    """
    load_dotenv()

    if deployment_type == "blog":
        deployment_manager = DeploymentManagerFactory.for_blog()
        deployment_manager.deploy()
        return

    if deployment_type == "website":
        deployment_manager = DeploymentManagerFactory.for_website()
        deployment_manager.deploy()
        return

    raise ValueError(f"Unknown deployment_type: {deployment_type}")


if __name__ == "__main__":
    typer.run(main)
