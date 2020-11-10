# Hong Kong District Council 2019 Bot

## About

This bot tweets satellite images of Hong Kong district council constituencies along with the outcome of the 2019 district council elections for that district.

## Configuration

Set up a virtual environment with `make venv` and enter it with `source venv/bin/activate`.

Export the following environment variables for authenticating to the Twitter API:
* `API_KEY`,
* `API_SECRET`,
* `ACCESS_TOKEN`,
* `ACCESS_TOKEN_SECRET`.

(See [twitter-authenticator](https://github.com/fionn/twitter-authenticator) for how to generate access tokens.)

You must also export `SEARCH_PATH`. This will prefix the file names given in the data.

## Usage

It takes a single mandatory positional argument which must be a comma-delimited file with the format matching [`example/example.csv`](example/example.csv).
The entries in the `filename` column must be real files that exist under `SEARCH_PATH`.

See `./src/constituencies.py --help` for details.

## Deployment

### Systemd

Add the above environment variables to `.env` in the repository root, without an `export` directive.
Add the data to `data.csv` in the repository root.
Make the virtual environment.
Then symlink or copy the unit files in [`system_units/`](system_units/) to `/etc/systemd/system/` and enable the timer.

### Actions

See [`.github/workflows/post.yml`](.github/workflows/post.yml) for the deployment configuration.
