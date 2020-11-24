"""Test the rayvison_sync.rayvision_transfer functions."""

# pylint: disable=import-error
import pytest


def test_transport_info(rayvision_transfer):
    """Test we can get transport info."""
    assert sorted(list(rayvision_transfer.transport_info.keys())) == [
        'aspera', 'raysync']


def test_create_cmd(rayvision_transfer):
    """Test we can get a str."""
    cmd_params = [
        "upload_path",
        "D:/gitlab_demo/temp/demo_bak/rayvision/help/scenes/demo_scenc.mb",
        "/D/gitlab_demo/temp/demo_bak/rayvision/help/scenes/demo_scenc.mb",
        "1048576",
        "false", "config_bid"
    ]
    data = rayvision_transfer.create_cmd(cmd_params)
    # noqa: E501  # pylint: disable=line-too-long
    result = '-E "aspera" -H "45.251.92.29" -P "10221" -S "54252" -U "100093088" -T "upload_path" ' \
             '-L "D:/gitlab_demo/temp/demo_bak/rayvision/help/scenes/demo_scenc.mb" ' \
             '-R "/D/gitlab_demo/temp/demo_bak/rayvision/help/scenes/demo_scenc.mb" ' \
             '-r "2" -K "false" -s "1048576" -C "None"'
    assert result in data


@pytest.mark.parametrize("transports_json, domain_name, platform", [
    (None, None, '2'),
    (None, "jop.foxrenderfarm.com", '2'),
    (None, "task.renderbus.com", '2'),
    (None, "jop.test.com", '2'),
])
def test_parse_transports_json(rayvision_transfer, transports_json,
                               domain_name, platform):
    """Test we can get correct data."""
    result = rayvision_transfer.parse_transports_json(transports_json,
                                                      domain_name, platform)
    assert sorted(list(result.keys())) == ['aspera', 'raysync']