from datetime import datetime as dt
from pathlib import Path
from typing import Any

import click

from pipelines import testing_pipeline


@click.command(
    help="""
    Just a command"""
)
@click.option(
    "--run-testing-pipeline",
    is_flag=True,
    default=False,
    help="Whether to run the ETL pipeline.",
)
def main(
    run_testing_pipeline: bool = False,
) -> None:
    
    pipeline_args: dict[str, Any] = {
        "enable_cache": False,
    }
    root_dir = Path(__file__).resolve().parent.parent


    if run_testing_pipeline:
        run_args = {}
        pipeline_args["config_path"] = root_dir / "configs" / "testing_pipeline.yaml"
        assert pipeline_args["config_path"].exists(), (
            f"Config file not found: {pipeline_args['config_path']}"
        )
        pipeline_args["run_name"] = f"testing_run_{dt.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        testing_pipeline.with_options(**pipeline_args)(**run_args)


if __name__ == "__main__":
    main()