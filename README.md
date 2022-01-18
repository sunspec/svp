![SVP Logo](images/OpenSVP.png?raw=true)

---

[Sunspec Alliance](https://sunspec.org/) is an alliance of over 100 solar and storage distributed energy industry participants, together pursuing information standards to enable “plug & play” system interoperability.

[CanmetENERGY-Varennes](https://www.nrcan.gc.ca/science-data/research-centres-labs/canmetenergy-research-centres/varennes-qc-research-centre/5761) is a research center designing and implementing clean energy solutions, and build on knowledge that helps produce and use energy in ways that are more efficient and sustainable.

This repository contains all of the open-source OpenSVP components written in Python 3.7. Python 3.9+ does not appear to be compatible with the wxPython version. More development on ui.py is needed. 


## Contribution

For the contribution list, please refer to [Contribution section](doc/CONTRIB.md)

## Installation

Please refer to the [Install section](doc/INSTALL.md) for detailed instruction

## Scripts, Tests and Suites

### UL1741 SA standard 
Here is the repo [UL1741 SA repository][1741SA-url] make sure to use the "dev" branch

### IEEE 1547.1 standard 
The latest version is 1.4.2 and here is the repo [IEEE 1547.1 repository][1547-1-url]. Make sure to use the library (p1547.py) with the same version.

### DR_AS-NZS 4777.2 standard 
The latest version is 1.0.1 and here is the repo [DR_AS-NZS 4777.2 repository][4777-2-url]. Make sure to use the library (pAus4777.py) with the same version.

## Drivers
### SVPELAB
The SVPELAB is the repository use by the SIRFN members. It tries to assemble all the equipment from different manufacturer(Grid simulator, PV simulator, Data acquisition system, HILs, etc.) in a single repo [SVPELAB repository][svpelab-url].

### Support

For any bugs/issues, please refer to the [bug tracker][bug-tracker-url] section.



[bug-tracker-url]: https://github.com/sunspec/svp/issues
[1547-1-url]: https://github.com/jayatsandia/svp_1547.1
[1741SA-url]: https://github.com/sunspec/svp_UL1741SA/tree/dev/UL1741%20SA
[4777-2-url]: https://github.com/BuiMCanmet/DR_AS-NZS-Scripts
[svpelab-url]: https://github.com/sunspec/svp_energy_lab

