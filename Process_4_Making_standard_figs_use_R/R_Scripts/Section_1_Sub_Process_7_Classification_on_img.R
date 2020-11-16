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


# calculate the summary data
data_summary <- data.p_7 %>% 
  group_by(year_range) %>%   
  summarise(mean = mean(Overall_ACC),  
            sd = sd(Overall_ACC), 
            n = n(),  
            SE = sd(Overall_ACC)/sqrt(n())) 




#______________________step 3: make plot________________________

#_____________Bar plot with standard error___________
summary_Plot <- ggplot(data_summary, aes(year_range, mean)) + 
  geom_col(width = 0.35,fill = 'grey90') +  
  geom_errorbar(aes(ymin = mean - SE, ymax = mean + SE), width=0.3,size = 0.25) +
  coord_cartesian(ylim = c(80, 96))+
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
  scale_y_continuous(breaks = seq(0,100,2.5),expand = c(0, 0)) +
  labs(color = '',
       fill = '')



#_____________Box plot with standard error___________
plt_classification_acc = data.p_7 %>% 
  ggplot(aes(x=year_range,y=Overall_ACC)) +
    stat_boxplot(geom ='errorbar',width = 0.4,color='grey20') +
  geom_boxplot(outlier.size = 0.8, 
               outlier.alpha = 0.6,
               outlier.shape = 1,
               width = 0.5,
               size=0.3) +
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
  scale_y_continuous(breaks = seq(0,100,5)) +
  labs(color = '',
       fill = '')
  

#_____________step 4: save plot to disk____________

plt_classification_acc
summary_Plot

ggsave(plot = summary_Plot,
       "../Section_1_7_classification_Accuracy_bar.svg", 
       width = 20, 
       height = 10, 
       units = "cm",
       dpi=500)

ggsave(plot = summary_Plot,
       "../Section_1_7_classification_Accuracy_bar.png", 
       width = 20, 
       height = 10, 
       units = "cm",
       dpi=500)

#-----------


ggsave(plot = plt_classification_acc,
       "../Section_1_7_classification_Accuracy.svg", 
       width = 20, 
       height = 10, 
       units = "cm",
       dpi=500)

ggsave(plot = plt_classification_acc,
       "../Section_1_7_classification_Accuracy.png", 
       width = 20, 
       height = 10, 
       units = "cm",
       dpi=500)









