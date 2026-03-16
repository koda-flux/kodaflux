resource "digitalocean_project" "project" {
  name        = "kodaflux"
  description = "Documentation aggregator project"
  purpose     = "Web Application"
  environment = var.environment
  resources = [
    digitalocean_app.kodaflux_app.urn,
    digitalocean_spaces_bucket.assets.urn,
    digitalocean_database_cluster.postgres.urn,
  ]
}
