# dpos-deputy

Howdy delegate! You have just been deputized!

### Installation

Install python 3.6

```commandline
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.6-dev

wget https://bootstrap.pypa.io/get-pip.py
sudo python3.6 get-pip.py
sudo pip3.6 install virtualenv
```

If you get an error related to hidapi or gcc, try this:
```commandline
sudo apt-get install gcc
sudo apt install libudev-dev libusb-1.0-0-dev
```

Create a virtual environment (replace myvirtualenv with whatever seems appriopriate, for example deputy)

```commandline
virtualenv myvirtualenv -p python3.6
```

Activate the virtualenv.

```commandline
source myvirtualenv/bin/activate
```

```commandline
pip install dpos-deputy
```

Deputy requires running ark-node instances/other network nodes like Kapu or Persona to function.

### Initial setup

Start out by enabling autocompletion for an easier time.

```commandline
deputy enable_autocomplete
```

### Help

Use flags to figure out what the commands do.

```bash
deputy --help
```

### Starting out
Start out by setting your configurations for further use.

```commandline
deputy set_config --help
```

### Example command
Setting up your configuration:

```commandline
deputy -p mypassword set_config
```

This will lead you through a series of prompts to store persistent configurations. If you don't use a 
password, deputy will default to default_password for encryption purposes. 

