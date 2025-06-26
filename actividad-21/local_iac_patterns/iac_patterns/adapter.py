# adapter.py
class MockBucketAdapter:
    """
    Adapter que transforma un bloque null_resource en un recurso simulado mock_cloud_bucket.
    Permite reutilizar la estructura de null_resource para otros propósitos en pruebas o integración.
    """
    def __init__(self, null_block: dict):
        self.null = null_block

    def to_bucket(self) -> dict:
        # Mapear triggers a parámetros de bucket simulado
        name = list(self.null["resource"]["null_resource"].keys())[0]
        return {
            "resource": {
                "mock_cloud_bucket": {
                    name: {"name": name, **self.null["resource"]["null_resource"][name]["triggers"]}
                }
            }
        }