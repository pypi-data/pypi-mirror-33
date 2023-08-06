import pytest
from attrs_to_sql.utils import camelcase_to_underscore


@pytest.mark.parametrize(
    "camelcase, underscore",
    [("SampleModel", "sample_model"), ("Model", "model"), ("under_score", "under_score")],
)
def test_camelcase_to_underscore(camelcase, underscore):
    assert camelcase_to_underscore(camelcase) == underscore
