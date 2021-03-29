import pytest

from ._common import CommonMethod


@pytest.mark.run(order=2)
class TestRaceInfoRepository(CommonMethod):
    pass
