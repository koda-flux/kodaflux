resource "digitalocean_spaces_bucket" "assets" {
  name   = "kodaflux-assets"
  region = var.region
}

resource "digitalocean_database_cluster" "postgres" {
  name       = "kodaflux-db-cluster"
  engine     = "pg"
  version    = var.postgres_version
  size       = "db-s-1vcpu-1gb"
  region     = var.region
  node_count = 1
}
