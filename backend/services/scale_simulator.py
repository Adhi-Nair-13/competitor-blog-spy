import asyncio
import time
import random
from typing import Dict, Any, List
from datetime import datetime, timezone

class ScaleSimulator:
    """
    Demonstrates and benchmarks asynchronous 100-website monitoring concurrency.
    Runs simulated website checks through an asyncio worker queue pool,
    exercising error isolation, concurrent workers, rate limiting, and response timing.
    """

    def __init__(self):
        self.is_running = False
        self.total_targets = 100
        self.concurrent_workers = 15
        self.active_workers = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.queued_tasks = 0
        self.response_times: List[float] = []
        self.logs: List[Dict[str, Any]] = []
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def get_status(self) -> Dict[str, Any]:
        avg_resp = (sum(self.response_times) / len(self.response_times)) if self.response_times else 0.0
        elapsed = 0.0
        if self.started_at:
            now = self.completed_at or datetime.now(timezone.utc)
            elapsed = (now - self.started_at).total_seconds()

        throughput = (self.completed_tasks / elapsed) if elapsed > 0 else 0.0

        return {
            "is_running": self.is_running,
            "total_targets": self.total_targets,
            "concurrent_workers": self.concurrent_workers,
            "active_workers": self.active_workers,
            "queued_tasks": self.queued_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "avg_response_time_ms": round(avg_resp, 2),
            "elapsed_seconds": round(elapsed, 2),
            "throughput_checks_per_sec": round(throughput, 2),
            "recent_logs": self.logs[-20:],
        }

    async def start_simulation(self, total_targets: int = 100, workers: int = 15):
        if self.is_running:
            return {"message": "Simulation is already running"}

        self.is_running = True
        self.total_targets = total_targets
        self.concurrent_workers = workers
        self.active_workers = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.response_times = []
        self.logs = []
        self.started_at = datetime.now(timezone.utc)
        self.completed_at = None

        queue = asyncio.Queue()
        for i in range(1, total_targets + 1):
            queue.put_nowait({
                "id": i,
                "name": f"Competitor Site #{i:03d}.com",
                "strategy": random.choice(["RSS + Sitemap", "RSS", "Sitemap", "Direct Page"]),
            })
        self.queued_tasks = queue.qsize()

        # Launch worker tasks
        worker_tasks = [
            asyncio.create_task(self._worker(queue, worker_id=w + 1))
            for w in range(workers)
        ]

        asyncio.create_task(self._wait_for_completion(queue, worker_tasks))
        return {"status": "started", "targets": total_targets, "workers": workers}

    async def _worker(self, queue: asyncio.Queue, worker_id: int):
        while self.is_running:
            try:
                task_data = queue.get_nowait()
            except asyncio.QueueEmpty:
                break

            self.queued_tasks = queue.qsize()
            self.active_workers += 1

            start_t = time.perf_counter()
            site_name = task_data["name"]
            # Simulate real-world network latency (30ms - 250ms)
            sim_latency = random.uniform(0.04, 0.22)
            # Inject realistic occasional failure (e.g. 4% network/timeout error)
            is_failure = random.random() < 0.04

            await asyncio.sleep(sim_latency)

            resp_ms = round((time.perf_counter() - start_t) * 1000, 2)
            self.response_times.append(resp_ms)

            if is_failure:
                self.failed_tasks += 1
                status = "FAILED"
                err = random.choice(["HTTP 504 Gateway Timeout", "DNS resolution failed", "HTTP 429 Rate Limit"])
            else:
                self.completed_tasks += 1
                status = "SUCCESS"
                err = None

            self.logs.append({
                "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3],
                "worker_id": worker_id,
                "site": site_name,
                "strategy": task_data["strategy"],
                "status": status,
                "response_time_ms": resp_ms,
                "error": err,
            })

            self.active_workers -= 1
            queue.task_done()

    async def _wait_for_completion(self, queue: asyncio.Queue, worker_tasks: List[asyncio.Task]):
        await queue.join()
        for t in worker_tasks:
            t.cancel()
        self.is_running = False
        self.completed_at = datetime.now(timezone.utc)
        self.active_workers = 0
        self.queued_tasks = 0

scale_simulator = ScaleSimulator()
