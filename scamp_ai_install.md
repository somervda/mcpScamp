# Setting Up Jetson

## Why Jetson?

https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/

### Jetson Setup Steps

    1. Create a sd card and setup Jetson
    2. Install a physical SSD
    3. Run the steps layed out in SD to SDD video (No external Linux machine needed)
    4. Install Ollama
        curl -fsSL https://ollama.com/install.sh | sh
    5. Test access to the Ollama web service from another machine
        http://jetai.local:11434/
        (This should fail so you need to update the serviced definition to open access to olklama API)

    6. Update sudo nano /etc/systemd/system/ollama.service.
        Add this Environment setting
            Environment="OLLAMA_HOST=0.0.0.0"
    7. sudo systemctl daemon-reload
    8. sudo systemctl restart ollama.service
    9. Test http://jetai.local:11434/ again.
        Should work

### Quick look at jetson running Ollama

    1. sudo apt install btop
    2. Start a monitor running btop
    3. Get a couple of small models
    4. ollama run llama3.2:latest --verbose
    5. ollama run gemma3:4b –verbose
    6. ollama list

# Raspberry PI 5 (4GB)

Install Raspberry Pi OS Lite 64 bit

Install OS and ssd (I already had a pimoroni nvme hat with a ssd installed and set as bootable)

## Docker install

    1. curl -sSL https://get.docker.com | sh

## Set up Portainer

https://pimylifeup.com/raspberry-pi-portainer/

    1. sudo docker pull portainer/portainer-ce:latest
    2. sudo docker volume create portainer_data
    3. sudo docker run -d -p 8000:8000 -p 9443:9443 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest

https://piai.local:9443/#!/home

## Install open-webui

    1. sudo docker run -d -p 3000:8080 -e OLLAMA_BASE_URL=http://jetai:11434 -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main

## or specific open-webui version

    1. docker rm -f open-webui
    2. docker pull ghcr.io/open-webui/open-webui:0.6.14
    3. sudo docker run -d -p 3000:8080 -e OLLAMA_BASE_URL=http://jetai:11434 -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:0.6.14
