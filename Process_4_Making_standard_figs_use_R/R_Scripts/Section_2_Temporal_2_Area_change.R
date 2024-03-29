library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)
library(comprehenr)
library(stringr)
library(ggpubr)


#________________________step 1: read data and format the df________________________
#___1) area change data
data.area_change = read.csv(paste("../../Process_2_Temporal_Check/",
                                   "Result/",
                                   "Area_change.csv",sep=""),
                             stringsAsFactors = T)%>% 
  mutate(year = paste0((year-1),'-',(year+1)))


#___2) area percent_change_to_begining_year data
data.area_change_percent = read.csv(paste("../../Process_2_Temporal_Check/",
                                  "Result/",
                                  "Area_change_percent.csv",sep=""),
                            stringsAsFactors = T)%>% 
  mutate(year = paste0((year-1),'-',(year+1)))

#___3) area percent_to_total_area_each_region data
data.area_change_to_total_area = read.csv(paste("../../Process_2_Temporal_Check/",
                                          "Result/",
                                          "Area_percet_change_each_region.csv",sep=""),
                                    stringsAsFactors = T)%>% 
  mutate(year = paste0((year-1),'-',(year+1)))


#______________________step 2: make plot of area change of my study________________________
p_2_2 = data.area_change %>% 
  mutate(area = sum*30*30/1000/1000) %>% 
  filter(Source == 'My') %>% 
  ggplot(aes(x=year,y=area,color=EN_Name,group=EN_Name)) +
  geom_line(size=0.5) +
  geom_point(size=1.5) +
  scale_color_discrete(breaks=c("Shandong","Henan","Hebei","Anhui","Jiangsu","Beijing","Tianjin"))

p_2_2_pct = data.area_change_percent %>% 
  ggplot(aes(x=year,y=Percent.comparasion,color=EN_Name,group=EN_Name)) +
  geom_line(size=0.5) +
  geom_point(size=1.5) +
  scale_color_discrete(breaks=c("Shandong","Henan","Hebei","Anhui","Jiangsu","Beijing","Tianjin"))

p_2_2_total_region_portion = data.area_change_to_total_area %>% 
  ggplot(aes(x=year,y=Proportion_total,color=EN_Name,group=EN_Name)) +
  geom_line(size=0.5) +
  geom_point(size=1.5) +
  scale_color_discrete(breaks=c("Shandong","Henan","Hebei","Anhui","Jiangsu","Beijing","Tianjin"))

plt_area_change = p_2_2 +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.text.x = element_blank(), # remove x-axis text 
        axis.line.y.left = element_line(),
        legend.position = c(0.13, 0.75),
        legend.key = element_rect(fill = NA ),
        legend.background = element_blank()) +
  scale_y_continuous(breaks = seq(0,200000,5000),labels = seq(0,20,0.5)) +
  labs(color = '',
       fill  = '',
       y = bquote('Area ('*10^5 ~km^2*')'),
       x = '') + # remove x label 
  guides(colour = guide_legend(nrow = 1))

plt_area_change_pct = p_2_2_pct +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.text.x = element_blank(),
        axis.line.y.left = element_line(),
        legend.position = c(0.13, 0.75),
        legend.key = element_rect(fill = NA ),
        legend.background = element_blank()) +
  labs(color = '',
       fill  = '',
       y = 'Percent (%)',
       x = '')

plt_area_pct_to_region = p_2_2_total_region_portion +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.text.x = element_text(angle = 30, vjust = 0.5),
        axis.line.y.left = element_line(),
        legend.position = c(0.13, 0.75),
        legend.key = element_rect(fill = NA ),
        legend.background = element_blank()) +
  labs(color = '',
       fill  = '',
       y = 'Built-up area proportion  (%)',
       x = 'Year')

plt_area_pct = ggarrange(plt_area_change,
                         plt_area_pct_to_region,
                         align = 'v',
                         ncol=1, 
                         nrow=2, 
                         common.legend = TRUE, 
                         legend="bottom",
                         labels = c('a)','b)'),
                         label.x = 0.15,
                         label.y = 0.9)


#______________________step 4: save plot to disk________________________
plt_area_pct 

ggsave(plot = plt_area_pct,
       "../Section_2_2_Area_change.svg", 
       width = 19, 
       height =15, 
       units = "cm",
       dpi=500)

ggsave(plot = plt_area_pct,
       "../Section_2_2_Area_change.png", 
       width = 19, 
       height =15, 
       units = "cm",
       dpi=500)



