def test_cli(mock_hub, hub):
    mock_hub.soluble.init.cli = hub.soluble.init.cli
    mock_hub.soluble.init.cli()
    mock_hub.pop.config.load.assert_called_once_with(["soluble"], "soluble")
