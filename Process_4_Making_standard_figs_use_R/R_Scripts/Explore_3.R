library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)
library(scales)
library(colorRamps)


#______________read data, using paste to concat long file path string______________
data.landsat = read.csv(paste("../../Process_3_Explore_Result/",
                                   "Result/",
                                   "Landsat_distribution.csv",sep=""),
                             stringsAsFactors = T)

data.sentinel = read.csv(paste("../../Process_3_Explore_Result/",
                              "Result/",
                              "Sentinel_distribution.csv",sep=""),
                        stringsAsFactors = T)


#_____________________________Make the plot_______________________________________

data.landsat %>% 
  mutate(Sensor = case_when(Sensor == 'LT05' ~ 'Landsat 5',
                            Sensor == 'LE07' ~ 'Landsat 7',
                            Sensor == 'LC08' ~ 'Landsat 8')) %>% 
  group_by(Sensor,Year,Month) %>% 
  summarise('Observation' = n()) %>% 
  ggplot(aes(x=Year,y=Month,fill = Observation)) +
  geom_tile(color='grey95') +
  scale_x_continuous(breaks = seq(1990,2019,2),minor_breaks = seq(1990,2019,1)) +
  scale_y_continuous(breaks = seq(1,12),minor_breaks = 1) +
  scale_fill_binned() +
  facet_grid(.~Sensor,scales = 'free',space = "free_x")


data.sentinel %>% 
  group_by(Year,Month) %>% 
  summarise('Observation' = n()) %>% 
  ggplot(aes(x=Year,y=Month,fill = Observation)) +
  geom_tile(color='grey95') +
  scale_x_continuous(breaks = seq(2015,2019,1),minor_breaks = seq(2015,2019,1)) +
  scale_y_continuous(breaks = seq(1,12),minor_breaks = 1) +
  scale_fill_binned()
