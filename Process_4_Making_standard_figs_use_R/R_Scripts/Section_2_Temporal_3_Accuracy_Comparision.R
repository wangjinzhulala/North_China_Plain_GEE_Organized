library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)
library(comprehenr)



#________________________step 1: read data and format the df________________________

data.accuracy = read.csv(paste("../../Process_2_Temporal_Check/",
                                  "Result/",
                                  "Accuracy_comparision.csv",sep=""),
                            stringsAsFactors = T) %>% 
                mutate(year = str_replace(year,'_','-'))


data.area_change = read.csv(paste("../../Process_2_Temporal_Check/",
                                  "Result/",
                                  "Area_change.csv",sep=""),
                            stringsAsFactors = T)%>% 
  mutate(year = str_replace(year, "_", "-"))

#______________________step 2: make plot of area comparision________________________

p_2_3 = data.area_change %>% 
  group_by(year,Source) %>% 
  summarise(area = sum(area_km2)) %>% 
  ggplot(aes(x=year,y=area,color=Source,group = Source)) + 
  geom_line(size=1) +
  geom_point(size=1.5) +
  scale_color_hue()+
  scale_color_discrete(labels = c("GAIA", "This study"))

plt_area_change_compare = p_2_3 +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        axis.text.x.bottom = element_blank(),
        legend.position = c(0.10, 0.8),
        legend.key = element_rect(fill = NA ))+
  labs(color = '',
       fill  = '',
       y = 'Area (km2)',
       x = '')


plt_area_change_compare

#______________________step 3: make plot of accuracy comparision________________________

p_2_3 = data.accuracy %>% 
  select(Type,year,Overall_ACC) %>% 
  ggplot(aes(x=year,y=Overall_ACC,color=Type,group=Type)) +
  geom_line(size=1,show.legend = F) +
  geom_point(size=1.5,show.legend = F) 



plt_acc_compare = p_2_3 +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        legend.position = c(0.09, 0.96),
        legend.key = element_rect(fill = NA )) +
  scale_color_discrete(labels = c("GAIA", "This study")) +
  labs(color = '',
       fill  = '',
       x='Year',
       y='Accuracy (%)') 

plt_acc_compare

#______________________step 4: combine plot________________________

plt_compare_acc_area =  plot_grid(plt_area_change_compare,
                                  plt_acc_compare,
                                  align = 'v',
                                  label_x = 0.5,
                                  label_y = 1,
                                  vjust = 2,
                                  nrow = 2,
                                  rel_widths = c(1,1),
                                  labels = c('a)','b)'),
                                  label_size = 12,
                                  label_fontface = 'plain')
plt_compare_acc_area


#______________________step 5: save plot to disk________________________


ggsave(plot = plt_compare_acc_area,
       "../Section_2_3_Acc_compare.svg", 
       width = 22, 
       height = 16, 
       units = "cm",
       dpi=300)

ggsave(plot = plt_compare_acc_area,
       "../Section_2_3_Acc_compare.png", 
       width = 22, 
       height = 16, 
       units = "cm",
       dpi=300)










