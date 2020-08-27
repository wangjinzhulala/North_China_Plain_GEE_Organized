library(ggplot2)
library(tidyr)
library(dplyr)
library(cowplot)
library(stringr)
library(scales)

############################# Make plot that refelect one point's Fourier fitting ##########################

#________________________step 1: read data and format the df________________________

data.original_val = read.csv(paste("../../Process_3_Explore_Result/",
                                   "Result/",
                                   "Original_image_value.csv",sep=""),
                             stringsAsFactors = T) %>% 
                             mutate(Type='Original',time = as.Date(time)) %>% 
                             pivot_longer(cols = c(NDVI,NDBI,EVI),names_to = 'Index',values_to='val')

data.fitted_val = read.csv(paste("../../Process_3_Explore_Result/",
                                   "Result/",
                                   "Fitted_image_value.csv",sep=""),
                             stringsAsFactors = T)  %>% 
                             mutate(Type='Fitted',time = as.Date(time)) %>% 
                             pivot_longer(cols = c(NDVI,NDBI,EVI),names_to = 'Index',values_to='val')

data.original_fitted = rbind(data.fitted_val,data.original_val)


#________________________step 2: make plot of one point Fourier fitting________________________

p_3_1 = data.original_fitted %>% 
  group_by(Type) %>% 
  ggplot(aes(x=time,y=val,color=Type)) +
  geom_line() +
  facet_grid(Index~.,scale='free') +
  scale_x_date(minor_breaks = '1 month',
               breaks =  seq(as.Date("2017-01-01"), as.Date("2020-01-01"), by="6 months"), 
               date_labels = "%b\n%Y") +
  labs(x='Date',y= 'Value')

plt_one_fourier = p_3_1 +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        axis.line.x.bottom = element_line(),
        axis.line.y.left = element_line(),
        strip.background = element_rect(fill = NA,
                                        color = 'grey50'))

plt_one_fourier

############################# Make plot that refelect all point's Fourier fitting ##########################

#________________________step 1: read data and format the df________________________
data.original_10K = read.csv(paste("../../Process_3_Explore_Result/",
                                   "Result/",
                                   "Original_value.csv",sep=""),
                             stringsAsFactors = T) %>% 
  mutate(Date = as.Date(time),From = 'Original value')

data.fitted_10K = read.csv(paste("../../Process_3_Explore_Result/",
                                   "Result/",
                                   "Fitted_values.csv",sep=""),
                             stringsAsFactors = T) %>% 
  mutate(Date = as.Date(Date),From = 'Fourier fit')


# bind the values together
data.Fourier = rbind(data.original_10K %>% select(Date,From,Type,Index,value),
                     data.fitted_10K   %>% select(Date,From,Type,Index,value))



#________________________step 2: get subplots of each Type|Index Combination ________________________


# create a function to make plots

filter_fourier = function(df,x) {
    select_df = df %>% 
    dplyr::filter(Type == x[1]) %>% 
    dplyr::filter(Index == x[2])
    
    original_df = select_df %>% filter(From == 'Original value') %>% 
                                filter(value < 1) %>% 
                                filter(value > -1)
    fit_df = select_df %>% filter(From == 'Fourier fit')%>% 
                           filter(value < 1) %>% 
                           filter(value > -1)
    
    ggplot(original_df,aes(x=Date,y=value)) +
      # plot_1: raster of original values
      stat_density_2d(
        data =  original_df,
        geom = 'raster',
        aes(fill = after_stat(count)),
        contour = FALSE,
        show.legend = F) +
      # plot_2: ribbon of fit value
      stat_summary(
        data = fit_df,
        fun.data = 'mean_se',
        geom  ='ribbon',
        fill = '#F98179',
        alpha = 1/2) +
      # plot_3: line of fit value
      stat_summary(
        data = fit_df,
        fun  = 'mean',
        geom ='line',
        size = 3/5,
        color = '#F98179') +
      # expand to full panel
      scale_x_date(expand = c(0,0)) + 
      scale_y_continuous(expand = c(0,0)) +
      scale_fill_gradient(low = "white",
                          high = "black",
                          limits = c(0, 500), 
                          oob = scales::squish) +
      theme(plot.margin = margin(l=-0.5, b = -0.5,unit="cm"))}


# create a df that stores all From|Type|Index combinations and the correspoding plots
combo_df = expand.grid(unique(data.Fourier$Type),unique(data.Fourier$Index))

# using combo_df as parameters to make plots
plots = apply(combo_df,1,filter_fourier,df=data.Fourier)

# cmobine all plots into one
plt_fourier_fit = plot_grid(greedy = T,rel_widths = c(5,5),ncol = 2,align = 'hv',
          plots[[1]] + coord_cartesian(ylim = c(0,0.8)) + theme(axis.title.x = element_blank(),
                                                                axis.text.x  = element_blank(),
                                                                axis.ticks.x = element_blank()),
          
          plots[[2]] + coord_cartesian(ylim = c(0,0.8)) + theme(axis.title.x = element_blank(),
                                                                axis.text.x  = element_blank(),
                                                                axis.ticks.x = element_blank(),
                                                                axis.title.y = element_blank(),
                                                                axis.text.y  = element_blank(),
                                                                axis.ticks.y = element_blank()),
          
          plots[[3]] + coord_cartesian(ylim = c(-0.5,0.2)) + theme(axis.title.x = element_blank(),
                                                                axis.text.x  = element_blank(),
                                                                axis.ticks.x = element_blank()),
          
          plots[[4]] + coord_cartesian(ylim = c(-0.5,0.2)) + theme(axis.title.x = element_blank(),
                                                                axis.text.x  = element_blank(),
                                                                axis.ticks.x = element_blank(),
                                                                axis.title.y = element_blank(),
                                                                axis.text.y  = element_blank(),
                                                                axis.ticks.y = element_blank()),
          
          plots[[5]] + coord_cartesian(ylim = c(0,0.7)),
          
          plots[[6]] + coord_cartesian(ylim = c(0,0.7)) + theme(axis.title.y = element_blank(),
                                                               axis.text.y  = element_blank(),
                                                               axis.ticks.y = element_blank()))

#________________________step 3: save to disk ________________________

ggsave(plot = plt_fourier_fit,
       "../Section_3_1_Fourier_fit.svg", 
       width = 15, 
       height = 9, 
       units = "cm",
       dpi=300)

ggsave(plot = plt_fourier_fit,
       "../Section_3_1_Fourier_fit.png", 
       width = 15, 
       height = 9, 
       units = "cm",
       dpi=300)
