library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)


# read data, using pate to concat long file path string
data.p_7_acc_sentinel = read.csv(paste("../../Process_1_GEE_Python_Classification/",
                                   "Sub_Process_7_Classification_on_img/",
                                   "Result/",
                                   "Classification_Accuracy_landsat_sentinel.csv",sep=""),
                             stringsAsFactors = T)

data.p_7_acc_landsat = read.csv(paste("../../Process_1_GEE_Python_Classification/",
                                      "Sub_Process_7_Classification_on_img/",
                                      "Result/",
                                      "Classification_Accuracy.csv",sep=""),
                                stringsAsFactors = T)

# mutate the df so we can get 'Sentinel/Landsat' and 'Year range' seperately
data.p_7_acc_landsat = data.p_7_acc_landsat %>% 
  separate(col = year, into = c('type','start','end'),sep = '_') %>% 
  unite(col = year_range, start,end,sep='-')


data.p_7_acc_sentinel = data.p_7_acc_sentinel %>% 
  separate(col = year, into = c('type','start','end'),sep = '_') %>% 
  unite(col = year_range, start,end,sep='-')


# concat two df together and make figure
data.p_7 = rbind(data.p_7_acc_landsat,data.p_7_acc_sentinel)

data.p_7 %>% 
  ggplot(aes(x=year_range,y=Overall_ACC,group = type,color=type, fill=type)) +
  stat_summary(fun = 'mean',geom = 'line') +
  stat_summary(fun.data = 'mean_se',geom='ribbon',alpha = 1/5,color='grey98') +
  labs(x = 'Year Range',y ='Overall Accuracy') +
  theme(axis.text.x = element_text(angle = 30, vjust = 0.5, hjust=0.5))
  






