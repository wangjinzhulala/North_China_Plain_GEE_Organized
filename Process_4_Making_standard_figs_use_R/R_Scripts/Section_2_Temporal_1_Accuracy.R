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
  stat_summary(aes(color='Accuracy(se)'),
               fun  = 'mean',
               geom = 'line') +
  stat_summary(aes(fill='Accuracy(se)'),
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
                  mutate(year = str_replace(year,'_','-')) %>% 
                  mutate(Mask = as.numeric(window - 1))

data.temporal_area = read.csv(paste("../../Process_2_Temporal_Check/",
                                 "Result/",
                                 "Temporal_check_area.csv",sep=""),
                           stringsAsFactors = T)

data.temporal_2  =  data.temporal_area %>% 
                    pivot_longer(cols = colnames(data.temporal_area)[2:length(colnames(data.temporal_area))],
                               names_to = 'Year',
                               values_to = 'Accuracy') %>% 
                    mutate(Year = str_replace(Year,'_','-')) %>% 
                    mutate(Year = str_replace(Year,'X',''))
  




#________________________step 2: make plot of window~accuracy________________________

p_2_1 = data.temporal_1 %>% 
  ggplot(aes(x=Mask,y=accuracy))+
  stat_summary(aes(color='Accuracy(se)'),
               fun = 'mean',
               geom = 'line',) +
  stat_summary(aes(fill='Accuracy(se)'),
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
  xlab('Mask number')+
  ylab('Overall Accuracy (%)') +
  scale_x_continuous(breaks = seq(0,10,1)) +
  scale_y_continuous(breaks = seq(0,100,0.5))

plt_temporal_window_accuracy


#________________________step 3: make plot of Iteration~area________________________

p_2_2 = data.temporal_2  %>% 
  ggplot(aes(x=X,y=Accuracy,color=Year)) +
  geom_line() +
  labs(color = '',fill ='') 

plt_temporal_iteration_area = p_2_2 +
  guides(col = guide_legend(nrow = 5)) +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        legend.position = c(0.8,0.85),
        legend.key = element_rect(colour = NA, fill = NA)) +
  xlab('Iteration number')+
  ylab('Area (km2)') +
  scale_x_continuous(breaks = seq(0,10,1)) +
  scale_y_continuous()

plt_temporal_iteration_area

#__________step 4: combie window_acc and iteration_acc together_____________
plt_window_iteration =  plot_grid(plt_temporal_window_accuracy,
                                  plt_temporal_iteration_area,
                                  label_x = 0.5,
                                  align = 'v',
                                  label_y = 1,
                                  vjust = 1.8,
                                  nrow = 2,
                                  rel_widths = c(1,1),
                                  labels = c('a)','b)'),
                                  label_size = 12,
                                  label_fontface = 'plain')
plt_window_iteration


#__________step 5: make plot to compare the original/temporal corrected accuracy________

Temporal_checked_df = data.temporal_1 %>% 
                        filter(window == 3) %>% 
                        filter(iteration == 9)


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
  geom_line(data = Temporal_checked_df,
            group =1,
            mapping = aes(x=year,y=accuracy,color = 'Temporal Corrected'))


plt_compare_original_temporal_acc = p_2_3 +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.text.x = element_text(angle = 30, vjust = 0.5),
        axis.line.y.left = element_line(),
        legend.position = c(0.17, 0.9),
        legend.key = element_rect(fill = NA ))+
  labs(color = '',
       fill  = '',
       y = 'Accuracy (%)',
       x = 'Year') +
  scale_y_continuous(breaks = seq(0,100,0.5))

plt_compare_original_temporal_acc



#__________step 7: save to disk_____________

plt_temporal_window_accuracy
plt_temporal_iteration_area

plt_window_iteration
plt_compare_original_temporal_acc

ggsave(plot = plt_temporal_window_accuracy,
       "../Section_2_1_1_temporal_window_accuracy.png", 
       width = 20, 
       height = 12, 
       units = "cm",
       dpi=500)

ggsave(plot = plt_temporal_window_accuracy,
       "../Section_2_1_1_temporal_window_accuracy.svg", 
       width = 20, 
       height = 12, 
       units = "cm",
       dpi=500)



ggsave(plot = plt_temporal_iteration_area,
       "../Section_2_1_2_plt_temporal_iteration_area.png", 
       width = 20, 
       height = 10, 
       units = "cm",
       dpi=500)

ggsave(plot = plt_temporal_iteration_area,
       "../Section_2_1_2_plt_temporal_iteration_area.svg", 
       width = 20, 
       height = 10, 
       units = "cm",
       dpi=500)


###

ggsave(plot = plt_compare_original_temporal_acc,
       "../Section_2_1_2_compare_original_temporal_acc.svg", 
       width = 16, 
       height = 9, 
       units = "cm",
       dpi=500)

ggsave(plot = plt_compare_original_temporal_acc,
       "../Section_2_1_2_compare_original_temporal_acc.png", 
       width = 16, 
       height = 9, 
       units = "cm",
       dpi=500)

















