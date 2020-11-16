library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)
library(comprehenr)
library(stringr)


#________________________step 1: read data and format the df________________________
data.area_change = read.csv(paste("../../Process_2_Temporal_Check/",
                                   "Result/",
                                   "Area_change.csv",sep=""),
                             stringsAsFactors = T)%>% 
  mutate(year = paste0((year-1),'-',(year+1)))




#______________________step 2: make plot of area change of my study________________________
p_2_2 = data.area_change %>% 
  mutate(area = sum*30*30/1000/1000) %>% 
  filter(Source == 'My') %>% 
  ggplot(aes(x=year,y=area,color=EN_Name,group=EN_Name)) +
  geom_line(size=0.5) +
  geom_point(size=1.5) +
  scale_color_hue()

plt_area_change = p_2_2 +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        legend.position = c(0.13, 0.73),
        legend.key = element_rect(fill = NA )) +
  scale_y_continuous(breaks = seq(0,200000,5000),labels = seq(0,20,0.5)) +
  labs(color = '',
       fill  = '',
       y = bquote('Area ('*10^5 ~km^2*')'),
       x = 'Year')





#______________________step 4: save plot to disk________________________
plt_area_change

ggsave(plot = plt_area_change,
       "../Section_2_2_Area_change.svg", 
       width = 20, 
       height = 10, 
       units = "cm",
       dpi=500)

ggsave(plot = plt_area_change,
       "../Section_2_2_Area_change.png", 
       width = 20, 
       height = 10, 
       units = "cm",
       dpi=500)



