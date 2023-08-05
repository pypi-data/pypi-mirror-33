import textwrap
import tempfile
import pytest

from falcon_helpers.config import (
    Config,
    ConfigurationError
)


def test_config_as_dict():
    conf = Config()
    conf['thing'] = 1
    conf['other'] = {'thing': 2}

    assert conf['thing'] == 1
    assert conf['other'] == {'thing': 2}

    with pytest.raises(ConfigurationError):
        assert conf['doesnt']


def test_config_as_mapping():
    conf = Config()
    conf.thing = 1
    conf.other = 'best'

    assert conf.thing == 1
    assert conf.other == 'best'

    with pytest.raises(ConfigurationError):
        assert conf.doesnt

def test_config_from_inis():

    with tempfile.NamedTemporaryFile() as f1, tempfile.NamedTemporaryFile() as f2:
        conf1 = textwrap.dedent(
        '''
        [sectionone]
        x = 1

        [sectiontwo]
        x = 2
        y = somestring
        ''')

        conf2 = textwrap.dedent(
        '''
        [sectionone]
        x = 3

        [sectionthree]
        y = 6
        other = mystring
        ''')

        f1.write(conf1.encode())
        f1.seek(0)

        f2.write(conf2.encode())
        f2.seek(0)

        config = Config.from_inis(f1.name, f2.name)

        # Test later config override earlier ones
        assert config.sectionone.x == '3'

        # test same named, in different section, is not overridden
        assert config.sectiontwo.x == '2'

        # test early configs without override stick around
        assert config.sectiontwo.y == 'somestring'

        # test later configs with new names are added
        assert config.sectionthree.other == 'mystring'

        # test later configs with names in other sections are added
        assert config.sectionthree.y == '6'
