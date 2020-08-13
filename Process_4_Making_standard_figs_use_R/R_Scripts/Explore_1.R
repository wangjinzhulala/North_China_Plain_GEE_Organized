library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)
library(scales)


#________________________________read data, using pate to concat long file path string__________________________________________

data.original_val = read.csv(paste("../../Process_3_Explore_Result/",
                                   "Result/",
                                   "Original_image_value.csv",sep=""),
                             stringsAsFactors = T) %>% 
                             mutate(Type='Original',time = as.Date(time)) %>% 
                             pivot_longer(cols = c(NDVI,NDBI,EVI),names_to = 'Index',values_to='val')

data.fitted_val = read.csv(paste("../../Process_3_Explore_Result/",
                                   "Result/",
                                   "Fitted_image_value.csv",sep=""),
                             stringsAsFactors = T)  %>% 
                             mutate(Type='Fitted',time = as.Date(time)) %>% 
                             pivot_longer(cols = c(NDVI,NDBI,EVI),names_to = 'Index',values_to='val')

data.original_fitted = rbind(data.fitted_val,data.original_val)

data.original_fitted %>% 
  group_by(Type) %>% 
  ggplot(aes(x=time,y=val,color=Type)) +
  geom_line() +
  facet_grid(Index~.,scale='free') +
  scale_x_date(minor_breaks = '1 month',
               breaks =  seq(as.Date("2017-01-01"), as.Date("2020-01-01"), by="6 months"), 
               date_labels = "%b\n%Y") +
  labs(x='Date',y= 'Value')

