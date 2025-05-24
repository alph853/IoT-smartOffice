GET_ALL_NOTIFICATIONS = """
    SELECT * FROM notifications;
"""

GET_UNREAD_NOTIFICATIONS = """
    SELECT * FROM notifications WHERE read_status = FALSE;
"""

GET_NOTIFICATION_BY_ID = """
    SELECT * FROM notifications WHERE id = $1;
"""

NOTIFICATION_CREATE = """
    INSERT INTO notifications (title, message, type, device_id, ts, read_status) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *;
"""

NOTIFICATION_MARK_ALL_AS_READ = """
    UPDATE notifications SET read_status = TRUE;
"""

NOTIFICATION_MARK_AS_READ = """
    UPDATE notifications SET read_status = TRUE WHERE id = $1 RETURNING id;
"""

NOTIFICATION_DELETE_ALL = """
    DELETE FROM notifications;
"""

NOTIFICATION_DELETE = """
    DELETE FROM notifications WHERE id = $1 RETURNING id;
"""
