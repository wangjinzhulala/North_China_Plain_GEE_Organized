library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)
library(comprehenr)

################################## Read the accuracy from original/10folds-correc ##########################

# determine the year_range column
year = seq(1990,2017,3)
year_range = to_vec(for(yr in year) paste(toString(yr),
                                          '-',
                                          toString(yr+2),sep = ''))

#________________________________read data, using pate to concat long file path string__________________________________________
data.acc_my = read.csv(paste("../../Process_2_Temporal_Check/",
                                  "Result/",
                                  "My_acc.csv",sep=""),
                            stringsAsFactors = T) %>% 
  mutate(type='My',year_range = year_range)

data.acc_GAIA = read.csv(paste("../../Process_2_Temporal_Check/",
                             "Result/",
                             "GAIA_acc.csv",sep=""),
                       stringsAsFactors = T)%>% 
  mutate(type='GAIA',year_range = year_range)




# combine two accuracy-df together
data.acc = rbind(data.acc_my,data.acc_GAIA)


# make the plot
data.acc %>% 
  select(type,year_range,Overall_ACC) %>% 
  ggplot(aes(x=year_range,y=Overall_ACC,color=type,group = type))+
  geom_line() +
  labs(x='Year Range',y='Overall Accuracy') +
  theme(axis.text.x = element_text(angle = 20,vjust = 0.4))


