from datetime import datetime

import pytest


@pytest.fixture()
def datetime_():
    now = datetime.now().replace(second=0, microsecond=0)
    return now
