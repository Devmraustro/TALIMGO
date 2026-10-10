"""TALIMGO's own AI layer: local-only inference, grounding, and output validation.

There is no hosted provider adapter here and none may be added (AGENTS.md section 2). The only
network calls this package can make are to the single configured local endpoint, re-validated by
:mod:`app.ai.policy` before every request.

This package deliberately re-exports nothing: ``app.config`` imports ``app.ai.policy`` at module
import time, so eager re-exports here would create an import cycle. Import the submodule you need:

    from app.ai.adapter import LocalModelClient
    from app.ai.policy import assert_local_endpoint
    from app.ai.schemas import validate_tutor_reply
"""
