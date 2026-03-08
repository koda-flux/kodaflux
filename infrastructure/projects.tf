resource "digitalocean_project" "project" {
  name        = "kodaflux"
  description = "Documentation aggregator project"
  purpose     = "Web Application"
  environment = var.environment
  resources   = []
}
