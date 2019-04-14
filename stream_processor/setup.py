from setuptools import setup, find_packages

test_deps = ["pytest"]

extras = {
    "testing": test_deps
}

setup(
    name = "stream_processor",
    author = "Jonathan Keane",
    author_email = "jkeane@gmail.com",
    description = "",
    license = "MIT",
    version = "0.0.1",
    classifiers = ['Development Status :: 1 - Planning',
                   'Intended Audience :: Developers'],
    packages = find_packages(where="src"),
    package_dir = {"": "src"},
    namespace_packages = ["stream_processor"],
    install_requires = ["celery", "eventlet", "python-socketio", "requests"],
    tests_require = test_deps,
    extras_require = extras
)
