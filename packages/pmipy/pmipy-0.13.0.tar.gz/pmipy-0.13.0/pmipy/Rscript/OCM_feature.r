args<-commandArgs(T)
file_name <- args[1]
tag <- args[2]

library(ggplot2)
dt <- read.csv(file_name)

#6:ncol(dt)
for (i in colnames(dt)[6:ncol(dt)]) {
  dt1 <- dt[, c('经度', '纬度', i)]
  dt2 <- dt1[is.na(dt1[,c(i)]), ]
  dt3 <- dt1[complete.cases(dt1),]
  # 去除0
  dt3 <- dt3[dt3[, c(i)] != 0, ]
  dt3 <- dt3[order(dt3[,c(i)]),]
  dt4 <- rbind(dt2, dt3)
  p <- ggplot(dt4, aes(经度, 纬度, colour=dt4[, c(3)])) + geom_point(size=0.5, alpha = 1) + theme_bw() 
  p + labs(colour='Value', title=paste(tag, '_', i)) + scale_colour_gradient(low="#4682B4", high="#8A2BE2", na.value='#EDEDED') +
    theme(plot.title=element_text(size=25, face='bold', hjust=0.5),
          axis.title.x = element_text(size=18), axis.title.y = element_text(size=18))
  ggsave(paste(tag, '/', tag, '_', i, '.png', sep=''), width = 9, height = 6)
}


# 将每个特征的值factor化
myfunction1 <- function(dt, feature){
  p <- ggplot(dt, aes(经度, 纬度))
  p + geom_point(aes(colour = factor(dt[, c(feature)]))) + theme_bw() + ggtitle(i) + labs(colour = i)
  ggsave(paste(tag, '/', tag, '_', feature, '_factor.png', sep=''))
}

# for (i in colnames(dt)[6:ncol(dt)]) {myfunction1(dt, i)}

