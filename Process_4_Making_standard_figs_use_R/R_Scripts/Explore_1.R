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


#________________________________read Original_10K, using pate to concat long file path string__________________________________________

data.original_10K = read.csv(paste("../../Process_3_Explore_Result/",
                                   "Result/",
                                   "Original_value.csv",sep=""),
                             stringsAsFactors = T) %>% 
  mutate(Date = as.Date(time),From = 'Original value')

data.fitted_10K = read.csv(paste("../../Process_3_Explore_Result/",
                                   "Result/",
                                   "Fitted_values.csv",sep=""),
                             stringsAsFactors = T) %>% 
  mutate(Date = as.Date(Date),From = 'Fourier fit')


# bind the values together
data.Fourier = rbind(data.original_10K %>% select(Date,From,Type,Index,value),
                     data.fitted_10K   %>% select(Date,From,Type,Index,value))



# individual plots

data.Fourier_Evi = data.Fourier %>% 
  filter( Index == 'EVI')

data.Fourier_Evi  %>% 
  ggplot(aes(x=Date,y=value)) +
  facet_wrap(.~Type,nrow = 1) +
  scale_y_continuous(limits = c(0,0.7),
                     expand = c(0,0))+ 
  scale_x_continuous(expand = c(0,0)) +
  stat_summary(data=data.Fourier_Evi %>% 
                 filter(From == 'Fourier fit'),
               geom = 'line',
               fun = 'mean')


# only plot the fitted values
data.Fourier %>% 
  filter( From == 'Fourier fit') %>% 
  filter((value<0.8)&(value>-0.3)) %>% 
  filter(Date < as.Date('2018-01-01')) %>% 
  ggplot(aes(x=Date,y=value,color=Type)) +
  facet_wrap(Index~.,ncol = 1) +
  stat_summary(geom = 'line',fun = 'mean') +
  scale_x_date(breaks =  seq(as.Date("2017-01-01"), as.Date("2020-01-01"), by="4 months"), 
               date_labels = "%b\n%Y") +
  labs(x='Date',y= 'Value')


# facet plot
data.Fourier %>% 
  filter(  (From == 'Original value') & (((value > - 1)&(value < 1)))) %>% 
  ggplot(aes(x=Date,y=value)) +
  facet_grid(Index~Type) +
  stat_density_2d(
    geom = 'raster',
    aes(fill = after_stat(count)),
    contour = FALSE)  +
  stat_summary(data = data.Fourier %>% filter(  (From == 'Fourier fit') & (value < 1)) ,
               fun = 'mean',
               aes(color = 'Fourier fit'),
               geom ='line',
               size = 1) +
  scale_color_manual(values ='#DD4F42' )








