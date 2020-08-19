library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)
library(comprehenr)

################################## Read the accuracy from original/10folds-correc ##########################

#________________________________read data, using pate to concat long file path string__________________________________________
data.area_change = read.csv(paste("../../Process_2_Temporal_Check/",
                                   "Result/",
                                   "Area_change.csv",sep=""),
                             stringsAsFactors = T)


# make plot
data.area_change %>% 
  filter(Type == 'My') %>% 
  ggplot(aes(x=year,y=sum,color=EN_Name,group=EN_Name)) +
  geom_line() +
  scale_color_viridis_d() +
  labs(x='Year Range',y = 'Pixel Count') +
  theme_bw() 







