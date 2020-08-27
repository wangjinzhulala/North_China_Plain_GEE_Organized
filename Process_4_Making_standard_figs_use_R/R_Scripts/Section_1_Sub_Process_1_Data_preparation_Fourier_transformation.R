library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)

#________________________step 1: read data and format the df________________________

data.p_1_1 = read.csv(paste("../../Process_1_GEE_Python_Classification/",
                            "Sub_Process_1_Data_preparation_Fourier_transformation/",
                            "Reuslt/",
                            "Residule_with_col_names.csv",sep=""),
                      stringsAsFactors = T)

# change 'Span' and 'Harmonic' to factor
data.p_1_1 = data.p_1_1 %>% 
  mutate(Span = as.factor(data.p_1_1$Span),
         Harmonic = as.factor(data.p_1_1$Harmonic) )



#_________________step 2: make a boxplot of Harmonic~Mean_Err_____________________

p_harmonic = data.p_1_1 %>% 
  ggplot(aes(x=Harmonic,y=Mean_Err)) +
  stat_boxplot(geom ='errorbar',width = 0.5,color='#CAA1A0') +
  geom_boxplot(outlier.size = 0.8, 
               outlier.alpha = 0.6,
               outlier.shape = 1,
               width = 0.5,
               size=0.3) +
  stat_summary(fun = 'median',
               geom='line',
               group=1,
               size=0.5,
               color = '#507DA7') +
  ylab('Mean Error')+
  xlab('Harmonic numbers')

p_harmonic_themed = p_harmonic + 
  scale_y_continuous(breaks = seq(0,200,20)) +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line())


#_________________step 2: make a boxplot of Harmonic~Mean_Err_____________________

# make a boxplot of Span~Mean_Err (650*400)
p_span = data.p_1_1 %>% 
  filter(Harmonic==3) %>% 
  ggplot(aes(x=Span,y=Mean_Err)) +
  stat_boxplot(geom ='errorbar',width = 0.25,color='#CAA1A0') +
  geom_boxplot(outlier.size = 0.8, 
               outlier.alpha = 0.6,
               outlier.shape = 1,
               width = 0.25,
               size=0.3)+
  stat_summary(fun = 'median',
               geom='line',
               group=1,
               size=0.5,
               color = '#507DA7') +
  ylab('Mean Error')+
  xlab('Stack Years')

p_span_themed = p_span + 
  scale_y_continuous(breaks = seq(0,200,20)) +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line())


#_________________step 3: combine the two plots together_____________________

p_harmonic_themed
p_span_themed

plot  = plot_grid(label_x = 0.5,
          label_y = 0.9,
          p_harmonic_themed,
          p_span_themed,
          nrow = 2,
          rel_widths = c(1,1),
          labels = c('a)','b)'),
          label_size = 12,
          label_fontface = 'plain')

ggsave("../Section_1_1_Harmonic_Span.svg", 
       width = 14, 
       height = 16, 
       units = "cm",
       dpi=300)

ggsave("../Section_1_1_Harmonic_Span.png", 
       width = 14, 
       height = 16, 
       units = "cm",
       dpi=300)













