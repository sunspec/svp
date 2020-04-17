### Published packages

| Package                                                     | Version | Description                                                            |
| ----------------------------------------------------------- | ------- | ---------------------------------------------------------------------- |
| [`@sunspec/pysunspec`][pysunspec-url]                       | 2.0.0   | Custom library packages needed to run OpenSVP                          |

### Install dependencies

The list packages required are included in ./svp_requirements 

Set up all dependencies:

from the root directory:

```bash
cd /opensvp_dir
pip install -r svp_requirements
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