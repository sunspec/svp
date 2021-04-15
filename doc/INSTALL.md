### Published packages

| Package                                                     | Version | Description                                                            |
| ----------------------------------------------------------- | ------- | ---------------------------------------------------------------------- |
| [`@sunspec/pysunspec`][pysunspec-url]                       | 2.0.0   | Custom library packages needed to run OpenSVP                          |
### Software requirements
* Python 3.7+ [Link](https://www.python.org/downloads/)
* Git [Link](https://git-scm.com/download/win)

### Install dependencies

1. Install Python 3.7+ on your computer or python environment if it hasn't been done yet
2. Install Git on your computer if not done yet
3. Download/Clone this OpenSVP repository on your computer
4. Install missing packages for python with the command displayed:

The list packages required are included in ./svp_requirements.txt

Open folder location in an Winders Explorer folder and type cmd in address bar.
This should open a command prompt
Execute the following command:

```bash
pip install -r svp_requirements.txt
```

### Execute OpenSVP

You will need to create a project folder and create a folder named Lib. 

You will need to copy/clone the svpelab drivers into that folder Lib: [svpelab][svpelab-url]

After installing all the dependencies, you can execute OpenSVP through commands:

```bash
cd /opensvp_dir
python ui.py
```


[pysunspec-url]: https://github.com/sunspec/pysunspec
[svpelab-url]: https://github.com/BuiMCanmet/svp_energy_lab/tree/dev_canmet_python37
