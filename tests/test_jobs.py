from datetime import UTC, datetime
from decimal import Decimal

from yarl import URL

from apolo_api_client.jobs import (
    Container,
    DiskVolume,
    HTTPPort,
    Job,
    JobPriority,
    JobRestartPolicy,
    JobStatus,
    JobStatusHistory,
    JobStatusItem,
    Resources,
    SecretFile,
    Volume,
    job_from_api,
)


async def test_job_from_api() -> None:
    data = {
        "id": "test-job-id",
        "org_name": "test-org",
        "project_name": "test-project",
        "name": "test-name",
        "status": "running",
        "description": "This is job description, not a history description",
        "http_url": "http://my_host:8889",
        "scheduler_enabled": True,
        "preemptible_node": True,
        "pass_config": True,
        "owner": "test-owner",
        "cluster_name": "default",
        "preset_name": "test-preset",
        "internal_hostname": "test-internal-job",
        "internal_hostname_named": "test-internal-job-named",
        "schedule_timeout": 3600,
        "uri": "job://default/owner/job-id",
        "total_price_credits": "10.01",
        "price_credits_per_hour": "20",
        "restart_policy": "always",
        "max_run_time_minutes": 60,
        "tags": ["test-tag"],
        "priority": "high",
        "materialized": True,
        "being_dropped": True,
        "logs_removed": True,
        "container": {
            "image": "test-image-name",
            "command": "test-command",
            "entrypoint": "test-entrypoint",
            "working_dir": "test-working-dir",
            "http": {"port": 8181},
            "resources": {
                "memory": 4096 * 2**20,
                "cpu": 7.0,
                "shm": True,
                "nvidia_gpu": 1,
                "tpu": {"type": "v3-8", "software_version": "1.14"},
            },
            "tty": True,
            "env": {
                "TEST_ENV": "TEST_VALUE",
            },
            "secret_env": {
                "TEST_SECRET": "secret://test-user/secret",
            },
            "volumes": [
                {
                    "src_storage_uri": "storage://test-user/path_read_only",
                    "dst_path": "/container/read_only",
                    "read_only": True,
                },
            ],
            "secret_volumes": [
                {
                    "src_secret_uri": "secret://test-user/secret",
                    "dst_path": "/container/read_only",
                    "read_only": True,
                },
            ],
            "disk_volumes": [
                {
                    "src_disk_uri": "disk://test-user/path_read_only",
                    "dst_path": "/container/read_only",
                    "read_only": True,
                },
            ],
        },
        "statuses": [
            {
                "status": "pending",
                "transition_time": "2025-03-26T09:10:10+00:00",
                "reason": "Creating",
            },
        ],
        "history": {
            "status": "running",
            "created_at": "2025-03-26T09:10:10+00:00",
            "started_at": "2025-03-26T09:10:14+00:00",
            "finished_at": "2025-03-26T09:10:18+00:00",
            "run_time_seconds": 4.168895,
            "restarts": 0,
        },
    }

    assert job_from_api(data) == Job(
        id="test-job-id",
        name="test-name",
        org_name="test-org",
        project_name="test-project",
        description="This is job description, not a history description",
        status=JobStatus.RUNNING,
        history=JobStatusHistory(
            status=JobStatus.RUNNING,
            created_at=datetime(2025, 3, 26, 9, 10, 10, tzinfo=UTC),
            started_at=datetime(2025, 3, 26, 9, 10, 14, tzinfo=UTC),
            finished_at=datetime(2025, 3, 26, 9, 10, 18, tzinfo=UTC),
            restarts=0,
            run_time_seconds=4.168895,
            transitions=[
                JobStatusItem(
                    status=JobStatus.PENDING,
                    reason="Creating",
                    transition_time=datetime(2025, 3, 26, 9, 10, 10, tzinfo=UTC),
                )
            ],
        ),
        http_url=URL("http://my_host:8889"),
        scheduler_enabled=True,
        preemptible_node=True,
        pass_config=True,
        owner="test-owner",
        cluster_name="default",
        uri=URL("job://default/owner/job-id"),
        total_price_credits=Decimal("10.01"),
        price_credits_per_hour=Decimal("20"),
        preset_name="test-preset",
        schedule_timeout=3600,
        life_span=3600,
        restart_policy=JobRestartPolicy.ALWAYS,
        internal_hostname="test-internal-job",
        internal_hostname_named="test-internal-job-named",
        tags=["test-tag"],
        materialized=True,
        being_dropped=True,
        logs_removed=True,
        priority=JobPriority.HIGH,
        container=Container(
            image="test-image-name",
            command="test-command",
            entrypoint="test-entrypoint",
            working_dir="test-working-dir",
            http=HTTPPort(port=8181, requires_auth=False),
            tty=True,
            resources=Resources(
                cpu=7.0,
                memory=4096 * 2**20,
                shm=True,
                nvidia_gpu=1,
                tpu_type="v3-8",
                tpu_software_version="1.14",
            ),
            env={
                "TEST_ENV": "TEST_VALUE",
            },
            secret_env={
                "TEST_SECRET": URL("secret://test-user/secret"),
            },
            volumes=[
                Volume(
                    storage_uri=URL("storage://test-user/path_read_only"),
                    container_path="/container/read_only",
                    read_only=True,
                )
            ],
            disk_volumes=[
                DiskVolume(
                    disk_uri=URL("disk://test-user/path_read_only"),
                    container_path="/container/read_only",
                    read_only=True,
                )
            ],
            secret_files=[
                SecretFile(
                    secret_uri=URL("secret://test-user/secret"),
                    container_path="/container/read_only",
                )
            ],
        ),
    )
