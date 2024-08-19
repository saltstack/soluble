"""
noxfile
~~~~~~~
Nox configuration script
"""
# pylint: disable=resource-leakage,3rd-party-module-not-gated
import datetime
import os
import pathlib
import shutil
import sys
from pathlib import Path

# fmt: off
if __name__ == "__main__":
    sys.stderr.write(
        "Do not execute this file directly. Use nox instead, it will know how to handle this file\n"
    )
    sys.stderr.flush()
    exit(1)
# fmt: on

import nox  # isort:skip
from nox.command import CommandFailed  # isort:skip

# Nox options
#  Reuse existing virtualenvs
nox.options.reuse_existing_virtualenvs = True
#  Don't fail on missing interpreters
nox.options.error_on_missing_interpreters = False

# Python versions to test against
PYTHON_VERSIONS = ("3", "3.8", "3.9", "3.10", "3.11")
# Be verbose when runing under a CI context
CI_RUN = os.environ.get("CI")
PIP_INSTALL_SILENT = CI_RUN is False
SKIP_REQUIREMENTS_INSTALL = "SKIP_REQUIREMENTS_INSTALL" in os.environ
EXTRA_REQUIREMENTS_INSTALL = os.environ.get("EXTRA_REQUIREMENTS_INSTALL")

COVERAGE_VERSION_REQUIREMENT = "coverage==5.5"

# Prevent Python from writing bytecode
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# Global Path Definitions
REPO_ROOT = pathlib.Path(__file__).resolve().parent
# Change current directory to REPO_ROOT
os.chdir(REPO_ROOT)

ARTIFACTS_DIR = REPO_ROOT / "artifacts"
# Make sure the artifacts directory exists
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

RUNTESTS_LOGFILE = ARTIFACTS_DIR / "runtests-{}.log".format(
    datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f")
)
COVERAGE_REPORT_DB = REPO_ROOT / ".coverage"
COVERAGE_REPORT_PROJECT = ARTIFACTS_DIR.relative_to(REPO_ROOT) / "coverage-project.xml"
COVERAGE_REPORT_TESTS = ARTIFACTS_DIR.relative_to(REPO_ROOT) / "coverage-tests.xml"
JUNIT_REPORT = ARTIFACTS_DIR.relative_to(REPO_ROOT) / "junit-report.xml"


def _get_session_python_version_info(session):
    try:
        version_info = session._runner._real_python_version_info
    except AttributeError:
        session_py_version = session.run_always(
            "python",
            "-c" 'import sys; sys.stdout.write("{}.{}.{}".format(*sys.version_info))',
            silent=True,
            log=False,
        )
        version_info = tuple(
            int(part) for part in session_py_version.split(".") if part.isdigit()
        )
        session._runner._real_python_version_info = version_info
    return version_info


def _get_pydir(session):
    version_info = _get_session_python_version_info(session)
    if version_info < (3, 8):
        session.error("Only Python >= 3.8 is supported")
    return "py{}.{}".format(*version_info)


@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    if SKIP_REQUIREMENTS_INSTALL is False:
        # Always have the wheel package installed
        session.install("wheel", silent=PIP_INSTALL_SILENT)
        session.install(COVERAGE_VERSION_REQUIREMENT, silent=PIP_INSTALL_SILENT)

        # Install requirements
        requirements_file = (
            REPO_ROOT / "requirements" / _get_pydir(session) / "tests.txt"
        )
        install_command = [
            "--progress-bar=off",
            "-r",
            str(requirements_file.relative_to(REPO_ROOT)),
        ]
        session.install(*install_command, silent=PIP_INSTALL_SILENT)

        if EXTRA_REQUIREMENTS_INSTALL:
            session.log(
                "Installing the following extra requirements because the "
                "EXTRA_REQUIREMENTS_INSTALL environment variable was set: "
                "EXTRA_REQUIREMENTS_INSTALL='%s'",
                EXTRA_REQUIREMENTS_INSTALL,
            )
            install_command = ["--progress-bar=off"]
            install_command += [
                req.strip() for req in EXTRA_REQUIREMENTS_INSTALL.split()
            ]
            session.install(*install_command, silent=PIP_INSTALL_SILENT)

    session.run("coverage", "erase")
    args = [
        "--rootdir",
        str(REPO_ROOT),
        f"--log-file={RUNTESTS_LOGFILE}",
        "--log-file-level=debug",
        "--show-capture=no",
        f"--junitxml={JUNIT_REPORT}",
        "--showlocals",
        "-ra",
        "-s",
    ]
    if session._runner.global_config.forcecolor:
        args.append("--color=yes")
    if not session.posargs:
        args.append("tests/")
    else:
        for arg in session.posargs:
            if arg.startswith("--color") and args[0].startswith("--color"):
                args.pop(0)
            args.append(arg)
        for arg in session.posargs:
            if arg.startswith("-"):
                continue
            if arg.startswith(f"tests{os.sep}"):
                break
            try:
                pathlib.Path(arg).resolve().relative_to(REPO_ROOT / "tests")
                break
            except ValueError:
                continue
        else:
            args.append("tests/")
    try:
        session.run("coverage", "run", "-m", "pytest", *args)
    finally:
        # Always combine and generate the XML coverage report
        try:
            session.run("coverage", "combine")
        except CommandFailed:
            # Sometimes some of the coverage files are corrupt which would
            # trigger a CommandFailed exception
            pass
        # Generate report for salt code coverage
        session.run(
            "coverage",
            "xml",
            "-o",
            str(COVERAGE_REPORT_PROJECT),
            "--omit=tests/*",
            "--include=soluble/*",
        )
        # Generate report for tests code coverage
        session.run(
            "coverage",
            "xml",
            "-o",
            str(COVERAGE_REPORT_TESTS),
            "--omit=soluble/*",
            "--include=tests/*",
        )
        # Move the coverage DB to artifacts/coverage in order for it to be archived by CI
        if COVERAGE_REPORT_DB.exists():
            shutil.move(
                str(COVERAGE_REPORT_DB), str(ARTIFACTS_DIR / COVERAGE_REPORT_DB.name)
            )


@nox.session(name="docs-html", python="3")
@nox.parametrize("clean", [False, True])
def docs_html(session, clean):
    """
    Build Sphinx HTML Documentation
    """
    _get_pydir(session)

    # Latest pip, setuptools, and wheel
    install_command = ["--progress-bar=off", "-U", "pip", "setuptools", "wheel"]
    session.install(*install_command, silent=True)

    # Install requirements
    requirements_file = Path("requirements", "docs.txt")
    install_command = ["--progress-bar=off", "-r", str(requirements_file)]
    session.install(*install_command, silent=True)

    build_dir = Path("docs", "_build", "html")
    sphinxopts = "-n"  # Use W as arg in future
    if clean:
        sphinxopts += "E"
        base_modules_dir = "soluble"
        autogen_config = []
        skip_dir_config = ["contracts"]
        gen_docs_dir_parent = "docs/ref"
        args = ["--separate", "--tocfile", "index", "-f", "-o"]
        index_ref_toc = ""
        # For each module dir, generate api docs for all subdirs
        for dir_target in autogen_config:
            module_listing = []
            dir_type = dir_target.split("/")[0]
            index_ref_toc += f"   ref/{dir_type}/index\n"
            sub_dirs = [
                f.path
                for f in os.scandir(f"{base_modules_dir}/{dir_target}")
                if f.is_dir()
            ]

            # Include all functions that might be defined in the base directory
            sub_dirs.append(f"{base_modules_dir}/{dir_target}")
            sub_dirs.append(f"{base_modules_dir}/{dir_type}")

            # Generate docs/ref dir tree
            for sub_dir in sub_dirs:
                module_dir = sub_dir.split("/")[-1]
                if module_dir in skip_dir_config:
                    continue
                if module_dir == dir_type:
                    new_module_dir_path = f"{gen_docs_dir_parent}/{module_dir}"
                else:
                    module_listing.append(
                        "   " + module_dir.replace("\\", "/") + "/index\n"
                    )
                    new_module_dir_path = (
                        f"{gen_docs_dir_parent}/{dir_type}/{module_dir}"
                    )
                Path(new_module_dir_path).mkdir(parents=True, exist_ok=True)
                session.run(
                    "sphinx-apidoc",
                    *args,
                    new_module_dir_path,
                    sub_dir,
                    f"{sub_dir}/init.py",
                    external=True,
                )
                # sphinx-apidoc has a bug where title underlines need to be fixed
                # Fix title underlines to appropriate length
                new_rst_files = [
                    f.path for f in os.scandir(new_module_dir_path) if f.is_file()
                ]
                for new_rst_file in new_rst_files:
                    # if this is the top level module, add direct files to index.rst
                    if module_dir == dir_type and not new_rst_file.endswith(
                        "index.rst"
                    ):
                        module_listing.append(
                            "   "
                            + f"{(new_rst_file.split('/')[-1]).replace('.rst', '')}\n"
                        )
                    with open(new_rst_file) as target_file_reader:
                        target_file_content = target_file_reader.read()
                    new_target_file_content = target_file_content.replace(
                        ".. automodule:: ",
                        ".. automodule:: "
                        + sub_dir.replace("/", ".").replace("\\", ".")
                        + ".",
                    )
                    rst_file_title_truncated = new_target_file_content.split("\n")[
                        0
                    ].replace(" module", "")
                    rst_file_title_length = len(rst_file_title_truncated)
                    rst_underline_length = len(new_target_file_content.split("\n")[1])
                    if (
                        rst_file_title_length != rst_underline_length
                        or rst_file_title_length < 3
                    ):
                        if rst_file_title_length < 3:
                            rst_new_underline = "==="
                        else:
                            rst_new_underline = "=" * rst_file_title_length
                        new_target_file_content = new_target_file_content.replace(
                            new_target_file_content.split("\n")[1], rst_new_underline
                        )
                    new_target_file_content = new_target_file_content.replace(
                        new_target_file_content.split("\n")[0], rst_file_title_truncated
                    )
                    with open(new_rst_file, "w") as target_file_writer:
                        target_file_writer.write(new_target_file_content)
            # Write root index file for all modules
            dir_type_title = f"{dir_type} modules"
            underline_length = len(dir_type_title)
            underline = "=" * underline_length
            module_listing.sort()
            index_contents = [
                f"{dir_type_title}\n",
                f"{underline}\n",
                "\n",
                ".. include:: /_includes/modindex-note.rst\n",
                "\n",
                ".. toctree::\n",
                "   :maxdepth: 2\n",
                "\n",
            ] + module_listing
            # Populate main base module index with all sub-indices
            with open(f"{gen_docs_dir_parent}/{dir_type}/index.rst", "w") as rst_file:
                rst_file.writelines(index_contents)
        # Create TOC reference section
        with open("docs/_includes/reference-toc-template.rst") as target_file_reader:
            target_file_content = target_file_reader.read()
        new_target_file_content = target_file_content.replace(
            "   .. REF_PLACEHOLDER\n", index_ref_toc
        )
        with open("docs/_includes/reference-toc.rst", "w") as target_file_writer:
            target_file_writer.write(new_target_file_content)
    args = [sphinxopts, "--keep-going", "docs", str(build_dir)]

    session.run("sphinx-build", *args, external=True)


@nox.session(python="3")
def docs(session) -> None:
    """
    Build and serve the Sphinx HTML documentation, with live reloading on file changes, via sphinx-autobuild.

    Note: Only use this in INTERACTIVE DEVELOPMENT MODE. This SHOULD NOT be called
        in CI/CD pipelines, as it will hang.
    """
    _get_pydir(session)

    # Latest pip, setuptools, and wheel
    install_command = ["--progress-bar=off", "-U", "pip", "setuptools", "wheel"]
    session.install(*install_command, silent=True)

    # Install requirements
    requirements_file = Path("requirements", "docs.txt")
    install_command = ["--progress-bar=off", "-r", str(requirements_file)]
    session.install(*install_command, silent=True)

    # Install autobuild req
    install_command = ["--progress-bar=off", "-U", "sphinx-autobuild"]
    session.install(*install_command, silent=True)

    # Launching LIVE reloading Sphinx session
    build_dir = Path("docs", "_build", "html")
    args = ["--watch", ".", "--open-browser", "docs", str(build_dir)]
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args)
