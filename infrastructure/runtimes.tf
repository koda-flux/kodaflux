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
      http_port          = "80"

      image {
        registry_type = var.container_registry_type
        repository    = var.backend_image_name
        tag           = "latest"

        deploy_on_push {
          enabled = true # Bleeding edge
        }
      }

      health_check {
        http_path             = "/healthz"
        initial_delay_seconds = 10
        period_seconds        = 90
        timeout_seconds       = 30
        failure_threshold     = 5
      }

      env {
        key   = "DATABASE_URL"
        value = digitalocean_database_cluster.postgres.uri
        scope = "RUN_TIME"
        type  = "SECRET"
      }

      env {
        key   = "CORS_ALLOWED_ORIGINS"
        value = "http://localhost:3000,"
        scope = "RUN_TIME"
        type  = "SECRET"
      }

      env {
        key   = "AGENT_URL"
        value = var.agent_url
        scope = "RUN_TIME"
      }

      env {
        key   = "DIGITALOCEAN_API_TOKEN"
        value = var.do_token
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

      build_command = "corepack enable && pnpm install --frozen-lockfile && pnpm run build --filter=frontend"
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
