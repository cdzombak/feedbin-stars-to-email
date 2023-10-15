# Feedbin Stars to Email

Email starred items from Feedbin to a chosen email address — like your OmniFocus or Things inbox — and unstar/archive them in Feedbin.

## Installation (Docker)

Pre-built Docker images are available. [See Docker Hub for details](https://hub.docker.com/r/cdzombak/feedbin-stars-to-things).

No installation is required to use these images under Docker.

## Installation (local Python)

1. Clone the repo and change into the `feedbin-stars-to-things` directory
2. Run `make virtualenv` to create a virtualenv for the project & install dependencies

## Configuration

### Credentials

Feedbin credentials are supplied via the environment variables `FEEDBIN_USERNAME` and `FEEDBIN_PASSWORD`.

Mailgun requires three environment variables:
- `MAILGUN_API`: the Mailgun API domain to use. This is `api.mailgun.net` unless you’re sending from Mailgun’s EU infrastructure; in that case use `api.eu.mailgun.net`.
- `MAILGUN_DOMAIN`: your Mailgun domain (the domain part of your `--from` email address)
- `MAILGUN_API_KEY`: your [Mailgun API key](https://app.mailgun.com/app/account/security/api_keys)

#### Docker Configuration

Credentials may be placed in a `.env` file and given to the `docker run` command like:

```shell
docker run --rm --env-file /path/to/.env cdzombak/feedbin-stars-to-things:1 [OPTIONS]
```

(See `.env.sample` for a sample file.)

Alternatively, credentials may be passed directly to the `docker run` command like:

```shell
docker run --rm \
    -e FEEDBIN_USERNAME=myusername \
    -e FEEDBIN_PASSWORD=mypassword \
    -e MAILGUN_API=api.mailgun.net \
    -e MAILGUN_DOMAIN=notices.example.com \
    -e MAILGUN_API_KEY=my_secret_mailgun_key \
    cdzombak/feedbin-stars-to-things:1 [OPTIONS]
```

#### Local Python Configuration

Your credentials can optionally be stored in a `.env` file alongside the `feedbin_stars.py` script. The script will automatically read environment variables from that file. (See `.env.sample` for an example.)

## Usage

### Docker Usage

Invoke the script with `docker run`:

```shell
docker run --rm --env-file /path/to/.env cdzombak/feedbin-stars-to-things:1 [--dry-run false] --from feedbin@notices.example.com --to me@example.com
```

### Local Python Usage

1. Activate the virtualenv: `. venv/bin/activate`
2. Run the script: `python feedbin_stars.py [OPTIONS]`

Alternatively, invoke the virtualenv's Python interpreter directly:

```shell
venv/bin/python3 feedbin_stars.py [--dry-run false] --from feedbin@notices.example.com --to me@example.com
```

### Flags

#### `--dry-run`

**Boolean. Default: True.**

Dry-run specifies whether the script should actually change anything in your Feedbin account. By default, this is `true`, meaning no changes will be made. (In dry-run mode, emails will still be sent, since this doesn't put any data at risk.)

Once you’re confident in your configuration, activate the script with `--dry-fun false`.

#### `--from`

**String. Required.**

The email address to send from.

#### `--to`

**String. Required.**

The email address to send to.

### Crontab Example

This is how I’m running this tool on my home server:

```text
# Feedbin Stars to Things
# Runs every 10 minutes
*/10  *   *   *   *   docker run --rm --env-file $HOME/.config/feedbin/env cdzombak/feedbin-stars-to-things:1 --from "Feedbin <feedbin@notices.cdzombak.net>" --to "add-to-things-xxx@things.email" --dry-run false
```

## See Also

[Feedbin Auto Archiver](https://github.com/cdzombak/feedbin-auto-archiver)

## License

[MIT License](https://choosealicense.com/licenses/mit/#).

## Author

Chris Dzombak @ [dzombak.com](https://www.dzombak.com)
