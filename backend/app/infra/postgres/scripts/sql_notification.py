GET_ALL_NOTIFICATION = """
    SELECT * FROM notification;
"""

GET_UNREAD_NOTIFICATION = """
    SELECT * FROM notification WHERE read_status = FALSE;
"""

GET_NOTIFICATION_BY_ID = """
    SELECT * FROM notification WHERE id = $1;
"""

NOTIFICATION_CREATE = """
    INSERT INTO notification (title, message, type, device_id, read_status, ts) VALUES ($1, $2, $3, $4, $5, $6) RETURNING id, title, message, type, device_id, read_status, ts;
"""

NOTIFICATION_MARK_ALL_AS_READ = """
    UPDATE notification SET read_status = TRUE;
"""

NOTIFICATION_MARK_AS_READ = """
    UPDATE notification SET read_status = TRUE WHERE id = $1 RETURNING id;
"""

NOTIFICATION_DELETE_ALL = """
    DELETE FROM notification;
"""

NOTIFICATION_DELETE = """
    DELETE FROM notification WHERE id = $1 RETURNING id;
"""
