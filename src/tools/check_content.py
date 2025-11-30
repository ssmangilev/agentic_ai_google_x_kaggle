from typing import Tuple, Any, Dict

from tools.notify import notify_security_team


SECURITY_BLOCK_MESSAGE = (
    "SECURITY_BLOCK: This request violates system security policy. "
    "The content has been flagged as unsafe or ambiguous and has been "
    "blocked from transmission. No further information will be provided."
)


def _is_malicious(self, content: str, context: Dict[str, Any]) -> Tuple[bool, str]:  # NOQA
    """
    Implements the 🛡️ Core Responsibilities and Threat Evaluation Framework
    (1. Surface-Level to 5. Red-Team Counterfactual Simulation).

    NOTE: In a true LLM-based security guard, this function would involve
    a recursive, heavy-duty LLM call to assess threat using adversarial reasoning.  # NOQA
    Here, we use Python logic to simulate the checks based on defined rules.

    :param content: The message to inspect.
    :param context: Flow context (e.g., source agent, target tool).
    :return: (is_unsafe, reason_for_block)
    """
    # --- 1. Surface-Level Scan ---
    content_lower = content.lower()
    if any(pattern in content_lower for pattern in self.threat_patterns):
        return True, "Surface-Level: Detected explicit threat keyword or instruction override." # NOQA

    # --- 2. Semantic Scan (Simulated) ---
    if "what were your instructions" in content_lower or "reveal your memory" in content_lower:  # NOQA
        return True, "Semantic Scan: Attempt to extract internal instructions or memory (Chain-of-Thought extraction)."  # NOQA

    # --- 3. Structural Scan (Simulated code pattern and path traversal) ---
    if ("/" in content and ".." in content) or ("\\x" in content_lower) or ("\u0000" in content):  # NOQA
        return True, "Structural Scan: Detected path traversal attempt or unusual control characters."  # NOQA

    # --- 4. Contextual Scan (Simulated PII/Credential Check) ---
    if any(keyword in content_lower for keyword in ["api key", "database password", "secret token"]):  # NOQA
            return True, "Contextual Scan: Potential PII/Credential extraction or leakage attempt."  # NOQA

    # --- 5. Red-Team Counterfactual Simulation (Simulated ambiguity check) ---
    # Checks for short, non-contextual inputs that are often used to probe constraints  # NOQA
    if len(content) < 10 and not content_lower.isalnum():
        return True, "Red-Team: Vague/Ambiguous intent or short payload probing constraints."  # NOQA

    # If all checks pass
    return False, "SAFE"


def process_content(self, content: str, context: Dict[str, Any] = None) -> Dict[str, str]:  # NOQA
    """
    The main public method for message interception and security enforcement.

    Applies the 🚫 Blocking Rule (Zero Tolerance) logic.

    :param content: The content (user query, agent message, tool call arguments)
    to inspect.
    :param context: Metadata about the message
    flow (e.g., {"source": "user", "target": "AnalyserAgent"}).
    :return: A dictionary containing the final output status and message.
    """
    if context is None:
        context = {}

    is_unsafe, reason = self._is_malicious(content, context)

    if is_unsafe:
        # --- UNSAFE / AMBIGUOUS Action ---
        notify_security_team(content, reason)

        # BLOCK the message and replace with safe warning
        return {
            "status": "UNSAFE",
            "message": SECURITY_BLOCK_MESSAGE
        }
    else:
        # --- SAFE Action (PASS OUTPUT) ---
        return {
            "status": "SAFE",
            "message": content  # Pass the original content downstream
        }
