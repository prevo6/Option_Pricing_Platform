from datetime import datetime
from airflow.decorators import dag
from airflow.providers.docker.operators.docker import DockerOperator

@dag(
    start_date=datetime(2026, 9, 9),
    schedule="@daily",
    catchup=False,
    tags=["alpaca_worker"],
)
def alpaca_worker() -> None:

    run_alpaca_pipeline = DockerOperator(
        task_id="run_alpaca_pipeline",
        image="option-pricing-etl:latest",
        command="python -m etl_scripts.alpaca.alp_etl",
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


alpaca_worker()
