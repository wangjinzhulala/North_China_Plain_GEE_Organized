library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)
library(comprehenr)

################################## Read the accuracy from original/10folds-correc ##########################


#________________________________read data, using pate to concat long file path string__________________________________________
data.accuracy = read.csv(paste("../../Process_2_Temporal_Check/",
                                  "Result/",
                                  "Accuracy_comparision.csv",sep=""),
                            stringsAsFactors = T)



# make the plot
data.accuracy %>% 
  select(Type,year,Overall_ACC) %>% 
  ggplot(aes(x=year,y=Overall_ACC,color=Type,group=Type))+
  geom_line() +
  labs(x='Year Range',y='Overall Accuracy') +
  theme_bw()


