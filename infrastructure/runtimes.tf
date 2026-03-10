resource "digitalocean_app" "kodaflux_app" {
  spec {
    name   = "kodaflux"
    region = var.region
    vpc {
      id = digitalocean_vpc.main.id
    }

    service {
      name               = "backend"
      instance_count     = 1
      instance_size_slug = "apps-s-1vcpu-1gb"

      image {
        registry_type = var.container_registry_type
        registry      = var.container_registry
        repository    = "${var.container_repository_name}/${var.backend_image_name}"
        tag           = "latest"

        deploy_on_push {
          enabled = true # Makes system run on bleeding edge
        }
      }

      env {
        key   = "DATABASE_URL"
        value = digitalocean_database_cluster.postgres.private_uri
        scope = "RUN_TIME"
        type  = "SECRET"
      }
    }

    static_site {
      name = "frontend"

      git {
        repo_clone_url = var.frontend_source_repo
        branch         = "main"
      }

      build_command = "pnpm install --frozen-lockfile && pnpm run build --filter=frontend"
      output_dir    = "packages/frontend/out"
    }

    ingress {
      rule {
        component {
          name = "frontend"
        }
        match {
          path {
            prefix = "/"
          }
        }
      }

      rule {
        component {
          name = "backend"
        }
        match {
          path {
            prefix = "/api"
          }
        }
      }
    }

    vpc {
      id = digitalocean_vpc.main.id
    }
  }
}
