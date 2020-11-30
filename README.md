# Guide for mapping the bulit-up land in the North China Plain

>### Instruction for use
>1. Copy this repository to you PC
>- Clone this repository using 'git clone https://github.com/wangjinzhulala/North_China_Plain_GEE_Organized.git'
>- Or [Download the Zip](https://github.com/wangjinzhulala/North_China_Plain_GEE_Organized/archive/master.zip)
>2. Create an Python environment
>- Download and install [Anaconda](https://www.anaconda.com/products/individual)
>- Navigate to the repository you just downloaded (e.g., "C:/Users/wangj/Desktop/North_China_Plain_GEE_Organized")
>- Open "Anaconda Prompt", then type in "cd C:/Users/wangj/Desktop/North_China_Plain_GEE_Organized"
>- Type "conda env create --file environment.yml"

### Why North China Plain?
- North China Plain is one of China's food base, providing over 1/3 of food to feed 1.4 billion people of Chinese
- North China Plain is one of the fastest urbinazated region in this planet, the urban population increase from ~20% to ~60% from 1990 to 2019
### What is the value of this mapping methods?
- Using early time remotely sensed imagery (e.g., Lantsat 5 TM) achieve low accuracy than recent data (e.g., Landsat 8 OLI/Sentinel 2 MSI)
- We stack 3-years image together and use a fitting algorithm (Fourier transform) to capature the temporal feature as input for built-up classification
- Result showed that using Fourier features boost the classification accuracy of using Landsat 5 TM to be close to using Landsat 8 OLI and Sentinel 2 MSI
- We use temporal correction to remove inconsistent classifications and promote all accuracies of 1990-2019 to >94%.

## Before using the repository
This repository allows you to reproduce the results of the mapping. Some knowledge are required to use the codes:
- Google Earth Engine (GEE) skills, which can be learnt from [here](https://developers.google.com/earth-engine/guides). If you know chinese, feel free to see this [tutorial](https://developers.google.com/earth-engine/tutorials/edu#chinese-language-materials)
- Python skills, which can be learnt everywhere.
- Virtual environment management of Anaconda

**After mastring above skills, please follow below steps to repreduce the results.**

## Generall Workflow

### The input data

There are five types of input data for the built-up land mapping, all of them (except for Meteorology data) can be accessed at the GEE.
- Spectral: the cloud-free image of Landsat/Sentinel
- Indices: the NDVI/EVI/NDBI computed from Landsat
- Fourier: Coefficients of the Discrete Fourier Transformation on indices images
- Meteorology: China Meteorological Forcing Data[here](https://data.tpdc.ac.cn/en/data/8028b944-daaa-4511-8769-965612652c49/?q=China%20Meteorological%20Forcing%20Data)
- Terrain: Elevation and Slope form the Shuttle Radar Topography Mission 

|Input type|Source	|Spatial resolution	|Number of bands	|Years|
|-----|-----|-----|-----|-----|
|Spectral|	Landsat TM	|30 m	|7	|1990-2010|
| |Landsat ETM+	|30 m	|9	|2011-2013|
| |	Landsat OLI	|30 m	|11	|2014-2019|
| |	Sentinel-2A MSI	|10 m	|13	|2015-2019|
|Indices	|NDVI	|30 m	|1	|1990-2019|
| |	EVI	|30 m	|1	|1990-2019|
| |	NDBI	|30 m	|1	|1990-2019|
|Fourier|	Coefficients of the Discrete Fourier Transformation	|30 m	|24	|1990-2019|
|Meteorology	|China Meteorological Forcing Data	|1°	|7	|1990-2019|
|Terrain|	Elevation	|30 m	|1	|1990-2019|
| |	Slope	|30 m	|1	|1990-2019| 


### The workflow
The generall work flow is as follows:
- Creating control points and visually inspect each of them.
- Preprocessing of input image data.
- Conduct the classification using Random Forest
- Apply a Temporal-correction to remove inconsistent classifications
- Compare the "overall accuracy" and "area change" between this study and other datasets.

![The workflow](https://github.com/wangjinzhulala/North_China_Plain_GEE_Organized/blob/master/Support_Result_Images/The%20work%20Flow_Page_1.jpg)












































