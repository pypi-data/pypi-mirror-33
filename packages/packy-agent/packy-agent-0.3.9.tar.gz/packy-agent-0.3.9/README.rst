Development
===========

Initial installation
--------------------

#. Install prerequisites::

    sudo apt-get install python-dev build-essential pkg-config python-pip
    sudo apt-get install libssl-dev libffi-dev libsasl2-dev liblz4-dev

#. Make sure that Python 2.7.12 is installed::

    python --version

#. Install and configure git::

    sudo apt-get install git
    git config --global user.name 'Firstname Lastname'
    git config --global user.email 'youremail@youremail_domain.com'

#. Fork `<https://bitbucket.org/samnz_/packy-agent>`_ repository

#. Clone forked repository (replace <username> with your bitbicket account name)::

    git clone git@bitbucket.org:<username>/packy-agent.git
    cd packy-agent

#. Create your custom `.gitignore` (the reason for not storing `.gitignore` itself in the repo is that
   every developer might have their own set of files to ignore, because they may use different IDEs
   and auxiliary files)::

    cat << EOF >> .gitignore
    .gitignore
    *.py[cod]
    /local/
    /packy_agent/scripts/*.retry
    # insert personal development environment entries here
    EOF

#. Install virtualenvwrapper::

    sudo pip install virtualenv
    sudo pip install setuptools
    pip install --user virtualenvwrapper
    cat << EOF >> ~/.bashrc
    export WORKON_HOME=$HOME/.virtualenvs
    source ~/.local/bin/virtualenvwrapper.sh
    EOF

    export WORKON_HOME=$HOME/.virtualenvs
    source ~/.local/bin/virtualenvwrapper.sh

#. Create virtualenv::

    mkvirtualenv packy-agent

#. Install Python prerequisites::

    pip install setuptools==36.0.1
    pip install pip==10.0.1

#. Install Packy Agent in development mode::::

    cd packy-agent  # this repo root
    pip install -e .

#. Create Control Server local configuration file::

    cat << EOF > ./local/packy-control-server.yaml
    packy:
      control_server:
        supervisor_configuration_file: $PWD/local/etc/packy-supervisord.conf
        uwsgi_configuration_file: $PWD/local/etc/packy-uwsgi.conf
        supervisor_log_file: $PWD/local/var/log/packy/supervisor/supervisor.log
        supervisor_run_directory: $PWD/local/var/run/packy/supervisor
        uwsgi_pid_file: $PWD/local/var/run/packy/uwsgi/pid
        control_server_stdout_log_file: $PWD/local/var/log/packy/control-server/standard.log
        control_server_stderr_log_file: $PWD/local/var/log/packy/control-server/error.log
        agent_stdout_log_file: $PWD/local/var/log/packy/agent/standard.log
        agent_stderr_log_file: $PWD/local/var/log/packy/agent/error.log
        watchdog_stdout_log_file: $PWD/local/var/log/packy/watchdog/standard.log
        watchdog_stderr_log_file: $PWD/local/var/log/packy/watchdog/error.log
        server_base_url: http://127.0.0.1:8000/
        enable_reboot: false
        enable_upgrade: false
        enable_network_configuration: false
    EOF

#. Continue with `Upgrade` section

#. Continue with `Run` section

#. Create new user in Packy Server::

    http://127.0.0.1:8000/accounts/signup/

#. Activate agent::

    http://127.0.0.1:8001/

Upgrade
-------

#. Change to this repo root directory::

    cd packy-agent

#. Activate virtualenv::

    workon packy-agent

#. Upgrade Packy Agent in development mode::::

    pip install -e .[post,dev]

#. Create directories::

    export PACKY_CONTROL_SERVER_CONFIG=$PWD/local/packy-control-server.yaml
    ANSIBLE_NOCOWS=1 ansible-playbook -i localhost, -c local --become-user=root packy_agent/scripts/deploy_devenv.yaml

Run
---

#. Run Packy Agent::

    cd packy-agent
    workon packy-agent
    export PACKY_AGENT_CONFIG=$PWD/local/packy-agent.yaml
    # TODO(dmu) MEDIUM: This is only required to read supervisor config file path
    export PACKY_CONTROL_SERVER_CONFIG=$PWD/local/packy-control-server.yaml
    export VENV_CELERY=`which celery`
    sudo -E $VENV_CELERY worker -A packy_agent.celery_app.app --loglevel=debug

#. Run Control Server::

    cd packy-agent
    workon packy-agent
    export PACKY_AGENT_DEBUG=1
    export PACKY_AGENT_CONFIG=$PWD/local/packy-agent.yaml
    export PACKY_CONTROL_SERVER_CONFIG=$PWD/local/packy-control-server.yaml
    export VENV_PYTHON=`which python`
    sudo -E $VENV_PYTHON -m packy_agent.control_server.run --debug
    # or
    export VENV_CONTROL_SERVER=`which control-server`
    sudo -E $VENV_CONTROL_SERVER --debug

#. Run Watchdog::

    cd packy-agent
    workon packy-agent
    export PACKY_AGENT_CONFIG=$PWD/local/packy-agent.yaml
    # TODO(dmu) MEDIUM: This is only required to read supervisor config file path
    export PACKY_CONTROL_SERVER_CONFIG=$PWD/local/packy-control-server.yaml
    export VENV_PYTHON=`which python`
    sudo -E $VENV_PYTHON -m packy_agent.watchdog.run
    # or
    export VENV_WATCHDOG=`which watchdog`
    sudo -E $VENV_WATCHDOG

#. Alternatively to running Packy Agent, Control server and Watchdog separately run them with Supervisor::

    cd packy-agent
    workon packy-agent
    export PACKY_AGENT_DEBUG=1
    export PACKY_AGENT_CONFIG=$PWD/local/packy-agent.yaml
    export PACKY_CONTROL_SERVER_CONFIG=$PWD/local/packy-control-server.yaml
    export VENV_SUPERVISORD=`which supervisord`
    sudo -E $VENV_SUPERVISORD --nodaemon --configuration ./local/etc/packy-supervisord.conf

#. Run to agent deployment testing::

    ANSIBLE_NOCOWS=1 ansible-playbook -i x.x.x.x, --become-user=root -e '{"packy_agent_version": "0.3.2", "packy_server_base_url": "http://192.168.1.231:8000"}' packy_agent/scripts/install.yaml


Run tests
---------

#. Run manual tests::

    behave manual_tests/

Production
==========

Build
-----

Python Source distribution package
++++++++++++++++++++++++++++++++++

#. Install virtualenvwrapper::

    pip install virtualenv
    pip install --user virtualenvwrapper
    cat << EOF >> ~/.bashrc
    export WORKON_HOME=$HOME/.virtualenvs
    source ~/.local/bin/virtualenvwrapper.sh
    EOF

    export WORKON_HOME=$HOME/.virtualenvs
    source ~/.local/bin/virtualenvwrapper.sh

#. Create virtualenv::

    mkvirtualenv packy-agent
    # or later:
    workon packy-agent

#. Install Python prerequisites::

    pip install setuptools==36.0.1
    pip install pip==10.0.1

#. Build Python Source Distribution::

    python setup.py sdist

#. Publish to public PyPI::

    pip install twine
    # Configure `pypipacky` in your `~/.pypirc`
    twine upload -r pypipacky ./dist/packy-agent-<x.y.z>.tar.gz

#. [optional] Publish to private PyPI (after merging to upstream/master)::

    git remote add fury https://dmugtasimov1@git.fury.io/dmugtasimov1/packy-agent.git
    git fetch upstream
    git push fury upstream/master:master

Docker image
++++++++++++

#. Build Python Source Distribution as described in `Python Source distribution package`_

#. Build Docker image::

    # Replace <version> with the version number built in previous step
    # (!!!) <packy_server_base_url> MUST be available from inside of Docker container
    export PACKY_AGENT_VERSION=<version>
    export PACKY_SERVER_BASE_URL=https://p05.packy.io

    mkdir ./tmp

    export PACKY_AGENT_PACKAGE_NAME=packy-agent
    wget "https://p05.packy.io/downloads/install-packy-agent.sh?os=alpine&version=$PACKY_AGENT_VERSION" -O ./tmp/install-packy-agent.sh
    # or (to install package from local disk, not PyPI)
    export PACKY_AGENT_PACKAGE_NAME=/root/packy-agent-$PACKY_AGENT_VERSION.tar.gz
    wget "http://192.168.1.231:8000/downloads/install-packy-agent.sh?packy_server_base_url=$PACKY_SERVER_BASE_URL&os=alpine" -O ./tmp/install-packy-agent.sh

    # This is workaround of Dockfile not supporting conditionals for COPY command
    test -f ./dist/packy-agent-$PACKY_AGENT_VERSION.tar.gz || touch ./dist/packy-agent-$PACKY_AGENT_VERSION.tar.gz
    docker build . -t packy-agent:$PACKY_AGENT_VERSION \
        --build-arg packy_server_base_url=$PACKY_SERVER_BASE_URL \
        --build-arg packy_agent_package_name=$PACKY_AGENT_PACKAGE_NAME \
        --build-arg packy_agent_version=$PACKY_AGENT_VERSION

#. Push Docker image to registry::

    docker login
    docker tag packy-agent:$PACKY_AGENT_VERSION dmugtasimovorg/packy-agent
    docker tag packy-agent:$PACKY_AGENT_VERSION dmugtasimovorg/packy-agent:$PACKY_AGENT_VERSION
    docker tag packy-agent:$PACKY_AGENT_VERSION dmugtasimovorg/packy-agent:latest
    docker push dmugtasimovorg/packy-agent:$PACKY_AGENT_VERSION
    docker push dmugtasimovorg/packy-agent:latest
    docker push dmugtasimovorg/packy-agent

Run
---

#. Start docker container::

    # Replace angle brackets (<>) with appropriate values
    ###############################################################################################

    export PACKY_AGENT_VERSION=<version>

    # For remote image:
    docker login
    export PACKY_IMAGE_NAME=dmugtasimovorg/packy-agent
    # for local image
    export PACKY_IMAGE_NAME=packy-agent

    # (!!!) You only need to set PACKY_SERVER_BASE_URL for
    #       debugging and testing purposes otherwise production value is set at image built time
    docker run -d -p 127.0.0.1:8001:8001 --name packy-agent-container \
        -e PACKY_SERVER_BASE_URL="<packy_server_base_url>" \
        $PACKY_IMAGE_NAME:$PACKY_AGENT_VERSION

#. Register agent at http://127.0.0.1:8001

Install Orange Pi Zero
----------------------

#. Download `Armbian Stretch – mainline kernel 4.14.y` archive from
   https://www.armbian.com/orange-pi-zero/ and uncompress it
#. Flash miscroSD with Etcher:

    #. Install Etcher from https://etcher.io/ and unzip
    #. Run unzipped *.AppImage file
    #. Click "Select image" and select previous downloaded and uncompressed Armbian *.img file
    #. Insert miscroSD card
    #. Click "Flash!"
    #. Enter your password if requested
    #. Wait until flashing is finished
    #. Remove microSD from computer

#. Insert microSD into Orange Pi Zero
#. Power on Orange Pi Zero
#. Connect Orange Pi Zero to wired network
#. Figure out which IP-address was assigned to Orange Pi Zero
   (probably list of DHCP leases on your router may help)
#. Login to Orange Pi Zero::

    ssh root@x.x.x.x
    # enter 1234 as password

#. Change root password and enter other information as prompted
#. Upgrade and reboot Orange Pi Zero::

    apt update
    apt upgrade
    reboot

#. Login to Orange Pi Zero again::

    ssh root@x.x.x.x

#. Install Packy Agent on to Orange Pi Zero:

    #. Download Packy Agent installation script::

        wget https://p04.packy.io/downloads/install-packy-agent.sh

    #. Set execute bit to `install-packy-agent.sh`::

        chmod +x install-packy-agent.sh

    #. Create special temp directory::

        # We need a temp dir on microSD for Orange PI
        mkdir /pip-tmp
        chmod a+rwx /pip-tmp

    #. Run installation script::

        TMPDIR=/pip-tmp PACKY_CONTROL_SERVER_PORT=80 PACKY_REMOVE_NGINX_DEFAULT_LANDING=True ./install-packy-agent.sh
