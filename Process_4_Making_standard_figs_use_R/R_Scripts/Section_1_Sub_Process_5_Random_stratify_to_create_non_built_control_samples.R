library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)


#________________________step 1: read data and format the df________________________
data.p_5_NDVI_hist = read.csv(paste("../../Process_1_GEE_Python_Classification/",
                                    "Sub_Process_5_Random_stratify_to_create_non_built_control_samples/",
                                    "Result_df/",
                                    "NDVI_area_propotion.csv",sep=""),
                      stringsAsFactors = T)

# only chose the year of 2017-2019 and pivot the data to long format
data.p_5_NDVI_hist.long = data.p_5_NDVI_hist  %>% 
                              filter(Year_range == '2017_2019') %>% 
                              pivot_longer(col=-c(Year_range,NDVI),
                                           names_to = 'type',
                                           values_to = 'val') %>% 
                              mutate(type = case_when(
                                                      type == 'Freq' ~ 'NDVI',
                                                      type == 'Select_num' ~ 'Sample'
                              ))

#_________________step 2: plot the histogram of NDVI_____________________

p_1_5 = data.p_5_NDVI_hist.long  %>% 
  ggplot(aes(x=NDVI,y=val,fill=type)) +
  geom_bar(stat = 'identity') +
  scale_y_log10() +
  ylab('Counts')

plot = p_1_5 + 
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        legend.position = c(0.9, 0.8))


#_________________step 3: save plot to disk_____________________ 
plot

ggsave("../Section_1_5_Control_sample_NDVI_distribution.svg", 
       width = 14, 
       height = 8, 
       units = "cm",
       dpi=300)

ggsave("../Section_1_5_Control_sample_NDVI_distribution.png", 
       width = 14, 
       height = 8, 
       units = "cm",
       dpi=300)
  




