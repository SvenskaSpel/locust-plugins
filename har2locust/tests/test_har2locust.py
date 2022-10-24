# pylint: disable=redefined-outer-name
import json
import pathlib
import subprocess
import os
import pytest
from har2locust.main import main, preprocessing, rendering

inputs_dir = pathlib.Path(__file__).parents[0] / "inputs"
outputs_dir = pathlib.Path(__file__).parents[0] / "outputs"

har_files = list(inputs_dir.glob("*.har"))
py_files = [outputs_dir / f.with_suffix(".py").name for f in har_files]

har_file = har_files[0]
py_file = py_files[0]

with open(har_file) as f:
    har = json.load(f)


def test_har_file_not_found():
    har_file_foo = inputs_dir / "foo.har"
    with pytest.raises(FileNotFoundError):
        main(har_file_foo)


def test_preprocessing_unsupported_resource_type():
    with pytest.raises(NotImplementedError, match="are not supported"):
        preprocessing(har, resource_type=["xhr", "foo", "bar"])


def test_rendering_without_preprocess():
    with pytest.raises(ValueError, match="har dict has wrong format."):
        rendering(har)


def test_rendering_syntax_error():
    with pytest.raises(
        AssertionError,
        match="Black failed to format the output - perhaps your template is broken?",
    ):
        rendering(
            preprocessing(har),
            template_dir=pathlib.Path(__file__).parents[0],
            template_name="broken_template.jinja2",
        )


# writing py file in tests/output for manual inspection
@pytest.mark.parametrize("har_file, py_file", zip(har_files, py_files))
def test_main(har_file, py_file):
    with open(py_file, encoding="utf-8") as f:
        expected_output = f.read()
    proc = subprocess.Popen(
        ["har2locust", har_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        cwd=os.path.join(os.path.dirname(__file__), "../"),
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, f"Bad return code {proc.returncode}, stderr: {stderr}"
    assert stdout.strip() == expected_output.strip()
