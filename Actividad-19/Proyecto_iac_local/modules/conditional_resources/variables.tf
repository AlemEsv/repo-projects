variable "items" {
  type = list(object({
    name    = string 
    enabled = bool   
    size    = number # mb
  }))
}