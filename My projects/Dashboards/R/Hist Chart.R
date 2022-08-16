library("ggplot2")
library("plyr")
library("reshape2")

hist_df <- read.csv("C:/Users/user/Downloads/histogram_data.csv",
                    header=TRUE,
                    sep=",")


hist_chart <- ggplot (hist_df,
                      aes(x=Price
                          
                                ))+
  geom_histogram(bins=8, 
                 fill = '#108a99', 
                 color='white')+
  theme_classic()+
  ggtitle("Distribution Real Estate Price") +
  xlab('Price (000$)')+
  ylab('Number of Properties')+
  theme(plot.title = element_text(size = 16, face = 'bold'))

hist_chart
