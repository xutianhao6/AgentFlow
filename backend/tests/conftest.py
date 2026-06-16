import os
import sys

# ensure backend root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentflow.core.db import init_db  # noqa: E402

init_db()

# Mirror the app startup so seed data (plugins / templates) exists in tests
# even when TestClient is not used as a context manager.
from agentflow.plugins.runtime import load_builtin_plugins  # noqa: E402
from agentflow.api.app import _seed_demo_data  # noqa: E402

load_builtin_plugins()
_seed_demo_data()
