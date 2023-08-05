from collections import defaultdict

import pytest


def pytest_addoption(parser):
    parser.addoption("--pigeonhole", dest="pigeonhole", help="Fixture name to spread outcommes summary against.")


def pytest_configure(config):
    fixturename = config.getoption('pigeonhole')
    if fixturename:
        configure_pigeonhole(config, fixturename)


def pytest_unconfigure(config):
    unconfigure_pigeonhole(config)


def configure_pigeonhole(pytest_config, fixturename):
    if not hasattr(pytest_config, 'slaveinput'):
        # prevent opening fixturenames on slave nodes (xdist)
        pytest_config._pigeonhole = Pigeonhole(fixturename)
        pytest_config.pluginmanager.register(pytest_config._pigeonhole)


def unconfigure_pigeonhole(pytest_config):
    pigeonhole = getattr(pytest_config, '_pigeonhole', None)
    if pigeonhole:
        pytest_config.pluginmanager.unregister(pigeonhole)
        del pytest_config._pigeonhole


def short_repr(value, max_len=80):
    value = repr(value)
    if len(value) > max_len:
        half_width = max_len / 2 - 2
        value = "{}...{}".format(value[:half_width], value[-half_width:])
    return value


NOT_APPLICABLE = "N/A"
UNKNOWN_VALUE = "unknown value"


class Pigeonhole(object):
    class Outcome(object):
        __slots__ = "passed", "failed", "skipped", "error"

        def __init__(self):
            for field in self.__slots__:
                setattr(self, field, 0)

        def increment(self, kind):
            assert kind in self.__slots__, "Unknown outcome type: %s." % kind
            setattr(self, kind, getattr(self, kind) + 1)

        def __str__(self):
            return " ".join("| {}: {:<4}".format(kind[0], getattr(self, kind)) for kind in self.__slots__)

        @classmethod
        def get_kind(cls, pytest_report):
            for kind in cls.__slots__:
                if getattr(pytest_report, kind, None):
                    return kind
                elif not hasattr(pytest_report, kind):
                    print("dupa, ni mo %s" % kind)
            return "error"

    def __init__(self, fixture_name):
        self._fixture_name = fixture_name
        self._outcomes = defaultdict(lambda: Pigeonhole.Outcome())

    @pytest.hookimpl(hookwrapper=True, trylast=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if self._fixture_name in item.fixturenames:
            report.pigeonhole_index = item.funcargs.get(self._fixture_name, UNKNOWN_VALUE)
        else:
            report.pigeonhole_index = item.funcargs.get(self._fixture_name, NOT_APPLICABLE)

    def count(self, pigeonhole_index, outcome_kind):
        if pigeonhole_index not in (NOT_APPLICABLE, UNKNOWN_VALUE):
            pigeonhole_index = short_repr(pigeonhole_index)

        return self._outcomes[pigeonhole_index].increment(outcome_kind)

    def pytest_runtest_logreport(self, report):
        when = getattr(report, "when", "call")
        kind = report.failed and when != "call" and "error" or Pigeonhole.Outcome.get_kind(report)
        if kind != "passed" or when == "call":
            self.count(report.pigeonhole_index, kind)

    def pytest_terminal_summary(self, terminalreporter):
        name_lengths = [len(str(value)) for value in self._outcomes.keys()]
        if name_lengths:
            max_width = max(name_lengths)
            terminalreporter.write_sep('=', 'Pigeonhole: {}'.format(self._fixture_name))
            for fixture_index, outcome in sorted(self._outcomes.items()):
                line = " {index:{width}} {outcome}\n".format(index=fixture_index, width=max_width, outcome=outcome)
                terminalreporter.write(line)
