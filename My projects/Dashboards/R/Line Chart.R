library("ggplot2")
library("plyr")
library("reshape2")

line_df <- read.csv("C:/Users/user/Downloads/line_chart_data.csv",
                       header=TRUE,
                       sep=",")
line_df$Date <- as.Date(line_df$Date,
                        format = '%m/%d/%Y')

line_df <- melt(line_df, id.vars = "Date")

line_df <- rename(new_line_types,
                         c("value"="Returns",
                           "variable" = "index"))


line_chart <- ggplot (line_df,
                      aes(x=Date,
                          y= Returns,
                          color = index,
                          group = index
                          ))+
  geom_line(aes(color = index), size = 1)+
  scale_color_manual(values = c('navyblue', 'red4'))+
  theme_minimal()+
  ggtitle("S&P vs FTSE Returns")

line_chart

min <- as.Date('2008-7-1')
max <- as.Date('2008-12-31')


## New  CHART ## 
line_chart_2008 <- ggplot (line_df,
                      aes(x=Date,
                          y= Returns,
                          color = index,
                          group = index
                      ))+
  geom_line(aes(color = index), size = 1)+
  scale_color_manual(values = c('navyblue', 'red4'))+
  theme_minimal()+
  ggtitle("S&P vs FTSE Returns 2008")+
  scale_x_date(limits =c(min,max)) + 
  theme(legend.justification = c(0.01,1),
        legend.position = c(0.01,1))

line_chart_2008