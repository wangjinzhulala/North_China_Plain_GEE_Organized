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
  stat_summary(aes(color='Accuracy(se)',group='Accuracy(se)'),
               fun = 'mean',
               geom = 'line') +
  stat_summary(aes(fill = 'Accuracy(se)',group='Accuracy(se)'),
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

#___Type_1_ribbon
p_1_6_2 = data.p_6_grid_acc %>% 
  filter(Tree==100) %>% 
  mutate(Year = str_replace(Year, "_", "-")) %>% 
  mutate(In_Bands = str_replace_all(In_Bands, "_", " + ")) %>% 
  mutate(In_Bands = str_replace_all(In_Bands, "Meterology", "Meteorology")) %>% 
  mutate(In_Bands = str_replace_all(In_Bands, "Spectrum", "Spectral")) %>% 
  mutate(In_Bands = str_replace_all(In_Bands, "Normalize", "Indices")) %>% 
  mutate(Accuracy = Accuracy *100) %>% 
  ggplot(aes(x=Year,y=Accuracy,group=In_Bands,color=In_Bands,fill=In_Bands)) +
  guides(fill = guide_legend(reverse = TRUE),color = guide_legend(reverse = TRUE))+
  stat_summary(fun = 'mean',geom = 'line') +
  stat_summary(fun.data = 'mean_se',
               geom = 'ribbon',
               alpha = 1/3,
               size=0.1,
               color='grey99') 
  
plt_inbands_acc_ribbon = p_1_6_2 + 
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.text.x = element_text(angle = 30,vjust = 0.5),
        axis.line.y.left = element_line(),
        legend.position = c(0.35, 0.59),
        legend.background = element_blank()) +
  ylab('Accuracy(%)') +
  labs(color = 'Input predictors',
       fill = 'Input predictors')

#___Type_2_bar

plt_inbands_acc_bar = data.p_6_grid_acc %>% 
  filter(Tree==100) %>% 
  mutate(Year = str_replace(Year, "_", "-")) %>% 
  mutate(In_Bands = str_replace_all(In_Bands, "_", " + ")) %>% 
  mutate(Accuracy = Accuracy *100) %>% 
  ggplot(aes(x=Year,y=Accuracy,fill = In_Bands)) +
  stat_summary(fun='mean',geom='bar',color='grey90',position = 'dodge') +
  coord_cartesian(ylim = c(80,97)) + 
  labs(fill = 'Input bands') +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line()) +
  scale_fill_viridis_d(option = 'D')

plt_inbands_acc_ribbon
plt_inbands_acc_bar

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
  stat_summary(aes(color='Accuracy(se)',group='Accuracy(se)'),
               fun = 'mean',
               geom = 'line') +
  stat_summary(aes(fill = 'Accuracy(se)',group='Accuracy(se)'),
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

ggsave(plot = plt_inbands_acc_bar,
       "../Section_1_6_2_In_bands_Accuracy.svg", 
       width = 30, 
       height = 8, 
       units = "cm",
       dpi=500)

ggsave(plot = plt_inbands_acc_bar,
       "../Section_1_6_2_In_bands_Accuracy.png", 
       width = 30, 
       height = 8, 
       units = "cm",
       dpi=500)



ggsave(plot = plt_inbands_acc_ribbon,
       "../Section_1_6_2_plt_inbands_acc_ribbon.svg", 
       width = 20, 
       height = 13, 
       units = "cm",
       dpi=800)

ggsave(plot = plt_inbands_acc_ribbon,
       "../Section_1_6_2_plt_inbands_acc_ribbon.png", 
       width = 20, 
       height = 13, 
       units = "cm",
       dpi=800)


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












data.p_6_grid_acc %>% 
  filter(Tree==100) %>% 
  mutate(Year = str_replace(Year, "_", "-")) %>% 
  mutate(In_Bands = str_replace_all(In_Bands, "_", " + ")) %>% 
  mutate(Accuracy = Accuracy *100) %>% 
  ggplot(aes(x=Year,y=Accuracy,fill = In_Bands)) +
  geom_bar(position = 'dodge',stat = 'identity',width = 0.5) +
  coord_cartesian(ylim = c(80,97)) + 
  labs(fill = 'Input bands') +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line())














