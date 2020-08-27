library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)
library(scales)
library(colorRamps)


#______________read data, using paste to concat long file path string______________
data.axia0 = read.csv(paste("../../Process_3_Explore_Result/",
                              "Result/",
                              "Axix_0_long.csv",sep=""),
                        stringsAsFactors = T)

data.axia1 = read.csv(paste("../../Process_3_Explore_Result/",
                            "Result/",
                            "Axix_1_long.csv",sep=""),
                      stringsAsFactors = T)


#____________________________________Make the plot_______________________________
data.axia0 %>% 
  ggplot(aes(x=Lat,y=Percent,color=Year)) +
  geom_line()

data.axia1 %>% 
  ggplot(aes(x=Lon,y=Percent,color=Year)) +
  geom_line()






