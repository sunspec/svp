#!/usr/bin/bash

# Set the git directories to pull down code
SSH_OR_HTTPS="SSH"

if [[ "$SSH_OR_HTTPS" == "HTTPS" ]]; then
    echo "Cloning repositories using the $SSH_OR_HTTPS method."
    SVP="https://github.com/jayatsandia/svp.git"
    # Alternative: "https://github.com/sunspec/svp.git"

    declare -a WORKING_DIRECTORIES=(\
    "https://github.com/jayatsandia/svp_1547.1.git" \
    "https://github.com/jayatsandia/svp_UL1741SA.git" \
    "https://github.com/jayatsandia/svp_energy_lab.git" \
    "https://github.com/jayatsandia/svp_additional_tools.git" \
    #"https://github.com/jayatsandia/svp_additional_tools.git"\
    )
	
else 
    echo "Cloning repositories using the $SSH_OR_HTTPS method." 
    SVP="git@github.com:jayatsandia/svp.git"
    # Alternative: "git@github.com:sunspec/svp.git"

    declare -a WORKING_DIRECTORIES=(\
    "git@github.com:jayatsandia/svp_1547.1.git" \
    "git@github.com:jayatsandia/svp_UL1741SA.git" \
    "git@github.com:jayatsandia/svp_energy_lab.git" \
    "git@github.com:jayatsandia/svp_additional_tools.git" \
    #"git@github.com:jayatsandia/svp_additional_tools.git"\
    )

fi

if [ -d "./svp_software" ]
then
    echo "Removing svp_software directory"
    rm -rf svp_software
else
    echo "No svp_software directory found"
fi

mkdir svp_software
cd svp_software

git clone "$SVP"
for repo in "${WORKING_DIRECTORIES[@]}"; do
    echo "Cloning: $repo"
    git clone "$repo"
done

echo "Moving the SVP Energy Lab into each working directory"
cp -r svp_energy_lab/Lib/svpelab/* svp_1547.1/1547.1/Lib/svpelab/
cp -r svp_energy_lab/Lib/svpdnp3 svp_1547.1/1547.1/Lib/

cp -r svp_energy_lab/Lib svp_additional_tools/

cp -r svp_energy_lab/Lib svp_UL1741SA/UL1741\ SA

echo "Downloading python dependencies"
pip3 install -r svp/svp_requirements.txt 

echo "Starting the SVP"
python3 svp/ui.py
