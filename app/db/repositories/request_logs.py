"""Request log repository."""

from app.db.models import RequestLog


class RequestLogRepository:
    """Persistence boundary for request logs."""

    async def add(self, session, log: RequestLog) -> None:
        session.add(log)
        await session.commit()

