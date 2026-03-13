<div align='center'>

<img src='./assets/kodaflux-logo.png' />

A simple AI powered documentation aggregator.

</div>

> :warning: This project is currently under active development and will experience breaking changes often.
>
> You can have a look what what is being worked on & the general plan in the [GitHub Project](https://github.com/orgs/koda-flux/projects/1)

# Development Setup

## Prerequisites

- [Nodejs](https://nodejs.org) (v20.9+)
- [PNPM](https://pnpm.io) (v10.28.0)
- [Python](https://python.org) (v3.12+)
- [UV](https://docs.astral.sh/uv) (latest stable version)
- [Docker & Docker compose](https://docker.com) (latest stable versions)
- [Terraform](https://developer.hashicorp.com/terraform) (latest stable version)
- [TFLint](https://github.com/terraform-linters/tflint) (latest stable version)

## Running the project

1. Clone the repo

	```bash
	git clone https://github.com/koda-flux/kodaflux.git

	cd kodaflux
	```

2. Install dependencies

	```bash
	pnpm install
	```

	```bash
	uv sync
 	```

3. Create copies of all `.env` files and populate values as necessary.

   >    Each of the packages located in the [packages/](./packages) directory have `.env.example` template files in their
   >    respective roots. Create copies of these files to `.env` and populate the values as necessary

   For convenience, you can run the [`setup_env_files.py`](./scripts/setup_env_files.py) script

   ```bash
    uv run ./scripts/setup_env_files.py
    ```

4. Start the external services

	```bash
	docker compose -f compose.dev.yml up -d
	```

	```bash
	pnpm turbo db:migrate
	```

5. Run the dev servers

	```bash
	pnpm run dev
	```

	This will run all available packages:
	- [frontend](./packages/frontend) - Nextjs
	- [backend](./packages/backend) - FastAPI
	- [agent](./packages/agent) - Gradient ADK

# License

Refer to the [LICENSE](./LICENSE) file to view the license applied to this project.

---

<div align='center'>
	<small>
		Build by <a href='https://lebophoshoko.dedyn.io'>Lebogang Phoshoko ⚒
	<small>
</div>
