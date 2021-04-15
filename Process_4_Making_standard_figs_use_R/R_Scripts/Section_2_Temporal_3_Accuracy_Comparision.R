library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)
library(comprehenr)
library(ggpubr)


scientific_10 <- function(x) {
  parse(text=gsub("e", " %*% 10^", scales::scientific_format()(x)))
}


#________________________step 1: read data and format the df________________________

data.accuracy = read.csv(paste("../../Process_2_Temporal_Check/",
                                  "Result/",
                                  "Accuracy_comparision.csv",sep=""),
                            stringsAsFactors = T) %>% 
  mutate(Source = str_replace(Source, "My", "This study")) %>% 
  filter(year>=1990) %>% 
  filter((Source == 'This study') | (Source == 'GAIA')
         | (Source == 'GIS')| (Source == 'Global Landcover 30')) 




data.area_change = read.csv(paste("../../Process_2_Temporal_Check/",
                                  "Result/",
                                  "Area_change.csv",sep=""),
                            stringsAsFactors = T) 

#______________________step 2: make plot of area comparision________________________

data_2_3_point = data.area_change %>% 
  filter((Source == 'GHSL') |(Source == 'GIS')|(Source == 'Global Landcover 30'))%>% 
  group_by(year,Source) %>% 
  summarise(area = sum(area_km2)) %>% 
  mutate(Source = str_replace(Source,'GIS','Global Impervious Surface'))%>% 
  mutate(Source = str_replace(Source,'Global Landcover 30','GlobeLand30'))

data_2_3_line = data.area_change %>% 
  filter((Source != 'GHSL') & (Source != 'GIS') & (Source != 'GRUMP 1995')
         & (Source != 'Global Landcover 30')) %>% 
  group_by(year,Source) %>% 
  summarise(area = sum(area_km2)) %>% 
  mutate(Source = str_replace(Source, "My", "This study")) %>% 
  mutate(Source = str_replace(Source,'Global Urban He','Global Urban Expansion'))%>% 
  mutate(Source = str_replace(Source,'Global Urban Liu','Global Urban Dynamics'))%>% 
  mutate(Source = str_replace(Source,'MODIS','MCD12Q1'))

p_2_3 = ggplot( data = data_2_3_line, aes(x=year,y=area))  +
        geom_line(aes(color=Source),size=1) +
        geom_point(data = data_2_3_point,aes(fill=Source),shape=21,size=4) +
        scale_fill_manual(values = c('grey70','yellow','#4C886B')) 
         

plt_area_change_compare = p_2_3 +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        #axis.text.x.bottom = element_blank(),
        legend.position = c(0.32, 0.75),
        legend.key = element_rect(fill = NA ),
        legend.box = "vertival",
        legend.spacing.y = unit(-0.3, "cm"))+
  scale_y_continuous(breaks = seq(0,200000,25000),labels = seq(0,20,2.5)) +
  scale_x_continuous(breaks = seq(1980,2020,5),minor_breaks = seq(1980,2020,1))+
  guides(color = guide_legend(ncol = 1)) +
  labs(color = '',
       fill  = '',
       y = bquote('Area ('*10^5 ~km^2*')'),
       x = '')



plt_area_change_compare 

#______________________step 3: make plot of accuracy comparision________________________

data_2_4_point = data.accuracy %>% 
  filter((Source == 'GIS') |(Source == 'Global Landcover 30'))

data_2_4_line = data.accuracy %>% 
  filter((Source == 'GAIA') |(Source == 'This study'))

p_2_4 =  
  ggplot() +
  geom_line(data = data_2_4_line,  aes(x=year,y=Overall_ACC,color=Source),size=1) +
  geom_point(data = data_2_4_point,aes(x=year,y=Overall_ACC,fill=Source),shape=21,size=4) +
  expand_limits(x = c(1990,2020))


plt_acc_compare = p_2_4 +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        legend.position = c(0.20, 0.7),
        legend.key = element_rect(fill = NA ),
        legend.box = "vertical") +
  scale_x_continuous(breaks = seq(1990,2020,5) ) + 
  scale_color_manual(values=c('#B8A105','#F565E3'))+
  scale_fill_manual(values=c("#FFFF00","#4C886B")) +
  guides(color = guide_legend(ncol = 1)) +
  labs(color = '',
       fill  = '',
       x='Year',
       y='Accuracy (%)') 

plt_acc_compare

#______________________step 4: combine plot________________________


plt_compare_acc_area = ggarrange(plt_area_change_compare,
          plt_acc_compare, 
          align = 'v',
          ncol=1, 
          nrow=2, 
          common.legend = TRUE, 
          legend="right",
          labels = c('a)','b)'),
          label.x = 0.2,
          label.y = 0.7)

plt_compare_acc_area

#______________________step 5: save plot to disk________________________


ggsave(plot = plt_compare_acc_area,
       "../Section_2_3_Acc_compare.svg", 
       width = 19, 
       height = 12, 
       units = "cm",
       dpi=500)

ggsave(plot = plt_compare_acc_area,
       "../Section_2_3_Acc_compare.png", 
       width = 19, 
       height = 12, 
       units = "cm",
       dpi=500)









