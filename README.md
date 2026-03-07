<div align='center'>

<img src='./assets/kodaflux-logo.png' />

A simple AI powered documentation aggregator.

</div>

> :warning: This project is currently under active development and will experience breaking changes often.
>
> You can have a look what what is being worked on & the general plan in the [GitHub Project](https://github.com/orgs/koda-flux/projects/1)

# Development Setup

## Prerequisites

- Nodejs (v20.9+)
- PNPM (v10.28.0)
- Python (v3.12+)
- UV (latest stable version)
- Docker & Docker compose (latest stable versions)

## Running the project

1. Clone the repo

	```bash
	git clone https://gitlab.com/kodaflux/kodaflux.git

	cd kodaflux
	```

2. Install dependencies

	```bash
	pnpm install
	```

	> :light_bulb: This will also run `uv sync` in the root of the backend which is written in Python (FastAPI)


3. Create copies of all `.env` files and populate values as necessary.

4. Start the external services

	```bash
	docker compose -f compose.dev.yml up -d
	```



	```bash
	pnpm turbo db:migrate
	```

6. Run dev servers

	```bash
	pnpm run dev
	```

# License

Refer to the [LICENSE](./LICENSE) file to view the license applied to this project.

---

<div align='center'>
	<small>
		Build by <a href='https://lebophoshoko.dedyn.io'>Lebogang Phoshoko ⚒
	<small>
</div>
