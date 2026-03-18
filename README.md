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
	python3 scripts/setup_env_files.py
	```

	> The [setup_env_files.py](./scripts/setup_env_files.py) script walks the the whole repository's file structure, ignoring all files and folders included in the `.gitignore`. It finds all files named `.env.example` and creates a copies of these files to `.env`.

4. Populate all variables in each of the newly created `.env` files. You will find `.env` in these packages:

	- [agent](./packages/agent/.env)
	- [backend](./packages/backend/.env)
	- [frontend](./packages/frontend/.env)

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
