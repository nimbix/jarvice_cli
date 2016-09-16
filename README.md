The Jarvice CLI by Nimbix, Inc. This consists of two components:
  * Python API for programmatically accessing https://api.jarvice.com
  * jarviceclient, a command-line tool for calling the API

For more information and the full API documentation, see https://api.jarvice.com.

The easiest way to get set up:

Create `~/.jarvice.cfg` with the following contents:

```
[auth]
username: username
apikey: apikey-from-portal
```

# The JARVICE CLI

## Installation
The easiest way to install is directly from PyPI.

```pip install --user jarviceclient```

If the installation was successful, you should have an executable called `jarvice_cli` in your path after installing the `jarviceclient` package.

## Interacting with Jobs

### Launching a job
Launch a job from the portal and save the JSON to `job.json`. To launch it again, do the following:

```jarvice_cli submit -j job.json```

### List a summary of your jobs

```jarvice_cli summary```

### See the output/error of a currently running job

```jarvice_cli tail -number <jobnumber>```

### See the output of a job that has ended


```jarvice_cli output -number <jobnumber>```

### Get connection details (address, password)

```jarvice_cli connect -number <jobnumber>```

### Cleanly shutdown a job (with shutdown signal)

```jarvice_cli shutdown -number <jobnumber>```

### Force termination of a job (like kill -9)


```jarvice_cli terminate -number <jobnumber>```

### Get the stats on your job

```jarvice_cli info -number <jobnumber>```

### Get the status of your job

```jarvice_cli status -number <jobnumber>```

### Perform a configured action on your job

```jarvice_cli action -number <jobnumber> -action <action>```

### Get a list of currently running jobs

```jarvice_cli jobs```

### Cleanly shutdown all currently running jobs

```jarvice_cli shutdown_all```

### Force termination of a job (like kill -9)

```jarvice_cli terminate_all```

### Wait for a job to end

```jarvice_cli wait_for -number <jobnumber>```


## Data Management for drop.jarvice.com Storage Vault

### Upload 

```jarvice_cli download -drop <source> -local <destination>```

### Upload file or directory to drop.jarvice.com

```jarvice_cli upload -local <source> -drop <destination>```

### List files on drop.jarvice.com

```jarvice_cli ls```
or
```jarvice_cli ls -d <remote_dir>```

## Querying JARVICE Options

### See the available apps and a schema describing inputs

```jarvice_cli apps```

### Query available machine types

```jarvice_cli machines```


# JarviceAPI

JarviceAPI contains a Client and AuthenticatedClient for interacting with https://api.jarvice.com
