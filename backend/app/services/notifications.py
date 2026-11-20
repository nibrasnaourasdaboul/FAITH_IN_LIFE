import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification, UserNotificationState


# يحفظ إشعاراً ويربطه بالمستخدم حتى يظهر في حسابه.
async def notify_user(
    session: AsyncSession,
    user_id: uuid.UUID,
    title: str,
    body: str,
    kind: str,
    dedupe_key: str | None = None,
) -> Notification:
    note = Notification(
        notification_type=kind,
        title=title,
        body=body,
        priority="normal",
        schedule_status="published",
        publish_at=datetime.now(timezone.utc),
        dedupe_key=dedupe_key,
    )
    session.add(note)
    await session.flush()
    session.add(
        UserNotificationState(
            notification_id=note.notification_id,
            user_id=user_id,
            read_flag=False,
            archived=False,
        )
    )
    return note
