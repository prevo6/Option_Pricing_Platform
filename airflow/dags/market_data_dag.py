from airflow.sdk import dag, task
from datetime import datetime
from airflow.providers.docker.operators.docker import DockerOperator

PATH_TO_EXTERNAL_PYTHON = "/Users/andrewprevo/Desktop/Option_Pricing_Platform/.venv/bin/python"

@dag(
    start_date=datetime(2026, 9, 9),
    schedule="@weekly", #run weekly because of free api limits
    catchup=False,
    tags=["md_worker"],
)
def md_worker() -> None:
 
    run_md_pipeline = DockerOperator(
        task_id="run_md_pipeline",
        image="option-pricing-etl:latest",
        command="python -m etl_scripts.market_data.md_etl",
        environment={
            "DB_HOST": "host.docker.internal",
            "DB_USER": "postgres",
            "DB_PASSWORD": "postgres",
            "DB_NAME": "options_db",
        },
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        auto_remove="success",
        mount_tmp_dir=False,
    )


md_worker()