# Automated purchase of ZSSK (slovakrail) free ticket(s)

Python script for automated **free** ticket buying at [ikvc.slovakrail.sk/esales/search](https://ikvc.slovakrail.sk/esales/search).

Script will click on buttons and fill up the input boxes for you with the predefined data in `person.txt` file.

The only thing what you are required to do is to launch the script with **exact** stations (departure and arrival station), date and time for your train.

## Requirements

* [python](https://www.python.org/downloads/) >= 3.6.7
* [geckodriver](https://github.com/mozilla/geckodriver/releases/latest) >= 0.24.0
* [firefox](https://www.mozilla.org/en-US/firefox/all/) >= 65.0.1
* pip packages:
  * flake8 >= 2.5.4
  * mccabe >= 0.4.0
  * pep8 >= 1.7.0
  * pyflakes >= 1.0.0
  * selenium >= 2.53.2
  * unidecode >= 0.4.19

## Installation

### Ubuntu/Debian

#### Ubuntu 16.04.6

1. Set your account credentials in `person.txt`.

2. Initialize the environment via these commands:

```sh
# 1) python3.6 + pip3
sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt-get update
sudo apt-get install python3.6 python3-pip

# 2) geckodriver
wget --verbose https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
tar --extract --verbose --gzip --file geckodriver-v0.24.0-linux64.tar.gz
chmod +x --verbose geckodriver
sudo mv --verbose geckodriver /usr/local/bin
rm --verbose --force geckodriver-v0.24.0-linux64.tar.gz

# 3) repository
git clone https://github.com/europ/zssk-ticket-automation.git
cd zssk-ticket-automation

# 4) requirements
python3.6 -m pip install -r requirements.txt

# 5) help test
python3.6 buy.py --help
```

3. See [*Usage*](https://github.com/europ/zssk-ticket-automation#usage) section.

## Usage

Set up your account credentials in `person.txt` and launch the script with the correct options (see [*Options*](https://github.com/europ/zssk-ticket-automation#options) section).

### Options

Order of the options does not matter. Option values **must exactly match the train details** (time, date and stations).

#### Mandatory

* Departure station `-D "Foo"` or `--departure "Foo"`
* Arrival station `-A "Bar"` or `--arrival "Bar"`
* Departure time `-t "HH:MM"` or `--time "HH:MM"`
* Departure date `-d "DD.MM.YYYY"` or `--date "DD.MM.YYYY"`

#### Optional

* Headless browser mode `-H` or `--headless`
  * web browser without a graphical user interface

### Examples

* Help
	```sh
	python3.6 buy -h
  ```
  or
  ```sh
  python3.6 buy --help
	```

* Usage example
	```sh
	python3.6 buy.py -D "Bratislava hl.st." -A "Kúty" -t "05:16" -d "18.03.2019"
  ```
  or
  ```sh
  python3.6 buy.py --departure "Bratislava hl.st." --arrival "Kúty" --time "05:16" --date "18.03.2019"
	```

* Headless example
  ```sh
  python3.6 buy.py -D "Bratislava hl.st." -A "Kúty" -t "05:16" -d "18.03.2019" -H
  ```
  or
  ```sh
  python3.6 buy.py --departure "Bratislava hl.st." --arrival "Kúty" --time "05:16" --date "18.03.2019" --headless
  ```

#### Log

![log-example](https://github.com/europ/zssk-ticket-automation/blob/master/example.png "Log Example")


## Help

If you have purchased a wrong ticket you are able to cancel it [here](https://ikvc.slovakrail.sk/esales/refund).

In case of any problem, please feel free to open an [issue](https://help.github.com/articles/creating-an-issue/) and specify the problem with **detailed** description.

## Contributing

Feel free to contribute via opening a [pull request](https://help.github.com/articles/creating-a-pull-request/) or an [issue](https://help.github.com/articles/creating-an-issue/).

## License

This project is available as open source under the terms of the [MIT License](https://github.com/europ/zssk-ticket-automation/blob/master/LICENSE).
