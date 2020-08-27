library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)


#________________________step 1: read data and format the df________________________
data.p_8_original = read.csv(paste("../../Process_1_GEE_Python_Classification/",
                                       "Sub_Process_8_Determine_the_threshold_for_the_sum_of_10_random_classification/",
                                       "Result/",
                                       "Threshold_acc_df.csv",sep=""),
                                 stringsAsFactors = T)


# rearrange the year column se we get 'year_range' and type of 'landsat/sentinel'
data.p_8 = data.p_8_original[, !(colnames(data.p_8_original) %in% c("Feature"))]

data.p_8 = data.p_8 %>% 
  separate(col = Year,into = c('type','start','end'),sep = '_') %>% 
  unite(col = year_range, start,end,sep='-') %>% 
  filter(  !(type =='Landsat'& year_range %in%  c('2014-2016','2017-2019')))


#____________________________Make the figure to show threshold == 4 is optimum____________________________________________

p_1_8 = data.p_8 %>% 
  ggplot(aes(x=Threshold,y=Accuracy,group=Threshold))+
  stat_boxplot(geom ='errorbar',
               width = 0.7,
               color='#CAA1A0') +
  geom_boxplot(outlier.size = 0.8, 
               outlier.alpha = 0.6,
               outlier.shape = 1,
               width = 0.7,
               size=0.3)+
  stat_summary(fun = 'median',
               geom='line',
               group=1,
               size=0.5,
               color = '#507DA7')

plt_threshold = p_1_8 + 
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line()) +
  xlab('Threshold')+
  ylab('Accuracy (%)') +
  scale_x_continuous(breaks = seq(0,10,1)) +
  scale_y_continuous(breaks = seq(0,100,1))

plt_threshold


#_________________step 3: save plot to disk_____________________


ggsave(plot = plt_threshold,
       "../Section_1_8_Ten_folds_correction.svg", 
       width = 20, 
       height = 10, 
       units = "cm",
       dpi=300)


ggsave(plot = plt_threshold,
       "../Section_1_8_Ten_folds_correction.png", 
       width = 20, 
       height = 10, 
       units = "cm",
       dpi=300)


