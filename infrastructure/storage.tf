resource "digitalocean_spaces_bucket" "assets" {
  name   = "kodaflux-assets"
  region = var.region
  acl    = "public-read"
}

resource "digitalocean_database_cluster" "postgres" {
  name       = "kodaflux-db-cluster"
  engine     = "pg"
  version    = var.postgres_version
  size       = "db-s-1vcpu-1gb"
  region     = var.region
  node_count = 1
}

resource "digitalocean_database_cluster" "redis" {
  name       = "kodaflux-redis-cluster"
  engine     = "valkey"
  version    = "8"
  size       = "db-s-1vcpu-1gb"
  region     = var.region
  node_count = 1
}
