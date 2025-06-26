from local_iac_patterns.iac_patterns.factory import NullResourceFactory
from local_iac_patterns.iac_patterns.adapter import MockBucketAdapter
from local_iac_patterns.iac_patterns.builder import InfrastructureBuilder
import json
import tempfile
import os

def test_adapter_in_builder_export():
    # Crea un null_resource usando la factory
    null_block = NullResourceFactory.create("mybucket")
    # Usa el adapter para convertirlo en un mock_cloud_bucket
    bucket_block = MockBucketAdapter(null_block).to_bucket()
    # Usa el builder para agregar el recurso adaptado
    builder = InfrastructureBuilder("dev")
    builder.module.add(bucket_block)
    # Exporta a un archivo temporal
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "main.tf.json")
        builder.export(path)
        with open(path) as f:
            data = json.load(f)
        # Validación: debe existir el recurso mock_cloud_bucket
        assert "resource" in data
        assert "mock_cloud_bucket" in data["resource"]
        assert "mybucket" in data["resource"]["mock_cloud_bucket"]