"""
Forge - Core Example
Demonstrates basic Forge functionality for building and composing agent workflows.
"""

from forge import Forge, Workflow, Step

def main():
    # Initialize Forge
    forge = Forge()

    # Define a workflow with steps
    workflow = Workflow(name="data-pipeline")

    # Add processing steps
    workflow.add_step(Step("extract", description="Extract raw data from source"))
    workflow.add_step(Step("transform", description="Clean and transform data"))
    workflow.add_step(Step("load", description="Load data to destination"))

    # Execute the workflow
    result = forge.run(workflow, params={
        "source": "s3://my-bucket/raw",
        "destination": "postgres://localhost/analytics"
    })

    print(f"Workflow status: {result.status}")
    print(f"Steps completed: {result.steps_completed}")

if __name__ == "__main__":
    main()
