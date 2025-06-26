from local_iac_patterns.iac_patterns.prototype import ResourcePrototype

#mutator
def add_welcome_file(block: dict):
    block["resource"]["null_resource"]["app_0"]["triggers"]["welcome"] = "¡Hola!"
    block["resource"]["local_file"] = {
        "welcome_txt": {
            "content": "Bienvenido",
            "filename": "${path.module}/bienvenida.txt"
        }
    }

def test_clone_with_local_file():
    prototipo_base = {
        "resource": {
            "null_resource": {
                "app_0": {
                    "triggers": {}
                }
            }
        }
    }
    proto = ResourcePrototype(prototipo_base)
    clon = proto.clone(mutator=add_welcome_file)
    assert "local_file" in clon.data["resource"]
    assert clon.data["resource"]["null_resource"]["app_0"]["triggers"]["welcome"] == "¡Hola!"