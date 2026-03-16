variable "do_token" {
  type        = string
  description = "DigitalOcean API access token"
  sensitive   = true
}

variable "environment" {
  type        = string
  description = "Type of environment where KodaFlux will run."
  default     = "Development"
}

variable "region" {
  type        = string
  description = "The region where KodaFlux resources will be provisioned"
  default     = "fra1"
}

variable "postgres_version" {
  type        = string
  description = "Major version number representing the version of Postgres"
  default     = "16"
}

variable "container_registry_type" {
  type        = string
  description = "The type of container registry where the images can be pulled"
  default     = "DOCR"
}

variable "backend_image_name" {
  type        = string
  description = "The name of the backend service's container image"
  default     = "kodaflux-backend"
}

variable "frontend_source_repo" {
  type        = string
  description = "The URL to the repo where the frontend source code lives"
  default     = "https://github.com/koda-flux/kodaflux.git"
}

variable "spaces_access_key_id" {
  type        = string
  description = "The access key id used to access Digitalocean Spaces"
  sensitive   = true
}

variable "spaces_secret_access_key" {
  type        = string
  description = "The secret access key used to access DigitalOcean Spaces"
  sensitive   = true
}

variable "agent_url" {
  type        = string
  description = "The URL to the deployed Gradeint ADK agent"
}

variable "api_url" {
  type        = string
  description = "The base URL to the API"
  default     = "https://kodaflux-6caab.ondigitalocean.app/api"
}
