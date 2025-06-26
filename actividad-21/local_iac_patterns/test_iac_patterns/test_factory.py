from local_iac_patterns.iac_patterns.factory import TimestampedNullResourceFactory

def test_timestamped_factor_simple():
    resource = TimestampedNullResourceFactory.create("test", fmt="%Y%m%d")
    assert "resource" in resource
    triggers = resource["resource"][0]["null_resource"][0]["test"][0]["triggers"]
    assert "timestamp" in triggers
    assert len(triggers["timestamp"]) == 8  # 'YYYYMMDD' tiene 8 caracteres