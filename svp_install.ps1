# PowerShell script to install the SVP

# Delete old directory and create new directory
Remove-Item "svp_software" -Recurse -Force
Write-Output "Creating svp_software\ directory"
New-Item "svp_software" -itemType Directory
Set-Location "svp_software"

# Clone the software of interest - need to have SSH keys
Write-Output "Using SSH to git clone directories."
Write-Output "Confirm keys are in %HOME%\.ssh\config\"

git clone git@github.com:jayatsandia/svp.git --verbose
git clone git@github.com:jayatsandia/svp_1547.1.git --verbose
git clone git@github.com:jayatsandia/svp_UL1741SA.git --verbose
git clone git@github.com:jayatsandia/svp_energy_lab.git --verbose
git clone git@github.com:jayatsandia/svp_additional_tools.git --verbose

# Copy SVP Energy Lab files into Working Directories
Write-Output "Moving the SVP Energy Lab into each working directory"
Copy-Item -Path "svp_energy_lab\Lib" -Destination "svp_additional_tools\" -Recurse
Copy-Item -Path "svp_energy_lab\Lib" -Destination "svp_UL1741SA\UL1741 SA\" -Recurse

Copy-Item -Path "svp_energy_lab\Lib\svpdnp3" -Destination "svp_1547.1\1547.1\Lib\" -Recurse
Copy-Item -Path "svp_energy_lab\Lib\svpelab\*" -Destination "svp_1547.1\1547.1\Lib\svpelab\" -Recurse

Write-Output "Downloading python dependencies"
pip3 install -r svp/svp_requirements.txt 

Write-Output "Starting the SVP..."
python3 svp/ui.py
