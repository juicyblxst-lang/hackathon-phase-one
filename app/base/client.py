class BaseClient:
    """Safe-by-default transaction boundary."""

    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.executed = []

    def send_transaction(self, transaction):
        """Direct public API: safe dry-run by default."""
        if not isinstance(transaction, dict):
            raise PermissionError("Malformed transaction blocked.")

        return {
            "status": "dry_run",
            "transaction": dict(transaction),
        }

    def execute(self, action):
        """Execution API reached through the deterministic gate."""
        if not isinstance(action, dict):
            raise ValueError("Base action must be a dictionary.")

        operation = action.get("operation")

        if not isinstance(operation, str) or not operation.strip():
            raise ValueError("Base operation is required.")

        payload = action.get("payload")

        record = {
            "operation": operation.strip(),
            "payload": payload,
        }

        self.executed.append(record)

        return {
            "status": "executed",
            "operation": operation.strip(),
            "payload": payload,
        }
