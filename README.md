<div align='center'>

![Kodaflux brand icon](./assets/kodaflux-logo.png)

A simple AI powered documentation aggregator.

</div>

> :warning: This project is currently under active development and will experience breaking changes often.
>
> You can have a look what what is being worked on and the generate roadmap in the [GitHub Project](https://github.com/orgs/koda-flux/projects/1)

# Overview

Kodaflux is an agentic AI application that takes a GitHub repository URL and autonomously generates a complete, unified documentation website for every dependency in that project. Drop in a repo link, and within minutes you have a fully navigable Docsify site hosted and live with consistent, readable quick-start guides for your entire dependency tree (Quick starts only for prototyping). No manual configuration. No copy-pasting. Just a URL in, a documentation site out.

# Run Kodaflux locally

> It is fitting to mention that development happened on a Linux machine. As such, this guide will provide commands and that'll surely work on any linux and Mac systems. If you are on a windows machine, you can use [WSL](https://github.com/microsoft/WSL#readme) which is garanteed to play nice with this project. You can try run this on a windows system but I don't promise a smooth run, although it probably will run.

> This guide assumes you won't be running any of the terraform scripts. Hence "locally".

## Prerequisites

Ensure you have the following tools installed on your system:

- [Nodejs](https://nodejs.org) (v20.9+)
- [PNPM](https://pnpm.io) (v10.28.0)
- [Python](https://python.org) (v3.12+)
- [UV](https://docs.astral.sh/uv) (latest stable version)
- [Docker & Docker compose](https://docker.com) (latest stable versions)
- [Terraform](https://developer.hashicorp.com/terraform) (latest stable version)
- [TFLint](https://github.com/terraform-linters/tflint) (latest stable version)
- [Git](https://git-scm.com) (latest stable version)

Additionally, you will need:

- [DigitalOcean Account](https://digitalocean.com)
- [Firecrawl Account](https://firecrawl.dev)
- [GitHub Account](https://github.com/)

## Preperation

Before running the setup script, ensure you have gathered the following credentials from their respective platforms. You will need to input these into the `.env` files generated in step 3 of the Setup.

1. DigitalOcean Credentials

	Required for AI processing (Gradient), object storage (Spaces), and managed databases.

	- Sign up at [digitalocean.com](https://digitalocean.com)
	- `DIGITALOCEAN_API_TOKEN`: Generate a Personal Access Token with read/write access in the API section of your dashboard.
	- `DIGITALOCEAN_SPACES_KEY_ID` & `DIGITALOCEAN_SPACES_SECRET_KEY`: Create a Spaces bucket. For ease moving forward with this guide, name the bucket `kodaflux-assets`. Then under Settings > API > Spaces Access Keys, create a key pair to programatically access the bucket (read/write). These are used for storing the generated Markdown documentation.
	- `DIGITALOCEAN_INFERENCE_KEY`: Found in the GenAI Platform (Gradient) dashboard. This powers the agentic rewriting of the docs.

2. Firecrawl API

	Required for the initial "crawl" of external documentation sites.

	- `FIRECRAWL_API_KEY`: Sign up at [firecrawl.dev](https://firecrawl.dev) and generate a key from your account settings.

3. GitHub

	Used for to increase the Github rate limits to 5000/hour.

	- `GITHUB_TOKEN`:
			Create a personal access token on github with read permission for repos.

## Setup

1. Clone the repository

	```bash
	git clone https://github.com/koda-flux/kodaflux.git
	```

	```bash
	cd kodaflux/
	```

2. Install project dependencies

	```bash
	pnpm install
	```

	```bash
	uv sync
	```

3. Prepare environment variable files

	```bash
	uv run scripts/setup_env_files.py
	```

	> The [setup_env_files.py](./scripts/setup_env_files.py) script walks the the whole repository's file structure, ignoring all files and folders included in the `.gitignore`. It finds all files named `.env.example` and creates a copies of these files to `.env`.

4. Populate all credentials in each of the newly created `.env` files. You will find `.env` in these packages:

	| Package | Required credentials |
	|---------|--------------------|
	| [agent](./packages/agent/.env) | `DIGITALOCEAN_API_TOKEN`, `DIGITALOCEAN_INFERENCE_KEY`, `DIGITALOCEAN_SPACES_KEY_ID`, `DIGITALOCEAN_SPACES_SECRET_KEY`, `GITHUB_TOKEN`, `FIRECRAWL_API_KEY` |
	| [backend](./packages/backend/.env) | `DIGITALOCEAN_API_TOKEN` |
	| [frontend](./packages/frontend/.env) | _A default value is set in the `.env.example` |

5. Build the frontend

	```bash
	pnpm run build --filter=frontend
   ```

6. Run the required external services

	```bash
	docker compose -f compose.dev.yml up -d
	```

	> The [compose.dev.yml](./compose.dev.yml) file defines all external services required to run the application locally.

7. Start all servers

	```bash
	pnpm run start
	```

# License

This project uses the `AGPL-3.0-only` open source license. Refer to the [LICENSE](./LICENSE) file to view the license.

---

<div align='center'>
	<small>
		Built by <a href='https://lebophoshoko.dedyn.io'>Lebogang Phoshoko ⚒</a>
	</small>
</div>
