# type: ignore
from typing import List
from typing import Tuple

from riot import Venv
from riot import latest


SUPPORTED_PYTHON_VERSIONS = [
    (2, 7),
    (3, 5),
    (3, 6),
    (3, 7),
    (3, 8),
    (3, 9),
    (3, 10),
    (3, 11),
]  # type: List[Tuple[int, int]]


def version_to_str(version):
    # type: (Tuple[int, int]) -> str
    """Convert a Python version tuple to a string

    >>> version_to_str((2, 7))
    '2.7'
    >>> version_to_str((3, 5))
    '3.5'
    >>> version_to_str((3, 1))
    '3.1'
    >>> version_to_str((3, 10))
    '3.10'
    >>> version_to_str((3, 11))
    '3.11'
    >>> version_to_str((3, ))
    '3'
    """
    return ".".join(str(p) for p in version)


def str_to_version(version):
    # type: (str) -> Tuple[int, int]
    """Convert a Python version string to a tuple

    >>> str_to_version("2.7")
    (2, 7)
    >>> str_to_version("3.5")
    (3, 5)
    >>> str_to_version("3.1")
    (3, 1)
    >>> str_to_version("3.10")
    (3, 10)
    >>> str_to_version("3.11")
    (3, 11)
    >>> str_to_version("3")
    (3,)
    """
    return tuple(int(p) for p in version.split("."))


MIN_PYTHON_VERSION = version_to_str(min(SUPPORTED_PYTHON_VERSIONS))
MAX_PYTHON_VERSION = version_to_str(max(SUPPORTED_PYTHON_VERSIONS))


def select_pys(min_version=MIN_PYTHON_VERSION, max_version=MAX_PYTHON_VERSION):
    # type: (str, str) -> List[str]
    """Helper to select python versions from the list of versions we support

    >>> select_pys()
    ['2.7', '3.5', '3.6', '3.7', '3.8', '3.9', '3.10', '3.11']
    >>> select_pys(min_version='3')
    ['3.5', '3.6', '3.7', '3.8', '3.9', '3.10', '3.11']
    >>> select_pys(max_version='3')
    ['2.7']
    >>> select_pys(min_version='3.5', max_version='3.8')
    ['3.5', '3.6', '3.7', '3.8']
    """
    min_version = str_to_version(min_version)
    max_version = str_to_version(max_version)

    return [version_to_str(version) for version in SUPPORTED_PYTHON_VERSIONS if min_version <= version <= max_version]


venv = Venv(
    pkgs={
        "mock": latest,
        "pytest": "<7.0.0",
        "pytest-mock": latest,
        "coverage": latest,
        "pytest-cov": latest,
        "opentracing": latest,
        "hypothesis": "<6.45.1",
    },
    env={
        "DD_TESTING_RAISE": "1",
    },
    venvs=[
        Venv(
            pys=["3"],
            pkgs={
                "black": "==21.4b2",
                "isort": [latest],
                # See https://github.com/psf/black/issues/2964 for incompatibility with click==8.1.0
                "click": "<8.1.0",
            },
            venvs=[
                Venv(
                    name="fmt",
                    command="isort . && black .",
                ),
                Venv(
                    name="black",
                    command="black {cmdargs}",
                ),
                Venv(
                    name="isort",
                    command="isort {cmdargs}",
                ),
            ],
        ),
        Venv(
            pys=["3"],
            pkgs={
                "flake8": ">=3.8,<3.9",
                "flake8-blind-except": latest,
                "flake8-builtins": latest,
                "flake8-docstrings": latest,
                "flake8-logging-format": latest,
                "flake8-rst-docstrings": latest,
                "flake8-isort": latest,
                "pygments": latest,
            },
            venvs=[
                Venv(
                    name="flake8",
                    command="flake8 {cmdargs}",
                ),
            ],
        ),
        Venv(
            pys=["3"],
            name="mypy",
            command="mypy {cmdargs}",
            create=True,
            pkgs={
                "mypy": latest,
                "envier": latest,
                "types-attrs": latest,
                "types-docutils": latest,
                "types-protobuf": latest,
                "types-PyYAML": latest,
                "types-setuptools": latest,
                "types-six": latest,
            },
        ),
        Venv(
            pys=["3"],
            pkgs={"codespell": "==2.1.0"},
            venvs=[
                Venv(
                    name="codespell",
                    command='codespell --skip="ddwaf.h" ddtrace/ tests/',
                ),
                Venv(
                    name="hook-codespell",
                    command="codespell {cmdargs}",
                ),
            ],
        ),
        Venv(
            pys=["3"],
            pkgs={"slotscheck": latest},
            venvs=[
                Venv(
                    name="slotscheck",
                    command="python -m slotscheck -v {cmdargs}",
                ),
            ],
        ),
        Venv(
            pys=["3"],
            pkgs={"ddapm-test-agent": ">=1.2.0"},
            venvs=[
                Venv(
                    name="snapshot-fmt",
                    command="ddapm-test-agent-fmt {cmdargs} tests/snapshots/",
                ),
            ],
        ),
        Venv(
            pys=["3"],
            name="riot-helpers",
            # DEV: pytest really doesn't want to execute only `riotfile.py`, call doctest directly
            command="python -m doctest {cmdargs} riotfile.py",
            pkgs={"riot": latest},
        ),
        Venv(
            pys=["3"],
            name="scripts",
            command="python -m doctest {cmdargs} scripts/get-target-milestone.py",
        ),
        Venv(
            name="docs",
            pys=["3"],
            pkgs={
                "cython": latest,
                "reno[sphinx]": latest,
                "sphinx": "~=4.3.2",
                "sphinxcontrib-spelling": latest,
                "PyEnchant": latest,
                # Pin due to dulwich not publishing wheels and the env doesn't have
                # the dependencies required to build the package.
                # https://github.com/jelmer/dulwich/issues/963.
                "dulwich": "<0.20.36",
            },
            command="scripts/build-docs",
        ),
        Venv(
            name="appsec",
            pys=select_pys(),
            command="pytest {cmdargs} tests/appsec",
            pkgs={
                "pycryptodome": latest,
                "cryptography": latest,
            },
        ),
        Venv(
            pys=select_pys(),
            pkgs={
                # pytest-benchmark depends on cpuinfo which dropped support for Python<=3.6 in 9.0
                # See https://github.com/workhorsy/py-cpuinfo/issues/177
                "pytest-benchmark": latest,
                "py-cpuinfo": "~=8.0.0",
                "msgpack": latest,
                # TODO: remove py dependency once https://github.com/ionelmc/pytest-benchmark/pull/227 is released
                "py": latest,
            },
            venvs=[
                Venv(
                    name="benchmarks",
                    command="pytest --no-cov --benchmark-warmup=on {cmdargs} tests/benchmarks",
                ),
                Venv(
                    name="benchmarks-nogc",
                    command="pytest --no-cov --benchmark-warmup=on --benchmark-disable-gc {cmdargs} tests/benchmarks",
                ),
            ],
        ),
        Venv(
            name="profile-diff",
            command="python scripts/diff.py {cmdargs}",
            pys="3",
            pkgs={
                "austin-python": "~=1.0",
                "rich": latest,
            },
        ),
        Venv(
            name="tracer",
            venvs=[
                Venv(
                    pys=select_pys(),
                    pkgs={
                        "msgpack": latest,
                        "attrs": ["==20.1.0", latest],
                        "structlog": latest,
                        # httpretty v1.0 drops python 2.7 support
                        "httpretty": "==0.9.7",
                    },
                    # Riot venvs break with Py 3.11 importlib, specifically with hypothesis (test_http.py).
                    # We'll skip the test_http.py tests in riot and run them separately through tox in CI.
                    # See linked riot issue: https://github.com/DataDog/riot/issues/192
                    command="pytest {cmdargs} tests/tracer/ --ignore=tests/tracer/test_http.py",
                ),
            ],
            env={
                "DD_REMOTE_CONFIGURATION_ENABLED": "false",
            },
        ),
        Venv(
            name="telemetry",
            command="pytest {cmdargs} tests/telemetry/",
            pys=select_pys(),
            pkgs={
                # httpretty v1.0 drops python 2.7 support
                "httpretty": "==0.9.7",
            },
        ),
        Venv(
            name="integration",
            pys=select_pys(),
            command="pytest --no-cov {cmdargs} tests/integration/",
            pkgs={"msgpack": [latest]},
            venvs=[
                Venv(
                    name="integration-latest",
                    env={
                        "AGENT_VERSION": "latest",
                    },
                ),
                Venv(
                    name="integration-snapshot",
                    env={
                        "DD_TRACE_AGENT_URL": "http://localhost:9126",
                        "AGENT_VERSION": "testagent",
                    },
                ),
            ],
        ),
        Venv(
            name="internal",
            command="pytest {cmdargs} tests/internal/",
            pkgs={
                "httpretty": "==0.9.7",
                "gevent": latest,
                "packaging": ["==17.1", latest],
            },
            env={
                "DD_REMOTE_CONFIGURATION_ENABLED": "false",
            },
            venvs=[
                Venv(pys="2.7"),
                Venv(
                    # FIXME[bytecode-3.11]: internal depends on bytecode, which is not python 3.11 compatible.
                    pys=select_pys(min_version="3.5"),
                    pkgs={"pytest-asyncio": latest},
                ),
            ],
        ),
        Venv(
            name="gevent",
            command="pytest {cmdargs} tests/contrib/gevent",
            pkgs={
                "botocore": latest,
                "requests": latest,
                "elasticsearch": latest,
                "pynamodb": latest,
            },
            venvs=[
                Venv(
                    pys="2.7",
                    pkgs={
                        "gevent": ["~=1.1.0", "~=1.2.0", "~=1.3.0"],
                        "greenlet": "~=1.0",
                    },
                ),
                Venv(
                    pkgs={
                        "aiobotocore": "<=2.3.1",
                        "aiohttp": latest,
                    },
                    venvs=[
                        Venv(
                            pys=select_pys(min_version="3.5", max_version="3.6"),
                            pkgs={
                                "gevent": ["~=1.1.0", "~=1.2.0", "~=1.3.0"],
                                "greenlet": "~=1.0",
                            },
                        ),
                        Venv(
                            pys=select_pys(min_version="3.7", max_version="3.8"),
                            pkgs={
                                "gevent": ["~=1.3.0", "~=1.4.0"],
                                # greenlet>0.4.17 wheels are incompatible with gevent and python>3.7
                                # This issue was fixed in gevent v20.9:
                                # https://github.com/gevent/gevent/issues/1678#issuecomment-697995192
                                "greenlet": "<0.4.17",
                            },
                        ),
                        Venv(
                            pys="3.9",
                            pkgs={
                                "gevent": ["~=20.9.0", "~=20.12.0", "~=21.1.0"],
                                "greenlet": "~=1.0",
                            },
                        ),
                        Venv(
                            pys="3.10",
                            pkgs={
                                "gevent": ["~=21.8.0"],
                            },
                        ),
                        Venv(
                            pys="3.11",
                            pkgs={
                                "gevent": ["~=22.8.0", latest],
                            },
                        ),
                    ],
                ),
            ],
        ),
        Venv(
            name="runtime",
            command="pytest {cmdargs} tests/runtime/",
            venvs=[Venv(pys=select_pys(), pkgs={"msgpack": latest})],
        ),
        Venv(
            name="ddtracerun",
            command="pytest {cmdargs} --no-cov tests/commands/test_runner.py",
            venvs=[
                Venv(
                    pys=select_pys(),
                    pkgs={
                        "redis": latest,
                        "gevent": latest,
                    },
                ),
            ],
        ),
        Venv(
            name="debugger",
            command="pytest {cmdargs} tests/debugging/",
            pkgs={"msgpack": latest},
            venvs=[
                Venv(pys="2.7"),
                Venv(
                    # FIXME[bytecode-3.11]: debugger depends on bytecode, which doesn't yet have 3.11 support
                    pys=select_pys(min_version="3.5", max_version="3.10"),
                    pkgs={"pytest-asyncio": latest},
                ),
            ],
        ),
        Venv(
            name="vendor",
            command="pytest {cmdargs} tests/vendor/",
            pys=select_pys(),
            pkgs={
                "msgpack": ["~=1.0.0", latest],
            },
        ),
        Venv(
            name="wait",
            command="python tests/wait-for-services.py {cmdargs}",
            # Default Python 3 (3.10) collections package breaks with kombu/vertica, so specify Python 3.9 instead.
            pys="3.9",
            pkgs={
                "cassandra-driver": latest,
                "psycopg2-binary": latest,
                "mysql-connector-python": "!=8.0.18",
                "vertica-python": ">=0.6.0,<0.7.0",
                "kombu": ">=4.2.0,<4.3.0",
            },
        ),
        Venv(
            name="httplib",
            command="pytest {cmdargs} tests/contrib/httplib",
            pys=select_pys(),
        ),
        Venv(
            name="test_logging",
            command="pytest {cmdargs} tests/contrib/logging",
            pys=select_pys(),
        ),
        Venv(
            name="falcon",
            command="pytest {cmdargs} tests/contrib/falcon",
            venvs=[
                # Falcon 1.x
                # Python 2.7+
                Venv(
                    pys=select_pys(max_version="3.9"),
                    pkgs={
                        "falcon": [
                            "~=1.4.1",
                            "~=1.4",  # latest 1.x
                        ]
                    },
                ),
                # Falcon 2.x
                # Python 3.5+
                Venv(
                    pys=select_pys(min_version="3.5"),
                    pkgs={
                        "falcon": [
                            "~=2.0.0",
                            "~=2.0",  # latest 2.x
                        ]
                    },
                ),
                # Falcon 3.x
                # Python 3.5+
                Venv(
                    pys=select_pys(min_version="3.5"),
                    pkgs={
                        "falcon": [
                            "~=3.0.0",
                            "~=3.0",  # latest 3.x
                            latest,
                        ]
                    },
                ),
            ],
        ),
        Venv(
            name="bottle",
            pkgs={"WebTest": latest},
            venvs=[
                Venv(
                    command="pytest {cmdargs} --ignore='tests/contrib/bottle/test_autopatch.py' tests/contrib/bottle/",
                    venvs=[
                        Venv(
                            pys=select_pys(max_version="3.9"),
                            pkgs={"bottle": [">=0.11,<0.12", ">=0.12,<0.13", latest]},
                        ),
                        Venv(
                            pys=select_pys(min_version="3.10"),
                            pkgs={"bottle": latest},
                        ),
                    ],
                ),
                Venv(
                    command="python tests/ddtrace_run.py pytest {cmdargs} tests/contrib/bottle/test_autopatch.py",
                    env={"DD_SERVICE": "bottle-app"},
                    venvs=[
                        Venv(
                            pys=select_pys(max_version="3.9"),
                            pkgs={"bottle": [">=0.11,<0.12", ">=0.12,<0.13", latest]},
                        ),
                        Venv(
                            pys=select_pys(min_version="3.10"),
                            pkgs={"bottle": latest},
                        ),
                    ],
                ),
            ],
        ),
        Venv(
            name="celery",
            command="pytest {cmdargs} tests/contrib/celery",
            pkgs={"more_itertools": "<8.11.0"},
            venvs=[
                # Non-4.x celery should be able to use the older redis lib, since it locks to an older kombu
                Venv(
                    # Use <=3.5 to avoid setuptools >=58 which removed `use_2to3` which is needed by celery<4
                    # https://github.com/pypa/setuptools/issues/2086
                    pys=select_pys(max_version="3.5"),
                    pkgs={
                        "pytest": "~=3.10",
                        "celery": "~=3.0",  # most recent 3.x.x release
                        "redis": "~=2.10.6",
                    },
                ),
                # Celery 4.2 is now limited to Kombu 4.3
                # https://github.com/celery/celery/commit/1571d414461f01ae55be63a03e2adaa94dbcb15d
                Venv(
                    pys=select_pys(max_version="3.6"),
                    pkgs={
                        "pytest": "~=3.10",
                        "celery": "~=4.2.2",
                        "redis": "~=2.10.6",
                        "kombu": "~=4.3.0",
                        "importlib_metadata": "<5.0",  # kombu using deprecated shims removed in importlib_metadata 5.0
                    },
                ),
                # Celery 4.3 wants Kombu >= 4.4 and Redis >= 3.2
                # Split into <3.8 and >=3.8 to pin importlib_metadata dependency for kombu
                Venv(
                    pys=select_pys(max_version="3.7"),
                    pkgs={
                        "pytest": "~=3.10",
                        "celery": [
                            "~=4.4",  # most recent 4.x
                        ],
                        "redis": "~=3.5",
                        "kombu": "~=4.4",
                        "importlib_metadata": "<5.0",  # kombu using deprecated shims removed in importlib_metadata 5.0
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.8", max_version="3.9"),
                    pkgs={
                        "pytest": "~=3.10",
                        "celery": [
                            "~=4.4",  # most recent 4.x
                        ],
                        "redis": "~=3.5",
                        "kombu": "~=4.4",
                    },
                ),
                # Celery 5.x wants Python 3.6+
                # Split into <3.8 and >=3.8 to pin importlib_metadata dependency for kombu
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.7"),
                    env={
                        # https://docs.celeryproject.org/en/v5.0.5/userguide/testing.html#enabling
                        "PYTEST_PLUGINS": "celery.contrib.pytest",
                    },
                    pkgs={
                        "celery": [
                            "~=5.0.5",
                            "~=5.0",  # most recent 5.x
                            latest,
                        ],
                        "redis": "~=3.5",
                        "importlib_metadata": "<5.0",  # kombu using deprecated shims removed in importlib_metadata 5.0
                    },
                ),
                Venv(
                    # Billiard dependency is incompatible with Python 3.11
                    # https://github.com/celery/billiard/issues/377
                    pys=select_pys(min_version="3.8", max_version="3.10"),
                    env={
                        # https://docs.celeryproject.org/en/v5.0.5/userguide/testing.html#enabling
                        "PYTEST_PLUGINS": "celery.contrib.pytest",
                    },
                    pkgs={
                        "celery": [
                            "~=5.0",  # most recent 5.x
                            latest,
                        ],
                        "redis": "~=3.5",
                    },
                ),
            ],
        ),
        Venv(
            name="pylons",
            command="python -m pytest {cmdargs} tests/contrib/pylons",
            venvs=[
                Venv(
                    pys="2.7",
                    pkgs={
                        "pylons": [
                            ">=0.9.6,<0.9.7",
                            ">=0.9.7,<0.9.8",
                            ">=0.10,<0.11",
                        ],
                        "decorator": "<5",
                        "pastedeploy": "<3",
                        "webob": "<1.1",
                    },
                ),
                Venv(
                    pys="2.7",
                    pkgs={
                        "pylons": [
                            ">=1.0,<1.1",
                        ],
                        "decorator": "<5",
                        "pastedeploy": "<3",
                    },
                ),
            ],
        ),
        Venv(
            name="cherrypy",
            command="python -m pytest {cmdargs} tests/contrib/cherrypy",
            venvs=[
                Venv(
                    pys=select_pys(max_version="3.10"),
                    pkgs={
                        "cherrypy": [
                            ">=11,<12",
                            ">=12,<13",
                            ">=13,<14",
                            ">=14,<15",
                            ">=15,<16",
                            ">=16,<17",
                            ">=17,<18",
                        ],
                        "more_itertools": "<8.11.0",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.5"),
                    pkgs={
                        "cherrypy": [">=18.0,<19", latest],
                        "more_itertools": "<8.11.0",
                    },
                ),
            ],
        ),
        Venv(
            name="pymongo",
            command="pytest {cmdargs} tests/contrib/pymongo",
            pkgs={
                "mongoengine": latest,
            },
            venvs=[
                Venv(
                    # Use <=3.5 to avoid setuptools >=58 which dropped `use_2to3` which is needed by pymongo>=3.4
                    # https://github.com/pypa/setuptools/issues/2086
                    pys=select_pys(max_version="3.5"),
                    pkgs={
                        "pymongo": [
                            ">=3.0,<3.1",
                            ">=3.1,<3.2",
                            ">=3.2,<3.3",
                            ">=3.3,<3.4",
                        ],
                    },
                ),
                Venv(
                    # pymongo 3.4 is incompatible with Python>=3.8
                    # AttributeError: module 'platform' has no attribute 'linux_distribution'
                    pys=select_pys(max_version="3.7"),
                    pkgs={
                        "pymongo": ">=3.4,<3.5",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.9"),
                    pkgs={
                        "pymongo": [
                            ">=3.5,<3.6",
                            ">=3.6,<3.7",
                            ">=3.7,<3.8",
                            ">=3.8,<3.9",
                            ">=3.9,<3.10",
                        ],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6"),
                    pkgs={
                        "pymongo": [
                            ">=3.10,<3.11",
                            ">=3.12,<3.13",
                            ">=4.0,<4.1",
                            latest,
                        ],
                    },
                ),
            ],
        ),
        # Django  Python version support
        # 1.11    2.7, 3.4, 3.5, 3.6, 3.7 (added in 1.11.17)
        # 2.0     3.4, 3.5, 3.6, 3.7
        # 2.1     3.5, 3.6, 3.7
        # 2.2     3.5, 3.6, 3.7, 3.8 (added in 2.2.8)
        # 3.0     3.6, 3.7, 3.8
        # 3.1     3.6, 3.7, 3.8
        # 4.0     3.8, 3.9, 3.10
        # 4.1     3.8, 3.9, 3.10
        # 4.2     3.8, 3.9, 3.10, 3.11
        # Source: https://docs.djangoproject.com/en/dev/faq/install/#what-python-version-can-i-use-with-django
        Venv(
            name="django",
            command="pytest {cmdargs} tests/contrib/django",
            pkgs={
                "django-redis": ">=4.5,<4.6",
                "django-pylibmc": ">=0.6,<0.7",
                "daphne": [latest],
                "requests": [latest],
                "redis": ">=2.10,<2.11",
                "psycopg2-binary": [">=2.8.6"],  # We need <2.9.0 for Python 2.7, and >2.9.0 for 3.9+
                "pytest-django": "==3.10.0",
                "pylibmc": latest,
                "python-memcached": latest,
            },
            venvs=[
                Venv(
                    pys=select_pys(max_version="3.6"),
                    pkgs={
                        "django": [">=1.8,<1.9", ">=1.11,<1.12"],
                    },
                ),
                Venv(
                    pys=["3.5"],
                    pkgs={
                        "django": [">=2.0,<2.1", ">=2.1,<2.2", ">=2.2,<2.3"],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.9"),
                    pkgs={"django": [">=2.0,<2.1"]},
                ),
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.9"),
                    pkgs={"django": [">=2.1,<2.2", ">=2.2,<2.3"]},
                ),
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.8"),
                    pkgs={
                        "django": [
                            "~=3.0",
                            "~=3.0.0",
                            "~=3.2.0",
                        ],
                        "channels": ["~=3.0", latest],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.8", max_version="3.10"),
                    pkgs={
                        "django": [
                            "~=4.0.0",
                            latest,
                        ],
                        "channels": [latest],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.8"),
                    pkgs={
                        "django": [
                            "~=4.1.0",
                            latest,
                        ],
                        "channels": [latest],
                    },
                ),
            ],
        ),
        Venv(
            name="django_hosts",
            command="pytest {cmdargs} tests/contrib/django_hosts",
            pkgs={
                "pytest-django": [
                    "==3.10.0",
                ],
            },
            venvs=[
                Venv(
                    pys=["3.5"],
                    pkgs={
                        "django_hosts": ["~=4.0"],
                        "django": ["~=2.2"],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6"),
                    pkgs={
                        "django_hosts": ["~=4.0"],
                        "django": [
                            "~=2.2",
                            "~=3.2",
                        ],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.8"),
                    pkgs={
                        "django_hosts": ["~=5.0", latest],
                        "django": "~=4.0",
                    },
                ),
            ],
        ),
        Venv(
            name="djangorestframework",
            command="pytest {cmdargs} tests/contrib/djangorestframework",
            venvs=[
                Venv(
                    pys=select_pys(max_version="3.6"),
                    pkgs={
                        "django": "==1.11",
                        "djangorestframework": [">=3.4,<3.5", ">=3.7,<3.8"],
                        "pytest-django": "==3.10.0",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.5", max_version="3.9"),
                    pkgs={
                        "django": ">=2.2,<2.3",
                        "djangorestframework": [">=3.8,<3.9", ">=3.9,<3.10", latest],
                        "pytest-django": "==3.10.0",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6"),
                    pkgs={
                        "django": ">=3.0,<3.1",
                        "djangorestframework": ">=3.10,<3.11",
                        "pytest-django": "==3.10.0",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6"),
                    pkgs={
                        "django": "~=3.2",
                        "djangorestframework": ">=3.11,<3.12",
                        "pytest-django": "==3.10.0",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.8"),
                    pkgs={
                        "django": "~=4.0",
                        "djangorestframework": ["~=3.13", latest],
                        "pytest-django": "==3.10.0",
                    },
                ),
            ],
        ),
        Venv(
            name="elasticsearch",
            command="pytest {cmdargs} tests/contrib/elasticsearch/test_elasticsearch.py",
            venvs=[
                Venv(
                    pys=select_pys(max_version="3.8"),
                    pkgs={
                        "elasticsearch": [
                            "~=1.6.0",
                            "~=1.7.0",
                            "~=1.8.0",
                            "~=1.9.0",
                            "~=2.3.0",
                            "~=2.4.0",
                            "~=5.1.0",
                            "~=5.2.0",
                            "~=5.3.0",
                            "~=5.4.0",
                            "~=6.3.0",
                            "~=6.4.0",
                            "~=6.8.0",
                            "~=7.0.0",
                            "~=7.1.0",
                            "~=7.5.0",
                        ]
                    },
                ),
                Venv(
                    pys=select_pys(),
                    pkgs={
                        "elasticsearch": [
                            "~=7.6.0",
                            "~=7.8.0",
                            "~=7.10.0",
                            # FIXME: Elasticsearch introduced a breaking change in 7.14
                            # which makes it incompatible with previous major versions.
                            # latest,
                        ]
                    },
                ),
                Venv(pys=select_pys(), pkgs={"elasticsearch1": ["~=1.10.0"]}),
                Venv(pys=select_pys(), pkgs={"elasticsearch2": ["~=2.5.0"]}),
                Venv(pys=select_pys(), pkgs={"elasticsearch5": ["~=5.5.0"]}),
                Venv(pys=select_pys(), pkgs={"elasticsearch6": ["~=6.4.0", "~=6.8.0", latest]}),
                Venv(pys=select_pys(), pkgs={"elasticsearch7": ["~=7.6.0", "~=7.8.0", "~=7.10.0"]}),
            ],
        ),
        Venv(
            name="elasticsearch-multi",
            command="pytest {cmdargs} tests/contrib/elasticsearch/test_elasticsearch_multi.py",
            venvs=[
                Venv(
                    pys=select_pys(),
                    pkgs={
                        "elasticsearch": ["~=1.6.0"],
                        "elasticsearch2": [latest],
                        "elasticsearch5": [latest],
                        "elasticsearch6": [latest],
                        "elasticsearch7": ["<7.14.0"],
                    },
                ),
            ],
        ),
        Venv(
            name="flask",
            command="pytest {cmdargs} tests/contrib/flask",
            pkgs={"blinker": latest, "requests": latest},
            venvs=[
                # Flask == 0.12.0
                Venv(
                    pys=select_pys(max_version="3.9"),
                    pkgs={
                        "flask": ["~=0.12.0"],
                        "pytest": "~=3.0",
                        "more_itertools": "<8.11.0",
                        # https://github.com/pallets/itsdangerous/issues/290
                        # DEV: Breaking change made in 2.0 release
                        "itsdangerous": "<2.0",
                        # https://github.com/pallets/markupsafe/issues/282
                        # DEV: Breaking change made in 2.1.0 release
                        "markupsafe": "<2.0",
                    },
                ),
                Venv(
                    pys=select_pys(max_version="3.9"),
                    command="python tests/ddtrace_run.py pytest {cmdargs} tests/contrib/flask_autopatch",
                    env={
                        "DD_SERVICE": "test.flask.service",
                        "DD_PATCH_MODULES": "jinja2:false",
                    },
                    pkgs={
                        "flask": ["~=0.12.0"],
                        "pytest": "~=3.0",
                        "more_itertools": "<8.11.0",
                        # https://github.com/pallets/itsdangerous/issues/290
                        # DEV: Breaking change made in 2.0 release
                        "itsdangerous": "<2.0",
                        # https://github.com/pallets/markupsafe/issues/282
                        # DEV: Breaking change made in 2.1.0 release
                        "markupsafe": "<2.0",
                    },
                ),
                # Flask 1.x.x
                Venv(
                    pys=select_pys(),
                    pkgs={
                        "flask": [
                            "~=1.0.0",
                            "~=1.1.0",
                            "~=1.0",  # latest 1.x
                        ],
                        # https://github.com/pallets/itsdangerous/issues/290
                        # DEV: Breaking change made in 2.1.0 release
                        "itsdangerous": "<2.1.0",
                        # https://github.com/pallets/markupsafe/issues/282
                        # DEV: Breaking change made in 2.1.0 release
                        "markupsafe": "<2.0",
                        # DEV: Flask 1.0.x is missing a maximum version for werkzeug dependency
                        "werkzeug": "<2.0",
                    },
                ),
                Venv(
                    pys=select_pys(),
                    command="python tests/ddtrace_run.py pytest {cmdargs} tests/contrib/flask_autopatch",
                    env={
                        "DD_SERVICE": "test.flask.service",
                        "DD_PATCH_MODULES": "jinja2:false",
                    },
                    pkgs={
                        "flask": [
                            "~=1.0.0",
                            "~=1.1.0",
                            "~=1.0",  # latest 1.x
                        ],
                        # https://github.com/pallets/itsdangerous/issues/290
                        # DEV: Breaking change made in 2.0 release
                        "itsdangerous": "<2.0",
                        # https://github.com/pallets/markupsafe/issues/282
                        # DEV: Breaking change made in 2.1.0 release
                        "markupsafe": "<2.0",
                        # DEV: Flask 1.0.x is missing a maximum version for werkzeug dependency
                        "werkzeug": "<2.0",
                    },
                ),
                # Flask >= 2.0.0
                Venv(
                    pys=select_pys(min_version="3.6"),
                    pkgs={
                        "flask": [
                            "~=2.0.0",
                            "~=2.0",  # latest 2.x
                            latest,
                        ],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6"),
                    command="python tests/ddtrace_run.py pytest {cmdargs} tests/contrib/flask_autopatch",
                    env={
                        "DD_SERVICE": "test.flask.service",
                        "DD_PATCH_MODULES": "jinja2:false",
                    },
                    pkgs={
                        "flask": [
                            "~=2.0.0",
                            "~=2.0",  # latest 2.x
                            latest,
                        ],
                    },
                ),
            ],
        ),
        Venv(
            name="flask_cache",
            command="pytest {cmdargs} tests/contrib/flask_cache",
            pkgs={
                "python-memcached": latest,
                "redis": "~=2.0",
                "blinker": latest,
            },
            venvs=[
                Venv(
                    pys=select_pys(max_version="2.7"),
                    pkgs={
                        "flask": ["~=0.10.0", "~=0.11.0"],
                        "Werkzeug": ["<1.0"],
                        "Flask-Cache": ["~=0.12.0"],
                        "werkzeug": "<1.0",
                        "pytest": "~=3.0",
                        "more_itertools": "<8.11.0",
                        # https://github.com/pallets/itsdangerous/issues/290
                        # DEV: Breaking change made in 2.0 release
                        "itsdangerous": "<2.0",
                        # https://github.com/pallets/markupsafe/issues/282
                        # DEV: Breaking change made in 2.1.0 release
                        "markupsafe": "<2.0",
                    },
                ),
                Venv(
                    pys=select_pys(max_version="3.9"),
                    pkgs={
                        "flask": ["~=0.10.0", "~=0.11.0", "~=0.12.0"],
                        "Werkzeug": ["<1.0"],
                        "Flask-Cache": ["~=0.13.0", latest],
                        "werkzeug": "<1.0",
                        "pytest": "~=3.0",
                        "more_itertools": "<8.11.0",
                        # https://github.com/pallets/itsdangerous/issues/290
                        # DEV: Breaking change made in 2.0 release
                        "itsdangerous": "<2.0",
                        # https://github.com/pallets/markupsafe/issues/282
                        # DEV: Breaking change made in 2.1.0 release
                        "markupsafe": "<2.0",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3"),
                    pkgs={
                        "flask": ["~=1.0.0", "~=1.1.0", latest],
                        "flask-caching": ["~=1.10.0", latest],
                        # https://github.com/pallets/itsdangerous/issues/290
                        # DEV: Breaking change made in 2.0 release
                        "itsdangerous": "<2.0",
                        # https://github.com/pallets/markupsafe/issues/282
                        # DEV: Breaking change made in 2.1.0 release
                        "markupsafe": "<2.0",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3"),
                    pkgs={
                        "flask": [latest],
                        "flask-caching": ["~=1.10.0", latest],
                    },
                ),
            ],
        ),
        Venv(
            name="mako",
            command="pytest {cmdargs} tests/contrib/mako",
            pys=select_pys(),
            pkgs={"mako": ["<1.0.0", "~=1.0.0", "~=1.1.0", latest]},
        ),
        Venv(
            name="mysql",
            command="pytest {cmdargs} tests/contrib/mysql",
            venvs=[
                Venv(
                    pys=select_pys(max_version="3.5"),
                    pkgs={"mysql-connector-python": ["==8.0.5", "<8.0.24"]},
                ),
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.9"),
                    pkgs={"mysql-connector-python": ["==8.0.5", ">=8.0", latest]},
                ),
                Venv(
                    pys=select_pys(min_version="3.10"),
                    pkgs={"mysql-connector-python": [">=8.0", latest]},
                ),
            ],
        ),
        Venv(
            name="psycopg",
            command="pytest {cmdargs} tests/contrib/psycopg",
            venvs=[
                Venv(
                    pys=["2.7"],
                    # DEV: Use `psycopg2-binary` so we don't need PostgreSQL dev headers
                    pkgs={"psycopg2-binary": ["~=2.7.0", "~=2.8.0"]},
                ),
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.10"),
                    # 2.7.x should also work, but it is from 2019
                    # DEV: Use `psycopg2-binary` so we don't need PostgreSQL dev headers
                    pkgs={"psycopg2-binary": ["~=2.8.0", "~=2.9.0", latest]},
                ),
                Venv(
                    pys=select_pys(min_version="3.11"),
                    # psycopg2>=2.9.2 supports Python 3.11
                    pkgs={"psycopg2-binary": ["~=2.9.2", latest]},
                ),
            ],
        ),
        Venv(
            name="pymemcache",
            pys=select_pys(),
            pkgs={
                "pymemcache": [
                    "~=1.4",  # Most recent 1.x release
                    "~=2.0",  # Most recent 2.x release
                    "~=3.0.1",
                    "~=3.1.1",
                    "~=3.2.0",
                    "~=3.3.0",
                    "~=3.4.2",
                    latest,
                ]
            },
            venvs=[
                Venv(command="pytest {cmdargs} --ignore=tests/contrib/pymemcache/autopatch tests/contrib/pymemcache"),
                Venv(command="python tests/ddtrace_run.py pytest {cmdargs} tests/contrib/pymemcache/autopatch/"),
            ],
        ),
        Venv(
            name="pynamodb",
            command="pytest {cmdargs} tests/contrib/pynamodb",
            venvs=[
                Venv(
                    pys=select_pys(min_version="3.7", max_version="3.10"),
                    pkgs={
                        # pynamodb==4.x breaks with botocore>=1.28 and python>=3.7
                        "pynamodb": [">=4.0,<4.1", ">=4.1,<4.2", ">=4.2,<4.3", ">=4.3,<4.4"],
                        "moto": ">=1.0,<2.0",
                        "botocore": "==1.27.96",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.11"),
                    pkgs={
                        # Pynamodb<=4.0 not compatible with Python 3.11
                        # (see https://github.com/pynamodb/PynamoDB/pull/703)
                        "pynamodb": [">=4.1,<4.2", ">=4.2,<4.3", ">=4.3,<4.4"],
                        "moto": ">=1.0,<2.0",
                        "botocore": "==1.27.96",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.7"),
                    pkgs={
                        "pynamodb": [latest],
                        "moto": ">=1.0,<2.0",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.5", max_version="3.6"),
                    pkgs={
                        # Pynamodb>=5.x dropped support for Python 3.5 & 3.6
                        "pynamodb": [">=4.0,<4.1", ">=4.1,<4.2", ">=4.2,<4.3", ">=4.3,<4.4"],
                        "moto": ">=1.0,<2.0",
                    },
                ),
                Venv(
                    pys=["2.7"],
                    pkgs={
                        # Pynamodb>=5.x dropped support for Python 2
                        "pynamodb": [">=4.0,<4.1", ">=4.1,<4.2", ">=4.2,<4.3", ">=4.3,<4.4"],
                        "moto": ">=1.0,<2.0",
                        "rsa": "<4.7.1",
                    },
                ),
            ],
        ),
        Venv(
            name="starlette",
            command="pytest {cmdargs} tests/contrib/starlette",
            pkgs={
                "httpx": latest,
                "pytest-asyncio": latest,
                "requests": latest,
                "aiofiles": latest,
                # Pinned until https://github.com/encode/databases/issues/298 is resolved.
                "sqlalchemy": "~=1.3.0",
                "aiosqlite": latest,
                "databases": latest,
            },
            venvs=[
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.10"),
                    pkgs={
                        "starlette": [">=0.13,<0.14", ">=0.14,<0.15", latest],
                    },
                ),
                Venv(
                    # Python 3.11 only compatible with Starlette >=0.21.
                    pys=select_pys(min_version="3.11"),
                    pkgs={
                        "starlette": ["~=0.21", latest],
                    },
                ),
            ],
        ),
        Venv(
            name="sqlalchemy",
            command="pytest {cmdargs} tests/contrib/sqlalchemy",
            venvs=[
                Venv(
                    venvs=[
                        Venv(
                            pys=select_pys(max_version="3.9"),
                            pkgs={
                                "sqlalchemy": ["~=1.0.0", "~=1.1.0", "~=1.2.0", "~=1.3.0", latest],
                                # 2.8.x is the last one support Python 2.7
                                "psycopg2-binary": ["~=2.8.0"],
                                "mysql-connector-python": ["<8.0.24"],
                            },
                        ),
                        Venv(
                            pys=select_pys(min_version="3.6", max_version="3.9"),
                            pkgs={
                                "sqlalchemy": ["~=1.0.0", "~=1.1.0", "~=1.2.0", "~=1.3.0", latest],
                                "psycopg2-binary": latest,
                                "mysql-connector-python": latest,
                            },
                        ),
                        Venv(
                            pys=select_pys(min_version="3.10"),
                            pkgs={
                                "sqlalchemy": ["~=1.2.0", "~=1.3.0", latest],
                                "psycopg2-binary": latest,
                                "mysql-connector-python": latest,
                            },
                        ),
                    ],
                ),
            ],
        ),
        Venv(
            name="requests",
            command="pytest {cmdargs} tests/contrib/requests",
            venvs=[
                Venv(
                    pys=select_pys(max_version="3.9"),
                    pkgs={
                        "requests-mock": ">=1.4",
                        "requests": [
                            ">=2.8,<2.9",
                            ">=2.10,<2.11",
                            ">=2.12,<2.13",
                            ">=2.14,<2.15",
                            ">=2.16,<2.17",
                            ">=2.18,<2.19",
                            ">=2.20,<2.21",
                            latest,
                        ],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.10"),
                    pkgs={
                        "requests-mock": ">=1.4",
                        "requests": [
                            ">=2.20,<2.21",
                            latest,
                        ],
                    },
                ),
            ],
        ),
        Venv(
            name="wsgi",
            command="pytest {cmdargs} tests/contrib/wsgi",
            venvs=[
                Venv(
                    pys=select_pys(),
                    pkgs={
                        "WebTest": latest,
                    },
                ),
            ],
        ),
        Venv(
            name="boto",
            command="pytest {cmdargs} tests/contrib/boto",
            venvs=[Venv(pys=select_pys(max_version="3.6"), pkgs={"boto": latest, "moto": "<1.0.0"})],
        ),
        Venv(
            name="botocore",
            command="pytest {cmdargs} tests/contrib/botocore",
            pkgs={"botocore": latest},
            venvs=[
                Venv(pys=select_pys(min_version="3.5"), pkgs={"moto[all]": latest}),
                Venv(pys=["2.7"], pkgs={"moto": ["~=1.0"], "rsa": ["<4.7.1"]}),
            ],
        ),
        Venv(
            name="mongoengine",
            command="pytest {cmdargs} tests/contrib/mongoengine",
            pkgs={
                "pymongo": latest,
            },
            venvs=[
                Venv(
                    # Use <=3.5 to avoid setuptools >=58 which dropped `use_2to3` which is needed by mongoengine<0.20
                    # https://github.com/pypa/setuptools/issues/2086
                    pys=select_pys(max_version="3.5"),
                    pkgs={
                        # 0.20 dropped support for Python 2.7
                        "mongoengine": [">=0.15,<0.16", ">=0.16,<0.17", ">=0.17,<0.18", ">=0.18,<0.19"],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6"),
                    pkgs={"mongoengine": [">=0.20,<0.21", ">=0.21,<0.22", ">=0.22,<0.23", latest]},
                ),
            ],
        ),
        Venv(
            name="asgi",
            pkgs={
                "pytest-asyncio": latest,
                "httpx": latest,
                "asgiref": ["~=3.0.0", "~=3.0"],
            },
            pys=select_pys(min_version="3.6"),
            command="pytest {cmdargs} tests/contrib/asgi",
        ),
        Venv(
            name="mariadb",
            command="pytest {cmdargs} tests/contrib/mariadb",
            venvs=[
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.10"),
                    pkgs={
                        "mariadb": [
                            "~=1.0.0",
                            "~=1.0",
                            latest,
                        ],
                    },
                ),
                Venv(pys=select_pys(min_version="3.11"), pkgs={"mariadb": [">=1.1.2", latest]}),
            ],
        ),
        Venv(
            name="pymysql",
            command="pytest {cmdargs} tests/contrib/pymysql",
            venvs=[
                Venv(
                    pys=select_pys(),
                    pkgs={
                        "pymysql": [
                            "~=0.7",
                            "~=0.8",
                            "~=0.9",
                        ],
                    },
                ),
                Venv(
                    # 1.x dropped support for 2.7 and 3.5
                    pys=select_pys(min_version="3.6"),
                    pkgs={
                        "pymysql": [
                            "~=1.0",
                            latest,
                        ],
                    },
                ),
            ],
        ),
        Venv(
            name="pyramid",
            command="pytest {cmdargs} tests/contrib/pyramid/test_pyramid.py",
            pkgs={
                "requests": [latest],
                "webtest": [latest],
                "tests/contrib/pyramid/pserve_app": [latest],
            },
            venvs=[
                Venv(
                    # pserve_app has PasteDeploy dependency, but PasteDeploy>=3.0 is incompatible with Python 2.7
                    # pyramid>=2.0 no longer supports Python 2.7 and 3.5
                    pys=select_pys(max_version="3.5"),
                    pkgs={
                        "pastedeploy": "<3.0",
                        "pyramid": [
                            "~=1.7",
                            "~=1.8",
                            "~=1.9",
                            "~=1.10",
                        ],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6"),
                    pkgs={
                        "pyramid": [
                            "~=1.7",
                            "~=1.8",
                            "~=1.9",
                            "~=1.10",
                            latest,
                        ],
                    },
                ),
            ],
        ),
        Venv(
            name="aiobotocore",
            command="pytest {cmdargs} tests/contrib/aiobotocore",
            pkgs={"pytest-asyncio": latest, "async_generator": ["~=1.10"]},
            venvs=[
                # async_generator 1.10 used because @asynccontextmanager was only available in Python 3.6+
                # aiobotocore 1.x and higher require Python 3.6 or higher
                Venv(
                    pys=select_pys(min_version="3.6"),
                    pkgs={
                        "aiobotocore": ["~=2.0.0", "~=2.1.0", "~=2.2.0", "~=2.3.0"],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6"),
                    pkgs={
                        "aiobotocore": ["~=1.0.0", "~=1.2.0", "~=1.3.0", "~=1.4.2"],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.5", max_version="3.6"),
                    pkgs={
                        "aiobotocore": ["~=0.2", "~=0.3", "~=0.4"],
                    },
                ),
                # aiobotocore 0.2 and 0.4 do not work because they use async as a reserved keyword
                Venv(
                    pys=select_pys(min_version="3.5", max_version="3.8"),
                    pkgs={
                        "aiobotocore": ["~=0.5", "~=0.7", "~=0.8", "~=0.9"],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.5"),
                    pkgs={
                        "aiobotocore": ["~=0.10", "~=0.11"],
                    },
                ),
                # aiobotocore dropped Python 3.5 support in 0.12
                Venv(
                    pys=select_pys(min_version="3.6"),
                    pkgs={
                        "aiobotocore": ["~=0.12"],
                    },
                ),
            ],
        ),
        Venv(
            name="fastapi",
            command="pytest {cmdargs} tests/contrib/fastapi",
            pkgs={
                "httpx": latest,
                "pytest-asyncio": latest,
                "requests": latest,
                "aiofiles": latest,
            },
            venvs=[
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.10"),
                    pkgs={
                        "fastapi": [">=0.51,<0.52", ">=0.55,<0.56", ">=0.60,<0.61", latest],
                    },
                ),
                Venv(
                    # Python 3.11 only compatible with starlette >=0.21 onwards.
                    # Since fastapi internally pins starlette~=0.20.4, we'll override the starlette version to latest.
                    pys=select_pys(min_version="3.11"),
                    pkgs={
                        "fastapi": [latest],
                        "starlette": latest,
                    },
                ),
            ],
        ),
        Venv(
            name="aiomysql",
            pys=select_pys(min_version="3.7"),
            command="pytest {cmdargs} tests/contrib/aiomysql",
            pkgs={
                "pytest-asyncio": latest,
                "aiomysql": ["~=0.1.0", latest],
            },
        ),
        Venv(
            name="pytest",
            command="pytest {cmdargs} tests/contrib/pytest/",
            venvs=[
                Venv(
                    pys=["2.7"],
                    # pytest==4.6 is last to support python 2.7
                    pkgs={"pytest": ">=4.0,<4.6", "msgpack": latest},
                ),
                Venv(
                    pys=select_pys(min_version="3.5", max_version="3.9"),
                    pkgs={
                        "pytest": [
                            ">=3.0,<4.0",
                            ">=4.0,<5.0",
                            ">=5.0,<6.0",
                            ">=6.0,<7.0",
                            latest,
                        ],
                        "msgpack": latest,
                        "more_itertools": "<8.11.0",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.10"),
                    pkgs={
                        "pytest": [
                            ">=6.0,<7.0",
                            latest,
                        ],
                        "msgpack": latest,
                        "asynctest": "==0.13.0",
                        "more_itertools": "<8.11.0",
                    },
                ),
            ],
        ),
        Venv(
            name="asynctest",
            command="pytest {cmdargs} tests/contrib/asynctest/",
            venvs=[
                Venv(
                    pys=select_pys(min_version="3.5", max_version="3.9"),
                    pkgs={
                        "pytest": [
                            ">=6.0,<7.0",
                        ],
                        "asynctest": "==0.13.0",
                    },
                ),
            ],
        ),
        Venv(
            name="pytest-bdd",
            command="pytest {cmdargs} tests/contrib/pytest_bdd/",
            pkgs={"msgpack": latest},
            venvs=[
                Venv(
                    pys=["2.7"],
                    # pytest-bdd==3.4 is last to support python 2.7
                    pkgs={"pytest-bdd": ">=3.0,<3.5"},
                ),
                Venv(
                    pkgs={
                        "more_itertools": "<8.11.0",
                    },
                    venvs=[
                        Venv(
                            pys=["3.6"],
                            pkgs={"pytest-bdd": [">=4.0,<5.0"]},
                        ),
                        Venv(
                            pys=select_pys(min_version="3.7", max_version="3.9"),
                            pkgs={
                                "pytest-bdd": [
                                    ">=4.0,<5.0",
                                    # FIXME: add support for v6.1
                                    ">=6.0,<6.1",
                                ]
                            },
                        ),
                        Venv(
                            pys=select_pys(min_version="3.10"),
                            pkgs={
                                "pytest-bdd": [
                                    ">=4.0,<5.0",
                                    # FIXME: add support for v6.1
                                    ">=6.0,<6.1",
                                ]
                            },
                        ),
                    ],
                ),
            ],
        ),
        Venv(
            name="grpc",
            command="python -m pytest {cmdargs} tests/contrib/grpc",
            pkgs={
                "googleapis-common-protos": latest,
            },
            venvs=[
                # Versions between 1.14 and 1.20 have known threading issues
                # See https://github.com/grpc/grpc/issues/18994
                Venv(
                    pys=select_pys(max_version="3.6"),
                    pkgs={
                        "grpcio": [
                            "~=1.12.0",
                            "~=1.22.0",
                        ],
                    },
                ),
                Venv(
                    pys=["3.7"],
                    pkgs={
                        "grpcio": [
                            "~=1.20.0",
                            latest,
                        ],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.8", max_version="3.9"),
                    pkgs={
                        "grpcio": ["~=1.24.0", "~=1.40.0", latest],
                    },
                ),
                Venv(
                    pys="3.10",
                    pkgs={
                        "grpcio": ["~=1.42.0", latest],
                    },
                ),
                Venv(pys="3.11", pkgs={"grpcio": ["~=1.49.0", latest]}),
            ],
        ),
        Venv(
            name="grpc_aio",
            command="python -m pytest {cmdargs} tests/contrib/grpc_aio",
            pkgs={
                "googleapis-common-protos": latest,
                "pytest-asyncio": latest,
            },
            venvs=[
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.6"),
                    pkgs={
                        "grpcio": ["~=1.32.0", latest],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.7", max_version="3.8"),
                    pkgs={
                        "grpcio": ["~=1.32.0", latest],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.9", max_version="3.9"),
                    pkgs={
                        # 3.9 wheels are not provided in 1.32
                        "grpcio": ["~=1.33.0", latest],
                    },
                ),
                Venv(
                    pys="3.10",
                    pkgs={
                        # 3.10 wheels were started to be provided in 1.41
                        # but the version contains some bugs resolved by https://github.com/grpc/grpc/pull/27635.
                        "grpcio": ["~=1.42.0", latest],
                    },
                ),
                Venv(pys="3.11", pkgs={"grpcio": ["~=1.49.0", latest]}),
            ],
        ),
        Venv(
            name="graphene",
            command="pytest {cmdargs} tests/contrib/graphene",
            pkgs={"pytest-asyncio": latest},
            venvs=[
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.9"),
                    pkgs={
                        # requires graphql-core<2.2 which is not supported in python 3.10
                        "graphene": ["~=2.0.0"],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.10"),
                    # FIXME[bytecode-3.11]: depends on bytecode module which doesn't yet support Python 3.11
                    pkgs={
                        "graphene": ["~=2.1.9", "~=3.0.0", latest],
                    },
                ),
            ],
        ),
        Venv(
            name="graphql",
            command="pytest {cmdargs} tests/contrib/graphql",
            pkgs={"pytest-asyncio": latest},
            venvs=[
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.9"),
                    pkgs={
                        # graphql-core<2.2 is not supported in python 3.10
                        "graphql-core": ["~=2.0.0", "~=2.1.0"],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.10"),
                    # FIXME[bytecode-3.11]: depends on bytecode module which doesn't yet support Python 3.11
                    pkgs={
                        "graphql-core": ["~=2.2.0", "~=2.3.0", "~=3.0.0", "~=3.1.0", "~=3.2.0", latest],
                    },
                ),
            ],
        ),
        Venv(
            name="rq",
            command="pytest tests/contrib/rq",
            venvs=[
                Venv(
                    pys=select_pys(max_version="2.7"),
                    pkgs={
                        "rq": [
                            "~=1.0.0",
                            "~=1.1.0",
                            "~=1.2.0",
                            "~=1.3.0",
                        ],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.5"),
                    pkgs={
                        "rq": [
                            "~=1.0.0",
                            "~=1.1.0",
                            "~=1.2.0",
                            "~=1.3.0",
                            "~=1.4.0",
                            "~=1.5.0",
                            "~=1.6.0",
                            "~=1.7.0",
                            "~=1.8.0",
                            "~=1.9.0",
                            "~=1.10.0",
                            latest,
                        ],
                        # https://github.com/rq/rq/issues/1469 rq [1.0,1.8] is incompatible with click 8.0+
                        "click": "==7.1.2",
                    },
                ),
            ],
        ),
        Venv(
            name="httpx",
            pys=select_pys(min_version="3.6"),
            command="pytest {cmdargs} tests/contrib/httpx",
            pkgs={
                "pytest-asyncio": latest,
                "httpx": [
                    "~=0.14.0",
                    "~=0.15.0",
                    "~=0.16.0",
                    "~=0.17.0",
                    "~=0.18.0",
                    "~=0.22.0",
                    latest,
                ],
            },
        ),
        Venv(
            name="urllib3",
            command="pytest {cmdargs} tests/contrib/urllib3",
            venvs=[
                Venv(
                    pys=select_pys(max_version="3.9"),
                    pkgs={"urllib3": ["~=1.22.0", ">=1.23,<1.27", latest]},
                ),
                Venv(
                    pys=select_pys(min_version="3.10"),
                    pkgs={"urllib3": [">=1.23,<1.27", latest]},
                ),
            ],
        ),
        Venv(
            name="cassandra",
            venvs=[
                # cassandra-driver does not officially support 3.10
                # TODO: fix sporadically failing tests in cassandra-driver v3.25.0 and py3.10
                Venv(
                    pys=["3.9"],
                    pkgs={"cassandra-driver": latest},
                ),
                # releases 3.7 and 3.8 are broken on Python >= 3.7
                # (see https://github.com/r4fek/django-cassandra-engine/issues/104)
                Venv(pys=["3.7", "3.8"], pkgs={"cassandra-driver": ["~=3.6.0", "~=3.15.0", "~=3.24.0", latest]}),
                Venv(
                    pys=select_pys(max_version="3.6"),
                    pkgs={
                        "cassandra-driver": [("~=3.%d.0" % m) for m in range(6, 9)] + ["~=3.15.0", "~=3.24.0", latest]
                    },
                ),
            ],
            command="pytest {cmdargs} tests/contrib/cassandra",
        ),
        Venv(
            name="algoliasearch",
            pys=select_pys(),
            command="pytest {cmdargs} tests/contrib/algoliasearch",
            pkgs={
                "algoliasearch": [">=1.2,<2", ">=2,<3", latest],
            },
        ),
        Venv(
            name="aiopg",
            venvs=[
                Venv(
                    pys=["3.5", "3.6"],
                    pkgs={
                        "aiopg": ["~=0.12.0", "~=0.15.0"],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.7", max_version="3.9"),
                    pkgs={
                        "aiopg": ["~=0.15.0", "~=0.16.0"],  # TODO: add latest
                    },
                ),
            ],
            pkgs={
                "sqlalchemy": latest,
            },
            command="pytest {cmdargs} tests/contrib/aiopg",
        ),
        Venv(
            name="aiohttp",
            command="pytest {cmdargs} tests/contrib/aiohttp",
            pkgs={
                "pytest-aiohttp": [latest],
            },
            venvs=[
                Venv(
                    pys=select_pys(min_version="3.5", max_version="3.6"),
                    pkgs={
                        "aiohttp": ["~=2.0", "~=2.1", "~=2.2", "~=2.3"],
                        "async-timeout": ["<4.0.0"],
                        "yarl": "~=0.18.0",
                    },
                ),
                Venv(
                    # pytest-asyncio is incompatible with aiohttp 3.0+ in Python 3.6
                    pys="3.6",
                    pkgs={
                        "aiohttp": [
                            "~=3.0",
                            "~=3.2",
                            "~=3.4",
                            "~=3.6",
                            "~=3.8",
                            latest,
                        ],
                        "yarl": "~=1.0",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.7"),
                    pkgs={
                        "pytest-asyncio": [latest],
                        "aiohttp": [
                            "~=3.0",
                            "~=3.2",
                            "~=3.4",
                            "~=3.6",
                            "~=3.8",
                            latest,
                        ],
                        "yarl": "~=1.0",
                    },
                ),
            ],
        ),
        Venv(
            name="aiohttp_jinja2",
            command="pytest {cmdargs} tests/contrib/aiohttp_jinja2",
            pkgs={
                "pytest-aiohttp": [latest],
            },
            venvs=[
                Venv(
                    pys="3.6",
                    pkgs={
                        "aiohttp": [
                            "~=3.4",
                            "~=3.6",
                            latest,
                        ],
                        "aiohttp_jinja2": [
                            "~=1.3.0",
                            "~=1.4.0",
                            latest,
                        ],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.7"),
                    pkgs={
                        "pytest-asyncio": [latest],
                        "aiohttp": [
                            "~=3.4",
                            "~=3.6",
                            "~=3.8",
                            latest,
                        ],
                    },
                    venvs=[
                        Venv(
                            pkgs={
                                "aiohttp_jinja2": [
                                    "~=1.3.0",
                                    "~=1.4.0",
                                    latest,
                                ],
                                # Jinja2 makes breaking changes in 3.0.
                                "jinja2": "<3.0",
                                # MarkupSafe makes breaking changes in 2.1.
                                "MarkupSafe": "<2.1",
                            }
                        ),
                        Venv(
                            pkgs={
                                "aiohttp_jinja2": [
                                    "~=1.5.0",
                                    latest,
                                ],
                                "jinja2": latest,
                            }
                        ),
                    ],
                ),
            ],
        ),
        Venv(
            name="jinja2",
            venvs=[
                Venv(
                    pys=select_pys(max_version="3.9"),
                    pkgs={
                        "jinja2": [("~=2.%d.0" % m) for m in range(9, 12)],
                        # https://github.com/pallets/markupsafe/issues/282
                        # DEV: Breaking change made in 2.1.0 release
                        "markupsafe": "<2.0",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6"),
                    pkgs={
                        "jinja2": ["~=3.0.0", latest],
                    },
                ),
            ],
            command="pytest {cmdargs} tests/contrib/jinja2",
        ),
        Venv(
            name="rediscluster",
            pys=select_pys(),
            command="pytest {cmdargs} tests/contrib/rediscluster",
            pkgs={
                "redis-py-cluster": [">=1.3,<1.4", ">=2.0,<2.1", ">=2.1,<2.2", latest],
            },
        ),
        Venv(
            name="redis",
            venvs=[
                Venv(
                    pys=select_pys(),
                    command="pytest {cmdargs} --ignore-glob='*asyncio*' tests/contrib/redis",
                    pkgs={
                        "redis": [
                            ">=2.10,<2.11",
                            ">=3.0,<3.1",
                            ">=3.1,<3.2",
                            ">=3.2,<3.3",
                            ">=3.3,<3.4",
                            ">=3.4,<3.5",
                            ">=3.5,<3.6",
                        ],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6"),
                    command="pytest {cmdargs} tests/contrib/redis",
                    pkgs={
                        "pytest-asyncio": latest,
                        "redis": [
                            ">=4.2,<4.3",
                            latest,
                        ],
                    },
                ),
            ],
        ),
        Venv(
            name="aredis",
            pys=select_pys(min_version="3.6", max_version="3.9"),
            command="pytest {cmdargs} tests/contrib/aredis",
            pkgs={
                "pytest-asyncio": latest,
                "aredis": [
                    "~=1.1.0",
                    latest,
                ],
            },
        ),
        Venv(
            name="yaaredis",
            pys=select_pys(min_version="3.6", max_version="3.9"),
            command="pytest {cmdargs} tests/contrib/yaaredis",
            pkgs={
                "pytest-asyncio": latest,
                "yaaredis": [
                    "~=2.0.0",
                    latest,
                ],
            },
        ),
        Venv(
            name="sanic",
            command="pytest {cmdargs} tests/contrib/sanic",
            pkgs={
                "pytest-asyncio": latest,
                "requests": latest,
            },
            venvs=[
                Venv(
                    pys=select_pys(min_version="3.7", max_version="3.9"),
                    pkgs={
                        "sanic": ["~=19.12", "~=20.12"],
                        "pytest-sanic": ["~=1.6.2"],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.7"),
                    pkgs={
                        "sanic": ["~=21.3.0"],
                        "pytest-sanic": latest,
                        "httpx": ["~=0.15.4"],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.7"),
                    pkgs={
                        "sanic": [
                            "~=21.6.0",
                        ],
                        "pytest-sanic": latest,
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.7"),
                    pkgs={
                        "sanic": [
                            "~=21.9.0",
                            "~=21.12.0",
                        ],
                        "sanic-testing": "~=0.8.3",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.7"),
                    pkgs={
                        "sanic": "~=22.3.0",
                        "sanic-testing": "~=22.3.0",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.7"),
                    pkgs={
                        "sanic": "~=22.9.0",
                        "sanic-testing": "~=22.9.0",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.7"),
                    pkgs={
                        "sanic": latest,
                        "sanic-testing": latest,
                    },
                ),
            ],
        ),
        Venv(
            name="snowflake",
            command="pytest {cmdargs} tests/contrib/snowflake",
            pkgs={
                "responses": "~=0.16.0",
            },
            venvs=[
                Venv(
                    # 2.2.0 dropped 2.7 support
                    pys=select_pys(max_version="3.9"),
                    pkgs={
                        "snowflake-connector-python": [
                            "~=2.0.0",
                            "~=2.1.0",
                        ],
                    },
                ),
                Venv(
                    # 2.3.7 dropped 3.5 support
                    pys=select_pys(min_version="3.5", max_version="3.9"),
                    pkgs={
                        "snowflake-connector-python": [
                            "~=2.2.0",
                        ],
                    },
                ),
                Venv(
                    # 2.3.x needs pyarrow >=0.17,<0.18 which does not install on Python 3.9
                    pys=select_pys(min_version="3.6", max_version="3.8"),
                    pkgs={
                        "snowflake-connector-python": [
                            "~=2.3.0",
                        ],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.9"),
                    pkgs={
                        "snowflake-connector-python": [
                            "~=2.4.0",
                            "~=2.5.0",
                            "~=2.6.0",
                            latest,
                        ],
                    },
                ),
            ],
        ),
        Venv(
            pys=["3"],
            name="reno",
            pkgs={
                "reno": latest,
            },
            command="reno {cmdargs}",
        ),
        Venv(
            name="aioredis",
            # aioredis was merged into redis as of v2.0.1, no longer maintained and does not support Python 3.11 onward
            pys=select_pys(min_version="3.6", max_version="3.10"),
            command="pytest {cmdargs} tests/contrib/aioredis",
            pkgs={
                "pytest-asyncio": latest,
                "aioredis": [
                    "~=1.3.0",
                    latest,
                ],
            },
        ),
        Venv(
            name="asyncpg",
            command="pytest {cmdargs} tests/contrib/asyncpg",
            pkgs={
                "pytest-asyncio": latest,
            },
            venvs=[
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.8"),
                    pkgs={
                        "asyncpg": [
                            "~=0.18.0",
                            "~=0.20.0",
                            "~=0.22.0",
                            "~=0.24.0",
                            latest,
                        ],
                    },
                ),
                Venv(
                    pys=["3.9"],
                    pkgs={
                        "asyncpg": [
                            "~=0.20.0",
                            "~=0.22.0",
                            "~=0.24.0",
                            latest,
                        ],
                    },
                ),
                Venv(
                    pys=["3.10"],
                    pkgs={
                        "asyncpg": [
                            "~=0.24.0",
                            latest,
                        ],
                    },
                ),
                Venv(
                    pys=["3.11"],
                    pkgs={"asyncpg": latest},
                ),
            ],
        ),
        Venv(
            name="asyncio",
            command="pytest {cmdargs} tests/contrib/asyncio",
            pys=select_pys(min_version="3.5"),
            pkgs={
                "pytest-asyncio": latest,
            },
        ),
        Venv(
            name="futures",
            command="pytest {cmdargs} tests/contrib/futures",
            venvs=[
                # futures is backported for 2.7
                Venv(pys=["2.7"], pkgs={"futures": ["~=3.0", "~=3.1", "~=3.2", "~=3.4"]}),
                Venv(
                    pys=select_pys(min_version="3.5"),
                ),
            ],
        ),
        Venv(
            name="sqlite3",
            command="pytest {cmdargs} tests/contrib/sqlite3",
            pys=select_pys(),
        ),
        Venv(
            name="dbapi",
            command="pytest {cmdargs} tests/contrib/dbapi",
            pys=select_pys(),
        ),
        Venv(
            name="dogpile_cache",
            command="pytest {cmdargs} tests/contrib/dogpile_cache",
            venvs=[
                Venv(
                    pys=select_pys(max_version="3.5"),
                    pkgs={
                        "dogpile.cache": [
                            "==0.6.*",
                            "==0.7.*",
                            "==0.8.*",
                            "==0.9.*",
                        ],
                        "decorator": "<5",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.6", max_version="3.10"),
                    pkgs={
                        "dogpile.cache": [
                            "==0.6.*",
                            "==0.7.*",
                            "==0.8.*",
                            "==0.9.*",
                            "==1.0.*",
                            latest,
                        ],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.11"),
                    pkgs={
                        "dogpile.cache": [
                            "==0.8.*",
                            "==0.9.*",
                            "==1.0.*",
                            "==1.1.*",
                            latest,
                        ],
                    },
                ),
            ],
        ),
        Venv(
            name="consul",
            pys=select_pys(),
            command="pytest {cmdargs} tests/contrib/consul",
            pkgs={
                "python-consul": [
                    ">=0.7,<1.0",
                    ">=1.0,<1.1",
                    ">=1.1,<1.2",
                    latest,
                ],
            },
        ),
        Venv(
            name="opentracer",
            pkgs={"opentracing": latest},
            venvs=[
                Venv(
                    pys=select_pys(),
                    command="pytest {cmdargs} tests/opentracer/core",
                ),
                Venv(
                    pys=select_pys(min_version="3.5"),
                    command="pytest {cmdargs} tests/opentracer/test_tracer_asyncio.py",
                    pkgs={"pytest-asyncio": latest},
                ),
                Venv(
                    pys=select_pys(min_version="3.5"),
                    command="pytest {cmdargs} tests/opentracer/test_tracer_tornado.py",
                    # TODO: update opentracing tests to be compatible with Tornado v6.
                    # https://github.com/opentracing/opentracing-python/issues/136
                    pkgs={
                        "tornado": ["~=4.4.0", "~=4.5.0", "~=5.0.0", "~=5.1.0"],
                    },
                ),
                Venv(
                    command="pytest {cmdargs} tests/opentracer/test_tracer_gevent.py",
                    venvs=[
                        Venv(
                            pys=select_pys(max_version="3.6"),
                            pkgs={
                                "gevent": ["~=1.1.0", "~=1.2.0"],
                                "greenlet": "~=1.0",
                            },
                        ),
                        Venv(
                            pys=select_pys(min_version="3.7", max_version="3.8"),
                            pkgs={
                                "gevent": ["~=1.3.0", "~=1.4.0"],
                                # greenlet>0.4.17 wheels are incompatible with gevent and python>3.7
                                # This issue was fixed in gevent v20.9:
                                # https://github.com/gevent/gevent/issues/1678#issuecomment-697995192
                                "greenlet": "<0.4.17",
                            },
                        ),
                        Venv(
                            pys="3.9",
                            pkgs={
                                "gevent": ["~=20.9.0", "~=20.12.0", "~=21.1.0"],
                                "greenlet": "~=1.0",
                            },
                        ),
                        Venv(
                            pys="3.10",
                            pkgs={
                                "gevent": "~=21.8.0",
                            },
                        ),
                        Venv(
                            pys="3.11",
                            pkgs={
                                "gevent": "~=22.8.0",
                            },
                        ),
                    ],
                ),
            ],
        ),
        Venv(
            name="pyodbc",
            command="pytest {cmdargs} tests/contrib/pyodbc",
            # FIXME: check if this constraint is no longer required
            pys=select_pys(max_version="3.9"),
            pkgs={"pyodbc": [">=3.0,<4.0", ">=4.0,<5.0", latest]},
        ),
        Venv(
            name="pylibmc",
            command="pytest {cmdargs} tests/contrib/pylibmc",
            venvs=[
                Venv(
                    pys=select_pys(max_version="3.10"),
                    pkgs={
                        "pylibmc": [">=1.4,<1.5", ">=1.5,<1.6", latest],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.11"),
                    pkgs={
                        "pylibmc": [">=1.6,<1.7", latest],
                    },
                ),
            ],
        ),
        Venv(
            name="kombu",
            command="pytest {cmdargs} tests/contrib/kombu",
            venvs=[
                Venv(
                    pys=select_pys(max_version="3.6"),
                    pkgs={
                        "kombu": [
                            ">=4.0,<4.1",
                            ">=4.1,<4.2",
                            ">=4.2,<4.3",
                            ">=4.3,<4.4",
                            ">=4.4,<4.5",
                            ">=4.5,<4.6",
                            ">=4.6,<4.7",
                            latest,
                        ],
                        # kombu using deprecated shims removed in importlib-metadata 5.0 pre-Python 3.8
                        "importlib_metadata": "<5.0",
                    },
                ),
                # Kombu>=4.2 only supports Python 3.7+
                Venv(
                    pys="3.7",
                    pkgs={
                        "kombu": [">=4.2,<4.3", ">=4.3,<4.4", ">=4.4,<4.5", ">=4.5,<4.6", ">=4.6,<4.7", latest],
                        # kombu using deprecated shims removed in importlib-metadata 5.0 pre-Python 3.8
                        "importlib_metadata": "<5.0",
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.8", max_version="3.9"),
                    pkgs={
                        "kombu": [">=4.2,<4.3", ">=4.3,<4.4", ">=4.4,<4.5", ">=4.5,<4.6", ">=4.6,<4.7", latest],
                    },
                ),
                Venv(
                    pys="3.10",
                    pkgs={
                        "kombu": [">=4.3,<4.4", ">=4.4,<4.5", ">=4.5,<4.6", ">=4.6,<4.7", latest],
                    },
                ),
                Venv(
                    pys="3.11",
                    pkgs={
                        "kombu": [">=5.0,<5.1", ">=5.1,<5.2", latest],
                    },
                ),
            ],
        ),
        Venv(
            name="tornado",
            command="python -m pytest {cmdargs} tests/contrib/tornado",
            venvs=[
                Venv(
                    pys="2.7",
                    pkgs={"tornado": [">=4.4,<4.5", ">=4.5,<4.6"], "futures": ["~=3.0", "~=3.1", "~=3.2", latest]},
                ),
                Venv(
                    pys=select_pys(max_version="3.9"),
                    pkgs={
                        "tornado": [">=4.4,<4.5", ">=4.5,<4.6"],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.7", max_version="3.9"),
                    pkgs={
                        "tornado": [">=5.0,<5.1", ">=5.1,<5.2", ">=6.0,<6.1", latest],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.10", max_version="3.11"),
                    pkgs={
                        "tornado": [">=6.0,<6.1", latest],
                    },
                ),
            ],
        ),
        Venv(
            name="mysqldb",
            command="pytest {cmdargs} tests/contrib/mysqldb",
            venvs=[
                Venv(
                    pys=select_pys(max_version="3.9"),
                    pkgs={
                        "mysqlclient": [">=1.3,<1.4", ">=1.4,<1.5", latest],
                    },
                ),
                Venv(
                    pys=select_pys(min_version="3.10"),
                    pkgs={
                        "mysqlclient": [">=1.4,<1.5", latest],
                    },
                ),
            ],
        ),
        Venv(
            name="molten",
            command="pytest {cmdargs} tests/contrib/molten",
            pys=select_pys(min_version="3.6"),
            pkgs={
                "molten": [">=0.6,<0.7", ">=0.7,<0.8", ">=1.0,<1.1", latest],
            },
        ),
    ],
)
