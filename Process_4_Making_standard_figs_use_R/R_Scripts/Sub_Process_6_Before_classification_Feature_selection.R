library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)


# read data, using pate to concat long file path string
data.p_6_grid_acc = read.csv(paste("../../Process_1_GEE_Python_Classification/",
                                    "Sub_Process_6_Before_classification_Feature_selection/",
                                    "Result/",
                                    "Grid_acc_tree.csv",sep=""),
                              stringsAsFactors = T)


data.p_6_grid_acc %>% 
  filter(In_Bands == 'Spectrum_Normalize_Fourier_Terrain_Meterology') %>% 
  ggplot(aes(x=Tree,y=Accuracy)) +
  stat_summary(fun = 'mean',geom = 'line',color = '#3081BA') +
  stat_summary(fun.data = 'mean_se',geom = 'ribbon',alpha = 1/3, fill = '#3081BA')


data.p_6_grid_acc %>% 
  ggplot(aes(x=Tree,y=Accuracy,group=In_Bands,color=In_Bands,fill=In_Bands)) +
  stat_summary(fun = 'mean',geom = 'line') +
  stat_summary(fun.data = 'mean_se',geom = 'ribbon',alpha = 1/3,size=0.1,color='grey99')


# read data, using pate to concat long file path string
data.p_6_sample_size = read.csv(paste("../../Process_1_GEE_Python_Classification/",
                                   "Sub_Process_6_Before_classification_Feature_selection/",
                                   "Result/",
                                   "Sample_size_acc.csv",sep=""),
                             stringsAsFactors = T)

# filter the accuracy from test and make plot
data.p_6_sample_size %>% 
  filter(Acc_type == 'acc_test') %>% 
  group_by(Size) %>% 
  ggplot(aes(x=Size,y=Acc_value)) +
  stat_summary(fun = 'mean',geom='line',color = '#3081BA')+
  stat_summary(fun.data = 'mean_se',geom = 'ribbon',alpha = 1/3, fill = '#3081BA')





