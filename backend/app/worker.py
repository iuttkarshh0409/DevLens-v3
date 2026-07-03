import asyncio
from app.jobs import shared_queue
from app.jobs.worker import Worker
from app.core.logging import logger

async def main():
    logger.info("Initializing background worker process...")
    worker = Worker(queue=shared_queue)
    await worker.start()

if __name__ == "__main__":
    asyncio.run(main())
