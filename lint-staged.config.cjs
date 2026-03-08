module.exports = {
	"*.{js,cjs,mjs,ts,cts,mts,tsx,json,css}": "biome check --fix",
	"*.py": ["ruff check --fix", "ruff format"],

	"infrastructure/**/*.tf": [
		(filenames) => filenames.map(file => `tflint --filter=${file}`),
		"terraform fmt"
	]
};
