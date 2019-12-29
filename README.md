# Shapes

## Configuration

Set up a virtual environment with `make venv` and enter it with `source venv/bin/activate`.

Export the following environment variables for authenticating to the Twitter API:
* `API_KEY`,
* `API_SECRET`,
* `ACCESS_TOKEN`,
* `ACCESS_TOKEN_SECRET`.

(See [https://github.com/fionn/twitterauthenticator](twitterauthenticator) for how to generate access tokens.)

You must also export `SEARCH_PATH`. This will prefix the file names given in the data.

## Usage

It takes a single mandatory positional argument which must be a comma-delimited file with the format matching [`example/example.csv`](example/example.csv).
The entries in the `filename` column must be real files that exist under `SEARCH_PATH`.

See `./src/shapes.py --help` for details.

## Deployment

### Systemd

Add the above environment variables to `.env` in the repository root, without an `export` directive.
Add the data to `data.csv` in the repository root.
Then symlink or copy the unit files in [`system_units/`](system_units/) to `/etc/systemd/system/` and enable the timer.
