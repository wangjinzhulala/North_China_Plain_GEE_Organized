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
  ggplot(aes(x=year_range,y=count,color=type,group=type)) +
  geom_line() +
  labs(x='Year Range',y = 'Pixel Count') +
  theme(axis.text.x = element_text(angle = 20,vjust = 0.4)) 








