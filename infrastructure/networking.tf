resource "digitalocean_vpc" "main" {
  name   = "kodaflux-vpc"
  region = var.region
}

resource "digitalocean_database_firewall" "database_firewall" {
  cluster_id = digitalocean_database_cluster.postgres.id
  rule {
    type  = "app"
    value = digitalocean_app.kodaflux.id
  }
}
