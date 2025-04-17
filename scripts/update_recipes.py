import os
from pathlib import Path
from instill.clients import init_pipeline_client
from dotenv import load_dotenv


def get_pipeline_id(yaml_path):
    """Extract pipeline ID from YAML filename by removing extension"""
    return os.path.splitext(os.path.basename(yaml_path))[0]


def update_recipes():
    # Load environment variables from .env file
    load_dotenv()

    # Initialize the pipeline client
    token = os.environ.get("INSTILL_CORE_API_TOKEN")
    if not token:
        raise ValueError("INSTILL_CORE_API_TOKEN not found in environment variables")

    pipeline = init_pipeline_client(
        api_token=token,
        url="localhost:8080",
        secure=False
    )

    # Get all YAML files from the recipes directory
    recipes_dir = Path(__file__).parent / "pipelines"
    yaml_files = list(recipes_dir.glob("*.yaml"))

    print(f"Found {len(yaml_files)} YAML recipes to sync")

    try:
        for yaml_path in yaml_files:
            pipeline_id = get_pipeline_id(yaml_path)
            print(f"\nDeploying pipeline: {pipeline_id}")

            # Read the YAML file
            with open(yaml_path, 'r') as f:
                raw_recipe = f.read()

            # Update the pipeline
            try:
                pipeline.update_pipeline(
                    namespace_id="admin",
                    pipeline_id=pipeline_id,
                    description="",
                    raw_recipe=raw_recipe
                )

                print(f"Successfully updated {pipeline_id}")
            except Exception as e:
                print(f"Error updating {pipeline_id}: {str(e)}")

    finally:
        pipeline.close()


if __name__ == "__main__":
    update_recipes()
