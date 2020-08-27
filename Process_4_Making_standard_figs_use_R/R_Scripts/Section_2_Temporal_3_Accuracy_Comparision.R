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



# make #______________________step 2: make plot________________________

p_2_3 = data.accuracy %>% 
  select(Type,year,Overall_ACC) %>% 
  ggplot(aes(x=year,y=Overall_ACC,color=Type,group=Type)) +
  geom_line(size=1) +
  geom_point(size=1.5) 



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
       x='Year Range',
       y='Accuracy') 



#______________________step 3: save plot to disk________________________
plt_acc_compare

ggsave(plot = plt_acc_compare,
       "../Section_2_3_Acc_compare.svg", 
       width = 22, 
       height = 12, 
       units = "cm",
       dpi=300)

ggsave(plot = plt_acc_compare,
       "../Section_2_3_Acc_compare.png", 
       width = 22, 
       height = 12, 
       units = "cm",
       dpi=300)










