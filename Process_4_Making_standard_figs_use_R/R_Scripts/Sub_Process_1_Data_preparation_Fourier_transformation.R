library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)


# read data, using pate to concat long file path string
data.p_1_1 = read.csv(paste("../../Process_1_GEE_Python_Classification/",
                            "Sub_Process_1_Data_preparation_Fourier_transformation/",
                            "Reuslt/",
                            "Residule_with_col_names.csv",sep=""),
                      stringsAsFactors = T)

# change 'Span' and 'Harmonic' to factor
data.p_1_1 = data.p_1_1 %>% 
  mutate(Span = as.factor(data.p_1_1$Span),
         Harmonic = as.factor(data.p_1_1$Harmonic) )




# make a boxplot of Harmonic~Mean_Err (650*400)
data.p_1_1 %>% 
  ggplot(aes(x=Harmonic,y=Mean_Err)) +
  geom_boxplot()+
  ylab('Mean Error')


# make a boxplot of Harmonic~Mean_Err wraped by Sensor~Index (650*800)
data.p_1_1 %>% 
  ggplot(aes(x=Harmonic,y=Mean_Err)) +
  geom_boxplot()+
  facet_wrap(Sensor~Index,scales = 'free') +
  ylab('Mean Error')




















