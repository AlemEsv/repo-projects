# ej 1
variable "connection_string_tpl" {
  type = string
  default = "" # vacio
}

variable "db_user" {
  description = "usuario"
  type        = string
}

variable "db_password" {
  description = "contraseña"
  type        = string
  sensitive   = true
}

variable "db_host" {
  description = "host"
  type        = string
}

variable "db_port" {
  description = "puerto"
  type        = number
}

variable "db_name" {
  description = "nombre de la base de datos"
  type        = string
}