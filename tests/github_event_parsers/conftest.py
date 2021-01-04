from datetime import datetime

import pytest


@pytest.fixture()
def datetime_():
    return datetime.now()
