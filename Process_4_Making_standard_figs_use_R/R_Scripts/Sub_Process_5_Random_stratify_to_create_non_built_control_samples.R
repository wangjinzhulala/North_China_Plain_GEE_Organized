library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)


# read data, using pate to concat long file path string
data.p_5_NDVI_hist = read.csv(paste("../../Process_1_GEE_Python_Classification/",
                                    "Sub_Process_5_Random_stratify_to_create_non_built_control_samples/",
                                    "Result_df/",
                                    "NDVI_area_propotion.csv",sep=""),
                      stringsAsFactors = T)

# only chose the year of 2017-2019 and pivot the data to long format
data.p_5_NDVI_hist.long = data.p_5_NDVI_hist  %>% 
                              filter(Year_range == '2017_2019') %>% 
                              pivot_longer(col=-c(Year_range,NDVI),
                                           names_to = 'type',
                                           values_to = 'val') %>% 
                              mutate(type = case_when(
                                                      type == 'Freq' ~ 'NDVI',
                                                      type == 'Select_num' ~ 'Sample'
                              ))

# plot the histogram of NDVI in the research area in 2017-2019
data.p_5_NDVI_hist.long  %>% 
  ggplot(aes(x=NDVI,y=val,fill=type)) +
  geom_bar(stat = 'identity') +
  scale_y_log10() +
  ylab('Counts')

  
  
  




