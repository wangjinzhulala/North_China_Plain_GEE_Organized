library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)



################## read the data of accuracy without threshold correction #############

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
  ggplot(aes(x=year_range,y=Overall_ACC,group=1)) +
  stat_summary(aes(color='Accuracy(sd)'),
               fun  = 'mean',
               geom = 'line') +
  stat_summary(aes(fill='Accuracy(sd)'),
               fun.data = 'mean_se',
               geom='ribbon',
               alpha = 1/5,
               color='grey98') +
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
  labs(color = '',
       fill = '')

plt_classification_acc





################## read the data of accuracy after temporal correction #############

#________________________step 1: read data and format the df________________________

data.temporal_1 = read.csv(paste("../../Process_2_Temporal_Check/",
                                   "Result/",
                                   "Temporal_check_acc.csv",sep=""),
                             stringsAsFactors = T) %>% 
                  mutate(year = str_replace(year,'_','-'))


#________________________step 2: make plot of window~accuracy________________________

p_2_1 = data.temporal_1 %>% 
  ggplot(aes(x=window,y=accuracy))+
  stat_summary(aes(color='Accuracy(sd)'),
               fun = 'mean',
               geom = 'line',) +
  stat_summary(aes(fill='Accuracy(sd)'),
               fun.data = 'mean_se',
               geom = 'ribbon',
               alpha=1/5) +
  scale_color_manual(values = c('#4990C2')) +
  scale_fill_manual(values = c('#4990C2')) +
  labs(color = '',fill ='') 
                                
plt_temporal_window_accuracy = p_2_1 +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        legend.position = c(0.89,0.4)) +
  xlab('Window size')+
  ylab('Accuracy (%)') +
  scale_x_continuous(breaks = seq(0,10,1)) +
  scale_y_continuous(breaks = seq(0,100,0.5))

plt_temporal_window_accuracy


#________________________step 3: make plot of Iteration~accuracy________________________

p_2_2 = data.temporal_1  %>% 
  filter(window==3) %>% 
  ggplot(aes(x=iteration,y=accuracy))+
  stat_summary(aes(color='Accuracy(sd)'),
               fun = 'mean',
               geom = 'line') +
  stat_summary(aes(fill='Accuracy(sd)'),
               fun.data = 'mean_se',
               geom = 'ribbon',
               alpha=1/5) +
  scale_color_manual(values = c('#4990C2')) +
  scale_fill_manual(values = c('#4990C2')) +
  labs(color = '',fill ='') 

plt_temporal_iteration_accuracy = p_2_2 +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        legend.position = c(0.89,0.4)) +
  xlab('Iteration number')+
  ylab('Accuracy (%)') +
  scale_x_continuous(breaks = seq(0,10,1)) +
  scale_y_continuous(breaks = seq(1,100,1.0),
                     labels = format(seq(1,100,1.0), digits=1, nsmall=1))

plt_temporal_iteration_accuracy

#__________step 4: combie window_acc and iteration_acc together_____________
plt_window_iteration =  plot_grid(plt_temporal_window_accuracy,
                                  plt_temporal_iteration_accuracy,
                                  label_x = 0.5,
                                  label_y = 1,
                                  vjust = 1.8,
                                  nrow = 2,
                                  rel_widths = c(1,1),
                                  labels = c('a)','b)'),
                                  label_size = 12,
                                  label_fontface = 'plain')
plt_window_iteration


#__________step 5: make plot to compare the original/temporal corrected accuracy________

p_2_3 = ggplot() +
  ######## Original accuracy
  stat_summary(data = data.p_7,
             group=1,
             mapping = aes(x=year_range, y=Overall_ACC),
             fun.data  = 'mean_se',
             fill = '#FF9D47',
             geom= 'ribbon',
             alpha = 1/5,
             color = 'grey95') +
  stat_summary(data = data.p_7,
               group=1,
               mapping = aes(x=year_range,y=Overall_ACC,color = 'Original Accuracy'),
               fun = 'mean',
               geom= 'line')+
  labs(x='Year',
       y='Accuracy (%)',
       color = '',
       fill = '') +
  ######## temporal correction accuracy
  geom_line(data = data.tempral_filter,
            group =1,
            mapping = aes(x=year,y=accuracy,color = 'Temporal Corrected'))


plt_compare_original_temporal_acc = p_2_3 +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        legend.position = c(0.13, 0.9),
        legend.key = element_rect(fill = NA ))+
  labs(color = '',
       fill  = '',
       y = 'Accuracy (%)',
       x = 'Size(%)')

plt_compare_original_temporal_acc


#__________step 6: save to disk_____________

plt_window_iteration
plt_compare_original_temporal_acc

ggsave(plot = plt_window_iteration,
       "../Section_2_1_temporal_iteration_accuracy.svg", 
       width = 14, 
       height = 16, 
       units = "cm",
       dpi=300)

ggsave(plot = plt_window_iteration,
       "../Section_2_1_temporal_iteration_accuracy.png", 
       width = 14, 
       height = 16, 
       units = "cm",
       dpi=300)


