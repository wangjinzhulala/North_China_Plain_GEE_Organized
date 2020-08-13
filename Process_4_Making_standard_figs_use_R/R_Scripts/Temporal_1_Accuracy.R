library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)

################################## Read the accuracy from original/10folds-correc ##########################

#________________________________read data, using pate to concat long file path string__________________________________________
data.p_8_original = read.csv(paste("../../Process_1_GEE_Python_Classification/",
                                   "Sub_Process_8_Determine_the_threshold_for_the_sum_of_10_random_classification/",
                                   "Result/",
                                   "Threshold_acc_df.csv",sep=""),
                             stringsAsFactors = T)


# rearrange the year column se we get 'year_range' and type of 'landsat/sentinel'
data.p_8 = data.p_8_original[, !(colnames(data.p_8_original) %in% c("Feature"))]

data.p_8 = data.p_8 %>% 
  separate(col = Year,into = c('type','start','end'),sep = '_') %>% 
  unite(col = year_range, start,end,sep='-') %>% 
  filter(  !(type =='Landsat'& year_range %in%  c('2014-2016','2017-2019')))


#____________________________Make the figure to show threshold == 5 is optimum____________________________________________

data.p_8 %>% 
  ggplot(aes(x=Threshold,y=Accuracy,group=Threshold))+
  geom_boxplot() +
  scale_x_continuous(breaks = seq(0, 10))




#____________________________read the data of accuracy without threshold correction____________________________________________
# read data, using pate to concat long file path string
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

# mutate the df so we can get 'Sentinel/Landsat' and 'Year range' seperately
data.p_7_acc_landsat = data.p_7_acc_landsat %>% 
  separate(col = year, into = c('type','start','end'),sep = '_') %>% 
  unite(col = year_range, start,end,sep='-')


data.p_7_acc_sentinel = data.p_7_acc_sentinel %>% 
  separate(col = year, into = c('type','start','end'),sep = '_') %>% 
  unite(col = year_range, start,end,sep='-')


# concat two df together and make figure
data.p_7 = rbind(data.p_7_acc_landsat,data.p_7_acc_sentinel)

data.p_7 = data.p_7 %>% 
  filter(  !(type =='Landsat'& 
               year_range %in%  c('2014-2016','2017-2019')) 
  )




#______________________Make the plot to show each accuracy change with year_range________________________________


data.p_8 %>% 
  ggplot(aes(x=Threshold,y=Accuracy,color = year_range)) +
  geom_line()


############################# Making fig for temporal check ############################################

#________________________________read data, using pate to concat long file path string__________________________________________
data.temporal_1 = read.csv(paste("../../Process_2_Temporal_Check/",
                                   "Result/",
                                   "Temporal_check_acc.csv",sep=""),
                             stringsAsFactors = T) %>% 
  filter(!Mode == 0) %>% mutate(year = str_replace(year, pattern = '_',replacement = '-'))


#_____________________________ make figures ________________________
data.temporal_1  %>% 
  filter(Mode == 'only_forward') %>% 
  ggplot(aes(x=Iteration,y=Accuracy))+
  stat_summary(fun = 'mean',geom = 'line',color='#4990C2') +
  stat_summary(fun.data = 'mean_se',geom = 'ribbon',alpha=1/5,fill='#4990C2') +
  scale_x_continuous(breaks = seq(1,10))

data.temporal_1 %>% 
  filter(Mode == 'only_forward', 
         Iteration == 9) %>% 
  ggplot(aes(x=Window,y=Accuracy))+
  stat_summary(fun = 'mean',geom = 'line',color='#4990C2') +
  stat_summary(fun.data = 'mean_se',geom = 'ribbon',alpha=1/5,fill='#4990C2')+
  scale_x_continuous(breaks = seq(2,6))


#______________Make the plot comparing original/10-folds/temporal-corrected accuracy________________

data.tempral_filter = data.temporal_1 %>% 
  filter(Window == 3,
         Iteration == 9,
         Mode == 'only_forward')


data.p_8 %>% 
  filter(Threshold == 5)   %>% 
  ######## 10-folds correction accuracy
  ggplot(aes(x=year_range,
             y=Accuracy,
             group='10-folds corrections',
             color = '10-folds corrections')) +
  geom_line() +
  ######## Original accuracy
  stat_summary(data = data.p_7,
               mapping = aes(x=year_range, y=Overall_ACC),
               fun.data  = 'mean_se',
               geom= 'ribbon',
               alpha = 1/10,
               color = 'grey95',
               fill = "#FF9D47") +
  stat_summary(data = data.p_7,
               mapping = aes(x=year_range,y=Overall_ACC,color = 'Original'),
               fun = 'mean',
               geom= 'line') +
  ######## temporal correction accuracy
  geom_line(data = data.tempral_filter,
            mapping = aes(x=year,y=Accuracy,color = 'Temporal'))  +
  scale_color_manual(name="", values = c("#3282BA","#FF9D47","#3DA83D")) +
  labs(x='Year Range') +
  theme(axis.text.x = element_text(angle = 18,vjust = 0.6))





