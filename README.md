# flamecell

<img src="docs/flamecell_logo.png" alt="FLAMECELL Logo" width="200"/>

![version](https://img.shields.io/badge/version-0.4.0-blue.svg)
![license](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)

'flamecell' is a Python package to simulate forest fire dynamics using a cellular 
It features wind and humidity effects, real world map-based inputs, and an interactive Streamlit interface.

## Features
- Cellular automaton for wildfire spread
- Environmental effects: **wind** and **humidity** and **temperature**
- Real map raster input support (land cover)
- Streamlit web interface for interactive control
- Visualization of fire spread with color-coded maps

## Installation

```bash
$ git clone https://github.com/your-username/flamecell.git
$ cd flamecell
$ poetry install
```

## Quick Start
Run the app with streamlit to start
```bash
streamlit run src/flamecell/app.py
```

Then follow the steps in the browser:

1.Select a region on the map.

2.Select desired resolution and wind/temperature/humidity on the sidebar

3.Generate the simulation grid.

4.Click to choose fire source.

5.Run the simulation and watch the fire spread!

## Note on Map Data
Map data for the whole Germany is large (~466 MB).
Please manually ['download'](https://heidata.uni-heidelberg.de/dataset.xhtml?persistentId=doi:10.11588/data/IUTCDN) the .tif file and place it under src/flamcell/data/. 

You can also download other EU country's map, just change the `TIF_PATH` in the app.py to the map's name


## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`flamecell` was created by YiyangZhu. It is licensed under the terms of the MIT license.

## Credits

`flamecell` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
