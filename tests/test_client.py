from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Callable

import aiohttp
import aiohttp.web
import pytest
from yarl import URL

from apolo_api_client.client import ApiClient


@asynccontextmanager
async def create_local_app_server(
    app: aiohttp.web.Application, port: int = 8080
) -> AsyncIterator[URL]:
    runner = aiohttp.web.AppRunner(app)
    try:
        await runner.setup()
        url = URL(f"http://127.0.0.1:{port}")
        site = aiohttp.web.TCPSite(runner, url.host, url.port)
        await site.start()
        yield url
    finally:
        await runner.shutdown()
        await runner.cleanup()


@pytest.fixture
def job() -> dict[str, Any]:
    return {
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


@pytest.fixture
def api_token() -> str:
    return "test-api-token"


@pytest.fixture
async def api_server(
    unused_tcp_port_factory: Callable[[], int], job: dict[str, Any], api_token: str
) -> AsyncIterator[URL]:
    async def _handle_get_jobs(request: aiohttp.web.Request) -> aiohttp.web.Response:
        assert request.headers["Authorization"] == f"Bearer {api_token}"
        return aiohttp.web.json_response({"jobs": [job]})

    async def _handle_get_job(request: aiohttp.web.Request) -> aiohttp.web.Response:
        assert request.headers["Authorization"] == f"Bearer {api_token}"
        return aiohttp.web.json_response(job)

    app = aiohttp.web.Application()
    app.add_routes(
        [
            aiohttp.web.get("/api/v1/jobs", _handle_get_jobs),
            aiohttp.web.get("/api/v1/jobs/{id}", _handle_get_job),
        ]
    )

    async with create_local_app_server(app, port=unused_tcp_port_factory()) as address:
        yield URL(f"http://{address.host}:{address.port}")


@pytest.fixture
async def api_client(api_server: URL, api_token: str) -> AsyncIterator[ApiClient]:
    async with ApiClient(api_server, api_token) as client:
        yield client


async def test_get_job(api_client: ApiClient) -> None:
    job = await api_client.get_job("test-job-id")

    assert job.id == "test-job-id"


async def test_iter_jobs(api_client: ApiClient) -> None:
    async with api_client.iter_jobs() as gen:
        jobs = [j async for j in gen]

    assert jobs[0].id == "test-job-id"
