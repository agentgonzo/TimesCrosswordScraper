# TimesCrosswordScraper
A Scraper for the Crosswords from The Times Crossword Club. It will download crosswords of the specified type in the input data range. It also has the option (TBD) to print out the crosswords automatically if you are running on a linux system with a printer enabled (it uses `lp`)

A subscription is required to access The Times crosswords (obviously, because nothing comes for free... even if you voted for Brexit)

I'd like to make this easily deployable/integratable with a web server for easy printing, but for the moment, it's CLI only.

## Usage
Run `python crossoword.py`.

On first login, you will be propmted for some login information (cookies - see below).
You must specify a date range and crossword type.

### Command line arguments
* `-s <date>` Start date - get crosswords from this date. Date input in DD/MM/YYYY format
* `-e <date>` End date - get crosswords until this date. Date input in DD/MM/YYYY format
* `-t <type>` Crossword type - see below for the list of types
* `-p` (Optional) Print out the crosswords after downloading

### Crossword Types
* `6`: Sunday Times Concise
* `5`: Times Concise
* `7`: Times Concise Jumbo
* `1`: Quick Cryptic
* `3`: Sunday Times Cryptic
* `2`: Times Cryptic
* `4`: Times Cryptic Jumbo
* `9`: General Knowledge Jumbo
* `8`: Mephisto
* `12`: Monthly Club Special
* `10`: O Tempora! (Latin)
* `11`: The Listener
* `SPECIALIST`: Specialist
* `CRYPTIC`: Cryptic

## Login/Authentication
The login mechanism is awkward to simulate, so for the time being, you will have to log in via your web browser, and then copy two cookies into the application.
These cookies are:
* `acs_tnl`
* `sacs_tnl`

The login mechanism involves not only a standard `POST` with the username and password, but also a `GET` with a signed JWT. I haven't traced how to get the login working with just the username and password yet, so but if you can figure it out, then please contact me or submit a PR. Fortunately, the two cookies are long-lived (in the order of months) so once you have set them you don't need to reset them that often.

