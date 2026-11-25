import pytest

from zgw_consumers.admin_forms import MASK_PREFIX, REVEAL_CHARS, mask


@pytest.mark.parametrize(
    "value,expected",
    [
        ("", ""),
        ("ab", MASK_PREFIX),
        ("abcd", MASK_PREFIX),  # revealing the suffix would reveal the whole value
        ("abcde", f"{MASK_PREFIX}bcde"),
        ("abcdefghijklmnopqrstuvwxyz", f"{MASK_PREFIX}wxyz"),
        ("Token abcdefghijklmnopqrstuvwxyz", f"{MASK_PREFIX}wxyz"),
    ],
)
def test_mask(value, expected):
    assert mask(value) == expected


@pytest.mark.parametrize("length", [1, 4, 5, 16, 64, 255])
def test_mask_does_not_leak_length(length):
    hint = mask("a" * length)

    # the only thing to learn is whether the value is trivially short
    expected = (
        MASK_PREFIX if length <= REVEAL_CHARS else f"{MASK_PREFIX}{'a' * REVEAL_CHARS}"
    )
    assert hint == expected
