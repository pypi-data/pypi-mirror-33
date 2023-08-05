import pytest
from pkglts.config_management import Config
from pkglts.option.test.option import OptionTest


@pytest.fixture()
def opt():
    return OptionTest('test')


def test_root_dir_is_defined(opt):
    assert opt.root_dir() is not None


def test_update_parameters(opt):
    cfg = {}
    opt.update_parameters(cfg)
    assert len(cfg['test']) == 1


def test_config_check_suite_names(opt):
    for name in ('walou', ' nose'):
        cfg = Config(dict(test={'suite_name': name}))
        assert 'test.suite_name' in opt.check(cfg)


def test_require(opt):
    for suite_name in ('pytest', 'nose'):
        cfg = Config(dict(base={}, test={'suite_name': suite_name}))

        assert len(opt.require('option', cfg)) == 1
        assert len(opt.require('setup', cfg)) == 0
        assert len(opt.require('install', cfg)) == 0
        assert len(opt.require('dvlpt', cfg)) == 2
