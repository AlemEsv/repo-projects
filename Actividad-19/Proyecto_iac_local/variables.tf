variable "nombre_entorno" {
  description = "Nombre base para el entorno generado."
  type        = string
  default     = "desarrollo"
}

variable "numero_instancias_app_simulada" {
  description = "Cuántas instancias de la app simulada crear."
  type        = number
  default     = 2
}

variable "mensaje_global" {
  description = "Un mensaje para incluir en varios archivos."
  type        = string
  default     = "Configuración gestionada por Terraform."
  sensitive   = true # Para mostrar en consola
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