library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)


#________________________step 1: read data and format the df________________________
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

#______________________step 2: formating the df________________________

# mutate the df so we can get 'Sentinel/Landsat' and 'Year range' seperately
data.p_7_acc_landsat = data.p_7_acc_landsat %>% 
  separate(col = year, into = c('type','start','end'),sep = '_') %>% 
  unite(col = year_range, start,end,sep='-') %>% 
  filter(year_range != '2014-2016') %>% 
  filter(year_range != '2017-2019')


data.p_7_acc_sentinel = data.p_7_acc_sentinel %>% 
  separate(col = year, into = c('type','start','end'),sep = '_') %>% 
  unite(col = year_range, start,end,sep='-')


# concat two df together and make figure
data.p_7 = rbind(data.p_7_acc_landsat,data.p_7_acc_sentinel) 


#______________________step 3: make plot________________________

plt_classification_acc = data.p_7 %>% 
  ggplot(aes(x=year_range,y=Overall_ACC)) +
  stat_boxplot(geom ='errorbar',width = 0.25,color='#CAA1A0') +
  geom_boxplot(outlier.size = 0.8, 
               outlier.alpha = 0.6,
               outlier.shape = 1,
               width = 0.3,
               size=0.3)+
  labs(x = 'Year',
       y ='Accuracy (%)') +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        legend.position = c(0.65, 0.8)) +
  scale_color_manual(values = c('#3081BA')) +
  scale_fill_manual(values = c('#3081BA')) +
  scale_y_continuous(breaks = seq(1,100,0.5)) +
  labs(color = '',
       fill = '')
  

#_____________step 4: save plot to disk____________

plt_classification_acc

ggsave(plot = plt_classification_acc,
       "../Section_1_7_classification_Accuracy.svg", 
       width = 19, 
       height = 10, 
       units = "cm",
       dpi=300)

ggsave(plot = plt_classification_acc,
       "../Section_1_7_classification_Accuracy.png", 
       width = 19, 
       height = 10, 
       units = "cm",
       dpi=300)









