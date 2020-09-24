library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)
library(comprehenr)


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
  filter((Source == 'This study') | (Source == 'GAIA'))


data.area_change = read.csv(paste("../../Process_2_Temporal_Check/",
                                  "Result/",
                                  "Area_change.csv",sep=""),
                            stringsAsFactors = T) %>% 
  mutate(Source = str_replace(Source, "My", "This study")) 

#______________________step 2: make plot of area comparision________________________

data_2_3_point = data.area_change %>% 
  filter((Source == 'GHSL') |(Source == 'GIS'))%>% 
  group_by(year,Source) %>% 
  summarise(area = sum(area_km2)) %>% 
  mutate(point = Source)

data_2_3_line = data.area_change %>% 
  filter((Source != 'GHSL') & (Source != 'GIS') & (Source != 'GRUMP 1995')) %>% 
  group_by(year,Source) %>% 
  summarise(area = sum(area_km2)) %>% 
  mutate(line = Source)

p_2_3 = ggplot( data = data_2_3_line, aes(x=year,y=area))  +
  geom_line(aes(color=Source),size=1) +
    geom_point(data = data_2_3_point,
             aes(fill=Source),shape=21,size=4) +
  scale_y_continuous(labels = comma) +
  scale_fill_manual(values = c('grey70','yellow')) 
         

plt_area_change_compare = p_2_3 +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        #axis.text.x.bottom = element_blank(),
        legend.position = c(0.32, 0.75),
        legend.key = element_rect(fill = NA ),
        legend.box = "horizontal")+
  scale_y_continuous(breaks = seq(0,200000,25000),labels = seq(0,20,2.5)) +
  scale_x_continuous(breaks = seq(1980,2020,5),minor_breaks = seq(1980,2020,1))+
  guides(color = guide_legend(ncol = 2)) +
  labs(color = '',
       fill  = '',
       y = bquote('Area ('*10^5 ~km^2*')'),
       x = '')



plt_area_change_compare 

#______________________step 3: make plot of accuracy comparision________________________

p_2_4 = data.accuracy %>% 
  ggplot(aes(x=year,y=Overall_ACC,color=Source,group=Source)) +
  geom_point(shape=1) +
  geom_line(show.legend = F) +
  expand_limits(x = c(1990,2020))



plt_acc_compare = p_2_4 +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        legend.position = c(0.13, 0.55),
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
       width = 20, 
       height = 16, 
       units = "cm",
       dpi=300)

ggsave(plot = plt_compare_acc_area,
       "../Section_2_3_Acc_compare.png", 
       width = 20, 
       height = 16, 
       units = "cm",
       dpi=300)









