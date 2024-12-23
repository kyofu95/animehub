# type: ignore
# pylint: disable=redefined-outer-name, missing-function-docstring, unsubscriptable-object

import pytest

from app.core.security import Hasher, HashingError


@pytest.mark.asyncio
async def test_hasher():
    plain_password = "abc"

    encoded = Hasher.hash(plain_password)

    assert Hasher.verify(plain_password, encoded)

    encoded = "wrong_hash"

    with pytest.raises(HashingError) as exc_info:
        assert Hasher.verify(plain_password, encoded) is False
    assert exc_info.type is HashingError
