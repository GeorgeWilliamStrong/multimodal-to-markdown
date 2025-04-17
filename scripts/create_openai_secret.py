import os
import dotenv
from instill.clients import init_pipeline_client


def create_openai_secret():
    # Load environment variables from .env file
    dotenv.load_dotenv()

    # Get the OpenAI API key from environment variables
    openai_api_key = os.environ.get("OPENAI_API_TOKEN")
    if not openai_api_key:
        print("Error: OPENAI_API_TOKEN not found in .env file")
        return

    # Get the Instill API token from environment variables
    instill_token = os.environ.get("INSTILL_CORE_API_TOKEN")
    print('instill_token', instill_token)
    if not instill_token:
        print("Error: INSTILL_CORE_API_TOKEN not found in .env file")
        return

    # Initialize the pipeline client
    pipeline = init_pipeline_client(
        api_token=instill_token,
        url="localhost:8080",
        secure=False
    )

    try:
        # Create the OpenAI secret
        pipeline.create_secret(
            namespace_id="admin",
            secret_id="openai",
            description="OpenAI API token for pipeline components",
            value=openai_api_key,
        )
        print("Successfully created 'openai' secret")
    except Exception as e:
        print(f"Error creating secret: {str(e)}")
    finally:
        pipeline.close()


if __name__ == "__main__":
    create_openai_secret()