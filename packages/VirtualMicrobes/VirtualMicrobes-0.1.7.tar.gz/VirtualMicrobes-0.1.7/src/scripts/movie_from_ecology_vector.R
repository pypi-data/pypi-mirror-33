### 	HOW TO USE 	###
# Launch R in terminal 	#
# Source this file in R #
# Enter filename	#
# Enter playback speed	#

library("optparse")

option_list = list(
  make_option(c("-n", "--nrsteps"), type="integer", default=100, 
              help="Number of steps to plot."),
  
  make_option(c("-f", "--file"), type="character", default="clustering.pdf", 
              help="save file name", metavar="character")
); 

opt_parser = OptionParser(option_list=option_list);
opts = parse_args(opt_parser);

file = opts$file
n = opts$nrsteps
X11()

#file = file.choose()
#n <- readline(prompt="Enter n for every nth line you want to plot (i.e. \"playback speed\") ")
#n <- as.integer(n)
cat("Now loading file...\n")
#x=read.csv(file, row.names=1, fill=TRUE)
x=read.table(file, row.names=1, sep=",", fill=TRUE)
cat("... done!\n\n")

maxx=max(x,na.rm=TRUE)
maxx=maxx*1.5
minx=min(x,na.rm=TRUE)
#minx=minx*1.01
#maxx=floor(maxx)
cat(paste("Setting max-x to ", maxx))
cat('\n')
cat(length(x))
refhist = hist(as.numeric(x[length(x[,1]),], breaks=seq(0,maxx,l=maxx)))
maxy = mean(refhist$counts)
maxy = maxy*1.5
cat(paste("\tSetting max-y to ", maxy))
cat("\n")

for( i in seq(0, length(x[,1]), by=n))
{
	hist(as.numeric(x[i,]), breaks=seq(minx,maxx,l=1000), xlim=c(minx,maxx), ylim=c(0,maxy), main=rownames(x[i,]))
}
