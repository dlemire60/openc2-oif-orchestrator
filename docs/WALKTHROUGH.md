# O.I.F. (OpenC2 Integration Framework) Orchestrator Walk Through

This document provides a detailed walkthrough of the
installation, configuration, and basic operations of the OIF
Orchestrator. The Orchestrator implements the OpenC2
[Producer](https://docs.oasis-open.org/openc2/oc2ls/v1.0/cs02/oc2ls-v1.0-cs02.html#16-overview)
function. The following diagram provides a high-level
overview of the OIF Orchestrator's construction:

![OIF Orchestrator Block Diagram](images/orch-block-diagram.png)

## System Preparation

Developers need the following tools to start working with
OIF:
 - Required:  [Python](https://www.python.org/),
   [pip](https://pip.pypa.io/en/stable/),
   [Docker](https://www.docker.com/), [Docker
Compose](https://docs.docker.com/compose/)
 - Optional: [git](https://git-scm.com/)

The OIF Orchestrator requires
[Python](https://www.python.org/) and
[Docker](https://www.docker.com/) to operate. Developers
should insure both of the following are installed on their
system:

- Docker, version 18 or higher
- Python, version 3.6 or higher

OIF Orchestrator also requires [Docker
Compose](https://docs.docker.com/compose/), and
[pip](https://pip.pypa.io/en/stable/) for configuration and
setup.  Docker Compose is [installed with
Docker](https://docs.docker.com/compose/install/) on Windows
and Mac systems, but must be installed separately on Linux
systems. Pip is usually [installed with
Python](https://pip.pypa.io/en/stable/installing/).
Developers are advised to update all of the software
components to the latest versions.

If working in a Linux environment, developers should also
perform Docker's [post-installation steps for
Linux](https://docs.docker.com/engine/install/linux-postinstall/),
specifically:

 * Manage Docker as a non-root user, and
 * Configure Docker to start on boot

Developers may optionally install [git](https://git-scm.com/)
version control software, as a means of obtaining the OIF
Orchestrator software.

## Obtain OIF Orchestrator Software

Developers must acquire a local copy of the OIF Orchestrator
software. There are two approaches for this:
 1. Clone the [OIF
    Orchestrator](https://github.com/oasis-open/openc2-oif-orchestrator)
    repository in the desired location:<br>
    `git clone
    https://github.com/oasis-open/openc2-oif-orchestrator.git`
 1. Download an ZIP archive by 
    1. Navigating to the
       [repository](https://github.com/oasis-open/openc2-oif-orchestrator).
	1. Click on the green **Clone** button.
	1. Select **Download ZIP**.
	1. Unwrap the ZIP archive in the desired location.

## Configure OIF Orchestrator Software

To configure the OIF Orchestrator, navigate to the directory
containing the local software copy and Run `configure.py`
with the desired options prior to starting the Orchestrator
for the first time. The available options are:
 - `-b` or `--build-image` -- Build base containers
 - `-d` or `--dev` -- Build using the development python image
 - `-f FILE` or `--log_file FILE` -- Enables logging to the designated file
 - `-h` or `--help` -- Shows the help and exits
 - `-v` or `--verbose` -- Enables verbose output    	

The configuration command is
```bash 
python configure.py [OPTIONS]
```

> **QUESTION**: is there a recommend default for the
> configuration command? 

> **QUESTION**: Is it common to need to run
> `configure.py` more than once (seems to have happened in
> our testing)?

## Container/Services ReadMe

The ReadMe files for OIF Orchestrator components are linked
here:

|Orchestrator   | Transport  | Logger  |
|:-:|:-:|:-:|
| [Core](../orchestrator/core/ReadMe.md)  | [HTTPS](../orchestrator/transport/https/README.md)  | [GUI](../logger/gui/ReadMe.md)  |
| [GUI](../orchestrator/gui/client/ReadMe.md)  | [MQTT](../orchestrator/transport/mqtt/ReadMe.md)  | [Server](../logger/server/ReadMe.md)  |





## Running OIF Orchestrator (Docker Compose)

As described in [its
documentation](https://docs.docker.com/compose/), Docker
Compose is use to "define and run multi-container Docker
applications". To start OIF Orchestrator in its default
configuration, the only required command is:

```bash
	docker-compose -f orchestrator-compose.yaml up
```

This command will:
 - Create the necessary Docker images as defined in the
   `orchestrator-compose.yml` configuration file
 - Execute the application in the defined containers,
   attached to the terminal from which it was launched  

Execution of an attached OIF instance is terminated by
typing `ctrl-C` in the terminal.

The Orchestrator can also be started in detached mode using
the docker-compose `-d` or `--detach` option:

```bash
	docker-compose up --detach
```

A detached instance of OIF is terminated with the complementary command:

```bash
	docker-compose down
```
> **--------------------------------------------------------------------**

> **Note from Dave:** IMO for this walkthrough, which by
> definition supposed to be basic, we should remove the
> material from the line above to the one further down about
> Docker options and image building. I think those things go
> beyond "basic walkthrough". I've left it untouched for now
> and am jumping ahead to describe first time operation of
> the Orchestrator.

### Docker Options
- Options
	- `-f FILE` or `--file FILE` -- Specify an alternate compose file (default: docker-compose.yml)
	- `-p NAME` or `--project-name NAME` -- Specify an alternate project name (default: directory name)
	- `d` or `--detach` -- Detached mode: Run containers in the background, print new container names. Incompatible with --abort-on-container-exit.
- Starting
	- Run the `docker-compose` command for the Orchestrator as shown below

-  Stopping
	-  If running attached (showing log output, no -d option)
		-  Use 'Ctrl + C' 
	-  If running detached (not showing log output, -d option)
		-  Run the `docker-compose` that was used to start the Orchestrator **except** replace `up ...` with `down`
			
			```bash
			docker-compose ...... down
			```
- Building Images
	- Run the `docker-compose` that was used to start the Orchestrator **except** replace `up ...` with `build`
	- Options
		- SERVICE_NAME - The name of the service to rebuild the image, if not specified all will build
	- Notes
		- Does not need to be run prior to starting, the containers will autobuild if not available
		- Should be run after adding a new Protocol or Serialization
	
	```bash
	docker-compose ...... build [SERVICE_NAME]
	```

### Docker Compose Files
### Central Logging
- __Still in Beta__
- Run the `docker-compose` as normal with the additional option of a second '-f/--file'
- Allows for a central location for logging rather than the docker default of per container
- Runs on default port of 8081 for logger web GUI

	```bash
	docker-compose -f orchestrator-compose.yaml -f orchestrator-compose.log.yaml ...
	```

#### Orchestrator
- Use [`docker-compose`](https://docs.docker.com/compose/reference/overview/) to start the orchestrator on the system

	```bash
	docker-compose -f orchestrator-compose.yaml [-p NAME] up [-d]
    ```

> **--------------------------------------------------------------------**

## Accessing the Orchestrator GUI

The OIF Orchestrator provides graphical user interfaces
(GUIs) for both the user (i.e., for managing devices and
actuators, and creating and sending OpenC2 commands and
receiving responses) and for administration (i.e., ... [**`need
developer input here`**]). The GUIs are accessed as follows:
 - User GUI -- `http://localhost:8080`
 - Admin GUI -- `http://localhost:8081`

Browsing to the User GUI location brings up the login
screen:

![OIF Orchestrator User Login](images/oif-orch-login.png)

> **NOTE:** Need to polish text based on the following Q&A: 

> **QUESTION:** what's the different between "Admin" and
> "logger", if any?

- "Admin" is the Django built-in admin (more granular control of database tables) and preferences (Orch ID, Orch Name, Orch IP, CommandWait)
 - "Logger" is the central logger for the containers (if
   enabled)

> **QUESTION:** what should this walkthrough say about the
> Admin / Logger UI?

- Admin - Granular control of existing database tables if errors/need arises for use, global preference updating
- Logger - Central location for logs if enabled

For both GUIs, the login credentials are 
 - Username: `admin`
 - Password: `password`

After login to the User GUI you will seen the home screen
with the system menu

![OIF Orchestrator Home Screen](images/oif-orch-home-screen.png)

## Create Devices and  Actuators

An OIF Device is an entity that groups one or more OpenC2
actuators and provides a communications interface so that
the Orchestrator can issue commands and receive responses.
Note that the Device isn't explicitly mentioned in the
[OpenC2
specifications](https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=openc2#technical),
it's an OIF construct. Devices and their associated
actuators have to be registered in the OIF Orchestrator before
interactions with them are possible. In addition, actuators
must have an associated JSON schema to inform the
Orchestrator of the action/target pairs the actuator can
process.

Devices and actuators have associated identifiers. Within
OIF these are required to be v4 UUIDs; this is an OIF
requirement rather than an OpenC2 requirement. While the UI
will permit the user to enter a non-UUID value as an
identifier, an error will occur when attempting to exchange
commands and responses.

### Registering a Device with the OIF

The procedure to create a new device is:

1. Select `Devices` from the Orchestrator menu; this brings
  the list of registered devices.
1. Click the `REGISTER` button at the right; this opens the
   dialog to register a new device.
1. Give the device a name (user's discretion).
1. Click the `GEN ID` button to generate a Device ID (Note: while
   the field permits user entry of an arbitrary ID, the
   Orchestrator expects a UUID value here).
1. Enter the Device's IP address and Port.
   - Default port for HTTPS Transfer is 5001
   - Default port for MQTT Transfer is 1883
1. Select the transfer protocol to use with this device.
1. Select the message serialization to use with this device.
   JSON is the default serialization for OpenC2.
1. Enter any desired information in the `Note` field. This
   is typically used to provide a human-friendly description
   of the device's type.
1. Click the `REGISTER` button at bottom right to complete
   the device registration.

The screenshots below show the registered devices list and device
editing dialog:

![Orchestrator Registered Devices List](images/oif-orch-dev-reg-screen.png)


![Orchestrator Device Editing Dialog](images/oif-orch-edit-device.png)


Device registration notes:

- Registered devices have an `EDIT` button that re-opens the
  registration dialog for updating
- The blue `+`  button in the registration dialog permits
  defining additional transport interfaces for a device.



### Registering an Actuator with the OIF
- Give actuator a name and generate a UUID for it.
- Select a parent device.
    -  Note: device should be registered before the
       actuator.
> **NOTE:**  link below is broken; need useful link
- Upload/Copy-Paste schema. Schema for the default included ISR actuator can be found at [device/actuator/isr/act_server/schema.json](../device/actuator/isr/act_server/schema.json).
> **NOTE:**  "ISR actuator" link below is broken; need useful link
- This information can also be found under the [ISR Actuator](../device/actuator/isr/ReadMe.md) page.
- If you are registering a new actuator for the first time
  while utilizing the MQTT transport you may need to update
  the `MQTT_TOPICS` environment variable. Read the MQTT
  Topics section [here](transport/mqtt/ReadMe.md)

## Generating Commands and Viewing Responses