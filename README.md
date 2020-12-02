# Feedbin Stars to Email

Email starred items from Feedbin to a chosen email address — like your OmniFocus or Things inbox — and unstar/archive them in Feedbin.

## Requirements

- Python 3 + [virtualenv](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv)
- A [Feedbin](https://feedbin.com) account
- A [Mailgun](https://www.mailgun.com) account
- Copy `.env.sample` to `.env` and fill out your credentials

I know this works on macOS and Ubuntu; it should work pretty much anywhere Python 3 runs.

## Installation

- Clone the repo
- Run `make bootstrap` to create a virtualenv for the project & install dependencies

### Crontab Example

This is how I’m running this tool on my personal server:

```
# Feedbin Stars to Things
*/10  *   *   *   *   /home/cdzombak/scripts/feedbin-stars/venv/bin/python3 /home/cdzombak/scripts/feedbin-stars/feedbin_stars.py --from "Feedbin <feedbin@notices.cdzombak.net>" --to "add-to-things-xxx@things.email" --dry-run false >/dev/null
```

### Cleanup

`make clean` will remove the virtualenv and cleanup any temporary artifacts (currently, there are none of those).

## Usage

- Activate the virtualenv: `. venv/bin/activate`
- Run the script: `python feedbin_stars.py [flags]`

At least some flags are needed to make the script do anything useful. Credential configuration is documented in “Configuration,” below.

### Flags

All flags are optional (though if you omit `--dry-run`, no changes will ever be made in your Feedbin account).

#### `--dry-run`

**Boolean. Default: True.**

Dry-run specifies whether the script should actually change anything in your Feedbin account. By default, this is `true`, meaning no changes will be made. (In dry-run mode, emails will still be sent, since this doesn’t put any data at risk.)

Once you’re confident in your configuration, activate the script with `--dry-fun false`.

#### `--from`

**String. Required.**

The email address to send from.

#### `--to`

**String. Required.**

The email address to send to.

## Configuration

### Credentials

Feedbin credentials are supplied via the environment variables `FEEDBIN_USERNAME` and `FEEDBIN_PASSWORD`.

Mailgun requires three environment variables:
- `MAILGUN_API`: the Mailgun API domain to use. This is `api.mailgun.net` unless you’re sending from Mailgun’s EU infrastructure; in that case use `api.eu.mailgun.net`.
- `MAILGUN_DOMAIN`: your Mailgun domain (the domain part of your `--from` emal address)
- `MAILGUN_API_KEY`: your [Mailgun API key](https://app.mailgun.com/app/account/security/api_keys)

Optionally, these can be stored in a `.env` file alongside the `feedbin_stars` script. The script will automatically read environment variables from that file. (See `.env.sample` for an example.)

## See Also

[Feedbin Auto Archiver](https://github.com/cdzombak/feedbin-auto-archiver)

## License

[MIT License](https://choosealicense.com/licenses/mit/#).

## Author

Chris Dzombak @ [dzombak.com](https://www.dzombak.com)
