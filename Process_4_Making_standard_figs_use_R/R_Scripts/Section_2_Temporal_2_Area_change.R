library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)
library(comprehenr)


#________________________step 1: read data and format the df________________________
data.area_change = read.csv(paste("../../Process_2_Temporal_Check/",
                                   "Result/",
                                   "Area_change.csv",sep=""),
                             stringsAsFactors = T)


#______________________step 2: make plot________________________
p_2_2 = data.area_change %>% 
  mutate(area = sum*30*30/1000/1000) %>% 
  filter(Type == 'My') %>% 
  ggplot(aes(x=year,y=area,color=EN_Name,group=EN_Name)) +
  geom_line(size=1) +
  geom_point(size=1.5) +
  scale_color_hue()

plt_area_change = p_2_2 +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        legend.position = c(0.15, 0.7),
        legend.key = element_rect(fill = NA ))+
  labs(color = '',
       fill  = '',
       y = 'Area (km2)',
       x = 'Year')

#______________________step 3: save plot to disk________________________
plt_area_change

ggsave(plot = plt_area_change,
       "../Section_2_2_Area_change.svg", 
       width = 20, 
       height = 10, 
       units = "cm",
       dpi=300)

ggsave(plot = plt_area_change,
       "../Section_2_2_Area_change.png", 
       width = 20, 
       height = 10, 
       units = "cm",
       dpi=300)



