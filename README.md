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

_________________________________________________________

### Why North China Plain?
- North China Plain is one of China's food base, providing over 1/3 of food to feed 1.4 billion people of Chinese
- North China Plain is one of the fastest urbinazated region in this planet, the urban population increase from ~20% to ~60% from 1990 to 2019
### What is the value of this mapping methods?
- Using early time remotely sensed imagery (e.g., Lantsat 5 TM) achieve low accuracy than recent data (e.g., Landsat 8 OLI/Sentinel 2 MSI)
- We stack 3-years image together and use a fitting algorithm (Fourier transform) to capature the temporal feature as input for built-up classification
- Result showed that using Fourier features boost the classification accuracy of using Landsat 5 TM to be close to using Landsat 8 OLI and Sentinel 2 MSI
- We use temporal correction to remove inconsistent classifications and promote all accuracies of 1990-2019 to >94%.

_________________________________________________________
## Before using the repository
This repository allows you to reproduce the results of the mapping. Some knowledge are required to use the codes:
- Google Earth Engine (GEE) skills, which can be learnt from [here](https://developers.google.com/earth-engine/guides). If you know chinese, feel free to see this [tutorial](https://developers.google.com/earth-engine/tutorials/edu#chinese-language-materials)
- Python skills, which can be learnt everywhere.
- Virtual environment management of Anaconda

**After mastring above skills, please follow below steps to repreduce the results.**

_________________________________________________________
## Generall Workflow

#### --------------------------------------------------The input data--------------------------------------------------

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

#### --------------------------------------------------The study area--------------------------------------------------
Five middle and eastern provinces of China corresponding to the North China Plain region were selected as the study area . The area spanned 780,000 km2 and five provinces (i.e., Henan, Hebei, Shandong, Anhui, and Jiangsu) and two metropoles  (Beijing and Tianjin). The study area is one of China’s fastest developing regions, with the urban population rate (excluding the two metropoles) tripling from ~20% in 1990 to ~60% in 2018. The North China Plain holds a strategic position in China in terms of economic development and food security, generating ~37% of the gross domestic product and ~35% of China’s grain production in 2019.

<img src="https://github.com/wangjinzhulala/North_China_Plain_GEE_Organized/blob/master/Support_Result_Images/Map_1_Research_Arae.jpg"  width="600"/>

#### --------------------------------------------------The workflow--------------------------------------------------
The generall work flow is as follows:
- Preprocessing of input image data.
- Creating control points and visually inspect each of them.
- Conduct the classification using Random Forest
- Apply a Temporal-correction to remove inconsistent classifications
- Compare the "overall accuracy" and "area change" between this study and other datasets.

![The workflow](https://github.com/wangjinzhulala/North_China_Plain_GEE_Organized/blob/master/Support_Result_Images/The%20work%20Flow_Page_1.jpg)

_________________________________________________________

## Preprocessing of input image data
#### ----------------- Step_1: Dtermine the best Stack-years, Harmonic number and export the Fourier images -----------------
It is weird to process the Fourier transform at the first step. But we need to figure out how many data will be used in the Fourier transofrm. For example, if we use 2 years of data for the transform, then we will also need to use two years of data to create the cloud-free image of Landsat. As a result, the images used (aka, the stack-year) for Fourier transform determines the other data's producing.

The code for find the optimum Stack-years and Harmonic number is in *North_China_Plain_GEE_Organized/Process_1_GEE_Python_Classification/Sub_Process_1_Data_preparation_Fourier_transformation*

There ara two Jyputer Notebook files in this path:

> *Step_1_Detemine the best Harmonic number.ipynb* is to Determine the best "Harmonic number" for creating the Fourier images.

> Specifically, 100 random points were distributed through the research area, and the mean error between the original value and the fitted value for each point was computed with different harmonic numbers and stack years. The harmonic numbers were set to 1–10, and the stack years were set to 1–5 (where 1 means using only the normalized data from 2015, while 5 means using all the normalized indices from 2015–2019). The harmonic number was determined to be 3, i.e., where the most significant drop in mean error occurred. Fewer harmonic numbers are preferred as they produce fewer coefficients for later classification. The stack year was also determined to be 3 by balancing the data used for the discrete Fourier transform and the mean error decrease. Fewer stack years are preferred because built-up land can be mapped at a higher frequency if fewer data are used for the discrete Fourier transform.

> <img src="https://github.com/wangjinzhulala/North_China_Plain_GEE_Organized/blob/master/Process_4_Making_standard_figs_use_R/Section_1_1_Harmonic_Span.svg"  width="600"/>

> *Step_2_Create_Fourier_imgs.ipynb* is to export the Fourier images to GEE_assest.

> Specifically, we:
> 1) Loop through 1990-2019 by 3-year intervales;
> 2) Create the Fourier image using 3-year stack of NDVI/EVI/NDBI, respectively;
> 3) Export the Fourier image to Assest with name "AmplitudePhase{year}"


#### ---------------------------- Step_2: Create the NDVI/EVI/NDBI images (Indices predictor)  ----------------------------
The code for this step is in *North_China_Plain_GEE_Organized/Process_1_GEE_Python_Classification/Sub_Process_2_Data_preparation_Create_Normalized_index_images*. Only one Notebook in this path, which will:

> 1) Stack 3-years Landsat data;
> 2) Compute the mean image of the 3-years Landsat data;
> 3) Create the NDVI/EVI/NDBI from the mean image

#### ---------------------------- Step_3: Create the cloud-free images (Spectrum predictor) ----------------------------
The code for this step is in *North_China_Plain_GEE_Organized/Process_1_GEE_Python_Classification/Sub_Process_3_Data_preparation_Create_Landsat_Sentinel_Cloud_free_image*. Only one Notebook in this path, which will:

> 1) Stack 3-years Landsat/Sentinel data;
> 2) Apply the "simpleComposite" to create Landsat cloud-free image,use 'QA' band to to create Sentinel cloud-free image;
> 3) Export the result to Assest

#### ---------------------------- Step_4: Create the Meteorology images (Meteorology predictor)   ----------------------------
The code for this step is in *North_China_Plain_GEE_Organized/Process_1_GEE_Python_Classification/Sub_Process_4_Data_preparation_Prepare_Meterological_data/*. Two Notebooks are in this path:

> *Step_1_Convert_NetCDF_to_individual_TIF.ipynb* is to conver the raw NetCDF meteorogoly data to GeoTiff formate. This step is not necessary for the analysis of this study, and it requires the ArcGIS pro Python library.

> Specifically, we:
> 1) Import each NetCDF as multibands tif;
> 2) Export each band to a sigle Tif file

> *SStep_2_Composite_Meterology_data_into_3_year_mean_image.ipynb* is to compute the mean image of meteorology data in GEE.

> Specifically, we:
> 1) stack 3-years of meteorology data;
> 2) create the mean image;
> 3) export the mean image to Assest

_________________________________________________________

## Creating control points

Because the conversion from non-built-up land to built-up land is unlikely to occur , built-up samples collected using Landsat base-maps from 1990–1992 were used for classification in 1990–2013. The non-built-up samples collected using Google Earth High Definition (HD) maps were used for the classification from 1990 to 2019. Given the 30-year research period, a few sample points may be incorrect. The built-up samples were re-inspected using the Google Earth HD map of 2014 and then used for classification in 2014–2019. We also re-inspected samples to ensure high accuracy in the last two classifications, which will be used as masks to remove inconsistencies in the former classifications.

<img src="https://github.com/wangjinzhulala/North_China_Plain_GEE_Organized/blob/master/Support_Result_Images/The%20work%20Flow_Page_2.jpg"  width="600"/>

#### ---------------------------- Collection of built-up samples ----------------------------
The raw built-up samples were taken from the [National Settlements Database of China](http://www.resdc.cn/data.aspx?DATAID=302). These records were generated in 2000 and comprised two types of settlement: government sites (including the department offices of provinces, cities, districts, counties, towns, and villages) and the offices of nationally owned companies. The total number of National Settlement points of the study area is 751,411, exceeding the analysis capacity in this study. We randomly subset 5,000 points from the total dataset, then used historical Landsat images to visually check each point and further diminish the number to 4,000 by excluding low-quality points (e.g., those near water bodies or in hilly areas).

Because of the low quality of Landsat data from 1990 to 1992, two false-color base maps (one map created using NDVI, NDBI, and EVI; the other map created from the coefficients of the temporal features) were used to assist with a visual inspection. Each sample point was inspected against all three base maps. We manually nudged their position to the center of nearby built-up land for some points located at positions that could be easily misclassified (such as the edge of a village or a skim road). The visuall check can be see with [inspection video](https://github.com/wangjinzhulala/North_China_Plain_GEE_Organized/blob/master/Support_Video/Suplement_Video_1_How_we_visualy_check_points.mp4)

<img src="https://github.com/wangjinzhulala/North_China_Plain_GEE_Organized/blob/master/Support_Result_Images/Map_2_All_village_points.jpg"  width="600"/>

#### ---------------------------- Collection of non-built-up samples ----------------------------

> The code for this step is in *North_China_Plain_GEE_Organized/Process_1_GEE_Python_Classification/Sub_Process_5_Random_stratify_to_create_non_built_control_samples*.

A stratified sampling scheme was used to create the raw non-built-up samples. NDVI was used to stratify raw samples because it can distinguish different land covers effectively, thus promoting even distributed non-built-up samples among different land covers. The raw non-built-up samples were produced with the following procedures. First, NDVI data were produced from the cloud-free image of the research area in 2017–2019. Then 50,000 random points were generated to extract the value of NDVI. Next, the random points were reduced to 5,000, where the histogram of NDVI data was used to stratify the reduction . Finally, these 5,000 points were visually checked.

Non-built-up samples were visually inspected using the Google Earth HD map of 2019. Points located in built-up lands were removed. Points located close to built-up lands were manually nudged to nearby non-built-up land to avoid interference.

<img src="https://github.com/wangjinzhulala/North_China_Plain_GEE_Organized/blob/master/Process_4_Making_standard_figs_use_R/Section_1_5_Control_sample_NDVI_distribution.svg"  width="600"/>

_________________________________________________________

## Conduct the classification using Random Forest

#### ---------------------------- Before classification, make preparation and determine some parameter ----------------------------

The code for this section is in *North_China_Plain_GEE_Organized/Process_1_GEE_Python_Classification/Sub_Process_6_Before_classification_Feature_selection/*. There are 4 steps for this section:

> *Step_1_Extract_img_value_to_sample_points.ipynb* is to extract the input image's value to control points.

> Why doing that? Because we can directly use the control poits with image's value to train classifier, otherwise a lot of time would be wasted during classifier training on "Extrating image value to points"

> Specifically, we:
> 1) stack all input images into a multiband image;
> 2) extract the multiband image value to control points;
> 3) export the points of extraction

> *Step_2_Determine the best tree number and compare diff bands performances.ipynb*  runs a sensitive test between tree-number/diff-inbands to accuracy.

> We used the sklearn.model_selection.GridSearchCV module to test the impacts of tree number on accuracy . We found no accuracy gains were achieved with more than 100 trees. Thus we set the tree number to 100. We also investigated control sample sizes from 0.5% to 99% of the sample and computed corresponding accuracy . We found that ~50% of the control samples were sufficient to high accuracy. In this study, 75% of the control samples were used for built-up land mapping, among which 70% were used to train the RF classifier. As a result, 52.5% (75% × 70%) of control samples were used to train the RF classifier, which was sufficient for stable classification.

<img src="https://github.com/wangjinzhulala/North_China_Plain_GEE_Organized/blob/master/Process_4_Making_standard_figs_use_R/Section_1_6_1_Tree_Size_Accuracy.svg"  width="600"/>









