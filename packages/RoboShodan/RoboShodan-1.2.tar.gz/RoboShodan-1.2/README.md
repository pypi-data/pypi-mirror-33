## RoboShodan

Robot Framework Library for Shodan

**Supports Python 2.7.x for now**

### Install Instructions

* You need Shodan API Key to run this program.
* Install the RoboShodan Library with `pip install RoboShodan`
* Create a `.robot` file that includes the keywords used by RoboShodan Library


### Importing

Arguments:  [shodan api key]

Shodan Library can be imported with one argument

Arguments:
    - ``shodan_api_key``: Shodan API Key is required to initialize a Shodan Scan on Target IP.

Examples:

`| Library `|` RoboShodan  | shodan_api_key | `


### Keywords

`run shodan scan`

`| run shodan scan  | results path  | target `

* results path: where your results will be stored. A `.json` file is generated as an output.
* target : IP of the Target.
