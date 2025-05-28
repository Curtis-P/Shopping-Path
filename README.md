# Shopping-Path

A CLI tool to take a shopping cart from erkul.games and return a "shortest" path for the ship components. It selects the destination with the highest amount of desired items and then finds the closest location that sells a desired item.

## Installation

Clone the repo:
```bash
git clone https://github.com/Curtis-P/Shopping-Path.git
cd source/to/repo
```

## Install dependencies
```bash
pip install -r requirements.txt
```

## Usage
```bash
python3 main.py stanton shoppingcart.csv
```

## Data requirements

This program uses data from starmap.space for locations and finder.cstone.space for component availability. Save the starmap.space containers api as LocationData.json within the directory. Finder.cstone.space does not have a public facing api, so you can scrape it yourself or use the [scraper I made](https://github.com/Curtis-P/Shopping-Path-Scraper) for this project. Make sure to save the scraped data as ShipComponents.csv.

The majority of information surrounding Star Citizen is available thanks to the community, as such not all information is available or accurate. An example I found during testing was the lack of location data for the pyro->stanton jump point. Thanks to Sketto in the Meridian Exploration Group Discord I was able to get the coordinates and create a mock entry to append to the starmap.space api:

```json
{
        "item_id": 26000,
        "System": "Pyro",
        "ObjectContainer": "Stanton Jumpoint",
        "InternalName": "Pyro_Stanton",
        "Type": "JumpPoint",
        "XCoord": 3310491.640,
        "YCoord": -27979408.221,
        "ZCoord": -2676285.679,
        "RotationSpeedX": 0,
        "RotationSpeedY": 0,
        "RotationSpeedZ": 0,
        "RotationAdjustmentX": 0,
        "RotationAdjustmentY": 0,
        "RotationAdjustmentZ": 0,
        "RotQuatW": "0.000000",
        "RotQuatX": 0,
        "RotQuatY": 0,
        "RotQuatZ": 0,
        "BodyRadius": 0,
        "OrbitalMarkerRadius": 0,
        "GRIDRadius": 0,
        "Comment": null,
        "Submitted": "2025-05-27 23:51:02"
    }
```