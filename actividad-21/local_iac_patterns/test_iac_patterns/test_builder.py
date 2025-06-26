from local_iac_patterns.iac_patterns.builder import InfrastructureBuilder
import json
import tempfile
import os

def test_build_group_export_structure():
    builder = InfrastructureBuilder("dev")
    builder.build_group("mygroup", 2)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "main.tf.json")
        builder.export(path)
        with open(path, "r") as f:
            data = json.load(f)
        # Validar estructura
        assert "module" in data
        assert "mygroup" in data["module"]
        assert "resource" in data["module"]["mygroup"]
        # Debe haber dos recursos null_resource
        resources = data["module"]["mygroup"]["resource"]
        assert any("null_resource" in r for r in resources)