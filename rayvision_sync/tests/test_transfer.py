"""Test the rayvison_sync.rayvision_transfer functions."""

# pylint: disable=import-error
import pytest


def test_transport_info(rayvision_transfer):
    """Test we can get transport info."""
    assert sorted(list(rayvision_transfer.transport_info.keys())) == [
        'engine_type',
        'server_ip',
        'server_name',
        'server_port']


def test_create_cmd(rayvision_transfer):
    """Test we can get a str."""
    cmd_params = [
        "upload_files",
        "D:/gitlab_demo/temp/demo_bak/rayvision/help/scenes/demo_scenc.mb",
        "/D/gitlab_demo/temp/demo_bak/rayvision/help/scenes/demo_scenc.mb",
        "1048576",
        "false", "config_bid"
    ]
    data = rayvision_transfer.create_cmd(cmd_params)
    # noqa: E501  # pylint: disable=line-too-long
    result = '"aspera" "CTCC" "45.251.92.29" "10221" "54252" "100093088" "upload_files" ' \
             '"D:/gitlab_demo/temp/demo_bak/rayvision/help/scenes/demo_scenc.mb" ' \
             '"/D/gitlab_demo/temp/demo_bak/rayvision/help/scenes/demo_scenc.mb" "1" "false" "1048576" "None" '
    assert result in data


@pytest.mark.parametrize("transports_json, domain_name, platform", [
    (None, None, '2'),
    (None, "jop.foxrenderfarm.com", '3'),
    (None, "task.renderbus.com", '3'),
    (None, "jop.test.com", '2'),
])
def test_parse_transports_json(rayvision_transfer, transports_json,
                               domain_name, platform):
    """Test we can get correct data."""
    result = rayvision_transfer.parse_transports_json(transports_json,
                                                      domain_name, platform)
    assert sorted(list(result.keys())) == ['engine_type', 'server_ip',
                                           'server_name', 'server_port']
