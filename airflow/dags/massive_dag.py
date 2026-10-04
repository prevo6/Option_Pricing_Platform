from datetime import datetime
from airflow.sdk import dag, task
from airflow.providers.docker.operators.docker import DockerOperator


@dag(start_date=datetime(2026, 9, 10), #configure start date to be whatever you want
    schedule="@daily",
    catchup=False,
    tags=["massive_worker"],)

def massive_worker() -> None:
   
    run_massive_pipeline = DockerOperator(
        task_id="run_massive_pipeline",
        image="option-pricing-etl:latest",
        command="python -m etl_scripts.massive.massive_etl",
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


massive_worker()