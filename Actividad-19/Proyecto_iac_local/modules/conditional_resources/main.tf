resource "null_resource" "item" {
  for_each = { for o in var.items : o.name => o if o.enabled }
  triggers = {
    item_name = each.key
    item_size = each.value.size
  }
}