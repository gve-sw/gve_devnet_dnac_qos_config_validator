# DNAC QoS Config Validator
This prototype assists in validating the QoS configuration of switchports that have 
access points plugged into them. First, the prototype checks the devices that are 
associated with DNA Center. From there, it checks the topology of DNA Center and finds 
which switches (and which of those interfaces) have access points connected to them. 
Next, it pulls the running configuration of the interfaces that have access points 
connected to them and checks if that configuration contains the line "auto qos trust 
dscp" if the switch is a Catalyst 9300 or 9400 series or "auto qos trust" if the 
switch is a Catalyst 4500 series or something else. Lastly, the program creates a file 
that notes which switchports have access points connected to them and need a line of 
QoS configuration.
![/IMAGES/dnac_qos_config_validator_high_level_design.png](/IMAGES/dnac_qos_config_validator_high_level_design.png)

## Contacts
* Danielle Stacy

## Solution Components
* DNA Center
* Python 3.9
* Catalyst switches

## Installation/Configuration
1. Clone this repository with `git clone https://github.com/gve-sw/gve_devnet_dnac_qos_config_validator` and open the directory.
2. Add the IP address. username, and password of your DNA Center instance to env.py. 
```python
env = {
    "base_url": "enter url of DNAC here",
    "username": "enter username of DNAC here",
    "password": "enter password of DNAC here"
}
```
3. Set up a Python virtual environment. Make sure Python 3 is installed in your environment, and if not, you may download Python [here](https://www.python.org/downloads/) Once Python 3 is installed in your environment, you can activate the virtual environment with the instructions found [here](https://docs.python.org/3/tutorial/venv.html)
4. Install the requirements with `pip3 install -r requirements.txt`

## Usage
The functions that make the API calls to DNA Center are located in dnac.py. The text file that is generated from running the code should be named {datetime}_configs.txt, where {datetime} is the date and time at which the code is run. The {datetime}_configs.txt file should contain the ID and IP address of each switch that needs a port configured, the ID of the access point that is connected to the switchport, the name of the switchport, the series of the switch, and the lines of configuration that the switchport needs.

To run the code, use the command `python3 check_configs.txt`


# Screenshots

![/IMAGES/0image.png](/IMAGES/0image.png)

Output of the program after it runs - notice it prints out the results of the show run interface command
![/IMAGES/output_screenshot.png](/IMAGES/output_screenshot.png)

Text file created by the program with the switches have access points that need configuration and what configuration they need
![/IMAGES/text_file_screenshot.png](/IMAGES/text_file_screenshot.png)
### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
