library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)


#________________________step 1: read data and format the df________________________
data.p_6_grid_acc = read.csv(paste("../../Process_1_GEE_Python_Classification/",
                                    "Sub_Process_6_Before_classification_Feature_selection/",
                                    "Result/",
                                    "Grid_acc_tree.csv",sep=""),
                              stringsAsFactors = T)


#_________________step 2: plot Acc~Tree_____________________

p_1_6_1 = data.p_6_grid_acc %>% 
  filter(In_Bands == 'Spectrum_Normalize_Fourier_Terrain_Meterology') %>% 
  mutate(Accuracy = Accuracy *100) %>% 
  ggplot(aes(x=Tree,y=Accuracy)) +
  stat_summary(aes(color='Accuracy(sd)',group='Accuracy(sd)'),
               fun = 'mean',
               geom = 'line') +
  stat_summary(aes(fill = 'Accuracy(sd)',group='Accuracy(sd)'),
               fun.data = 'mean_se',
               geom = 'ribbon',
               alpha = 1/3)+
  scale_color_manual(values = c('#3081BA')) +
  scale_fill_manual(values = c('#3081BA')) +
  scale_x_continuous(breaks = seq(0,120,20)) +
  labs(color = "", 
       fill  = "",
       y = 'Accuracy (%)')

plt_ACC_Tree = p_1_6_1 +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        legend.position = c(0.83, 0.7))


plt_ACC_Tree

#_________________step 3: plot In_bands~ACC_____________________

p_1_6_2 = data.p_6_grid_acc %>% 
  filter(Tree==100) %>% 
  mutate(Year = str_replace(Year, "_", "-")) %>% 
  mutate(In_Bands = str_replace_all(In_Bands, "_", " + ")) %>% 
  mutate(Accuracy = Accuracy *100) %>% 
  ggplot(aes(x=Year,y=Accuracy,group=In_Bands,color=In_Bands,fill=In_Bands)) +
  stat_summary(fun = 'mean',geom = 'line') +
  stat_summary(fun.data = 'mean_se',
               geom = 'ribbon',
               alpha = 1/3,
               size=0.1,
               color='grey99') 
  
plt_inbands_acc = p_1_6_2 + 
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        legend.position = c(0.3, 0.57)) +
  labs(color = 'Accuracy and Standard Deviation',
       fill = 'Accuracy and Standard Deviation')

plt_inbands_acc


#_________________step 3: plot In_Size~ACC_____________________

data.p_6_sample_size = read.csv(paste("../../Process_1_GEE_Python_Classification/",
                                   "Sub_Process_6_Before_classification_Feature_selection/",
                                   "Result/",
                                   "Sample_size_acc.csv",sep=""),
                             stringsAsFactors = T)

# filter the accuracy from test and make plot
p_1_6_3 = data.p_6_sample_size %>% 
  filter(Acc_type == 'acc_test') %>% 
  mutate(Acc_value = Acc_value *100) %>% 
  group_by(Size) %>% 
  ggplot(aes(x=Size,y=Acc_value)) +
  stat_summary(aes(color='Accuracy(sd)',group='Accuracy(sd)'),
               fun = 'mean',
               geom = 'line') +
  stat_summary(aes(fill = 'Accuracy(sd)',group='Accuracy(sd)'),
               fun.data = 'mean_se',
               geom = 'ribbon',
               alpha = 1/3)+
  scale_color_manual(values = c('#3081BA')) +
  scale_fill_manual(values = c('#3081BA')) +
  scale_x_continuous(breaks = seq(0,101,15))

plt_ACC_Size = p_1_6_3 + 
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        legend.position = c(0.83, 0.7)) +
  labs(color = '',
       fill  = '',
       y = 'Accuracy (%)',
       x = 'Size(%)')

plt_ACC_Size

#_____________step 4: Arrange to combine Size_acc and Tree_acc together____________

plot  = plot_grid(plt_ACC_Tree,
                  plt_ACC_Size,
                  nrow = 2,
                  rel_widths = c(1,1),
                  labels = c('a)','b)'),
                  label_x = 0.5,
                  label_y = 0.8,
                  label_size = 12,
                  label_fontface = 'bold')

plot

#_____________step 5: save plots to disk____________

ggsave(plot = plt_inbands_acc,
       "../Section_1_6_2_In_bands_Accuracy.svg", 
       width = 30, 
       height = 15, 
       units = "cm",
       dpi=300)

ggsave(plot = plt_inbands_acc,
       "../Section_1_6_2_In_bands_Accuracy.png", 
       width = 35, 
       height = 15, 
       units = "cm",
       dpi=300)


ggsave(plot = plot,
       "../Section_1_6_1_Tree_Size_Accuracy.svg", 
       width = 14, 
       height = 16, 
       units = "cm",
       dpi=300)

ggsave(plot = plot,
       "../Section_1_6_1_Tree_Size_Accuracy.png", 
       width = 14, 
       height = 16, 
       units = "cm",
       dpi=300)




