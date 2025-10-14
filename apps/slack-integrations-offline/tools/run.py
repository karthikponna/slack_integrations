from datetime import datetime as dt
from pathlib import Path
from typing import Any

import click

from pipelines import (
    collect_crawl_data
)


@click.command(
    help="""
    Just a command"""
)
@click.option(
    "--run-collect-crawl-data-pipeline",
    is_flag=True,
    default=False,
    help="Whether to run the collect crawled data from pipeline.",
)
def main(
    run_collect_crawl_data_pipeline: bool = False,
) -> None:
    
    pipeline_args: dict[str, Any] = {
        "enable_cache": False,
    }
    root_dir = Path(__file__).resolve().parent.parent


    if run_collect_crawl_data_pipeline:
        run_args = {}
        pipeline_args["config_path"] = root_dir / "configs" / "collect_crawl_data.yaml"
        assert pipeline_args["config_path"].exists(), (
            f"Config file not found: {pipeline_args['config_path']}"
        )
        pipeline_args["run_name"] = f"testing_run_{dt.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        collect_crawl_data.with_options(**pipeline_args)(**run_args)


if __name__ == "__main__":
    main()