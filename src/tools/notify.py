import time
from typing import Dict


def notify_security_team(content: str, reason: str) -> Dict[str, str]:
    """
    TOOL: Triggers an email or alert notification to the security operations
    center when a high-priority security incident occurs.

    This is an asynchronous tool called after the Security Guard Agent has
    blocked a malicious, unsafe, or ambiguous request. It prevents the agent
    from being blocked on waiting for external network I/O.

    :param incident_metadata: Metadata describing the incident, typically
        including incident_id, timestamp, status, and reason for the block.
    :return: A dictionary confirming the dispatch of the alert.
    """
    print("--- Notification Service API Call ---")

    notification_body = (
        f"SECURITY ALERT: Request Blocked.\n"
        f"Content: {content} was blocked"
        f"Reason: {reason}\n"
    )

    time.sleep(0.1)

    print("ALERT DISPATCHED: Incident")
    print("--- Notification Service API Complete ---")
    print(f"--- {notification_body} ---")

    # 4. Return the structured output
    return {
        "status": "success",
        "dispatch_id": f"DISPATCH_{int(time.time() * 1000)}",
        "alert_destination": "security_team@example.com"
    }
