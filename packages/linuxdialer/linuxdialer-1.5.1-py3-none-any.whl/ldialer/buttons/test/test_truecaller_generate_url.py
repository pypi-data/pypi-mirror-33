import pytest
from phonenumbers import parse

from ..truecaller import generate_url

testcases = (
    ('+919829142536', 'https://www.truecaller.com/search/in/9829142536'),
    ('+12024561111', 'https://www.truecaller.com/search/us/2024561111'),
    ('+441632960746', 'https://www.truecaller.com/search/gb/1632960746'),
    ('+16135550124', 'https://www.truecaller.com/search/us/6135550124'),
    ('+611900654321', 'https://www.truecaller.com/search/au/1900654321'),
    ('+353209110146', 'https://www.truecaller.com/search/ie/209110146'),
    ('+3655173903', 'https://www.truecaller.com/search/hu/55173903')
)


@pytest.mark.parametrize('inputs, outputs', testcases)
def test_generate_url(inputs, outputs):
    obs = generate_url(parse(inputs, None))
    print(obs)
    assert obs == outputs
