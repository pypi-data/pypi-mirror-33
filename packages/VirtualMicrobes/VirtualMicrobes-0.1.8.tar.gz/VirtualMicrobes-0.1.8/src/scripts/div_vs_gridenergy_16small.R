### 	HOW TO USE 	###
# plots Average energy left on gridpoints vs diversity of the ecosystem. 
# Takes 3 obligatory and 1 optional arguments: 
# required: (1) folder (2) plotting interval (3) annotate pump counts
# optional: (4) sav to save to PNG in home folder

args <- commandArgs(trailingOnly = TRUE)
print(args)
file <- args[1]
n <- as.numeric(args[2])
print(n)
if(length(args)> 2 && args[3] == "annotate") {
  annotate <- TRUE
} else { annotate <- FALSE}

if(length(args) > 3){
  
}

cat("\n")
cat("Plotting avg energy on gridpoints vs ecosystem diversity for:", "\n")
cat(file, "\n")
cat("interval size:",n, "\n")
# 
# 
# args <-"/hosts/linuxhome/mutant26/tmp/jeroen/ha_death_fluct0_bas0.03_prodprot_pseed41"
# annotate <- TRUE
# n=1

## Functions ####

# Returns Shannon's diversity index for a given vector of fractions 
shannondiversity = function(myvector){
  
  myvector <- myvector[!is.na(myvector)] # remove NA values
  myvector <- as.vector(myvector[myvector>0]) # remove items that are zero
  
  D <- 0
  d <- 0 
  for (i in 1:length(myvector)) {
    Pi = myvector[i]  
    d = Pi*log(Pi)
    D = D + d
  }
  return(-D)
}

# reads text file line for line, and returns the part indicated by 'begin' and 'end' 
# n.b. empty line is recognised as end by default
readtext <- function(filepath, begin, end, stopblankline = TRUE) {
  con = file(filepath, 'r')
  mytext <- vector()
  savtext <- FALSE # indicates whether lines should be saved or not
  
  while( TRUE ) {
    line = readLines(con, n = 1)
    
    if(savtext == TRUE){
      mytext <- c(mytext, line)
    }
    
    # look for begin 
    if (grepl(begin, line)) {
      #cat("Found beginning...", "\n")
      savtext <- TRUE
    }
    
    if (grepl(end, line)) {
      #cat("...and end, finished reading")
      savtext <- FALSE
      break
    }
    
    if (savtext == TRUE && line == "" && stopblankline == TRUE) {
      #cat("... and a blank line, finished reading", "\n")
      #cat("Don't want to end at a blank line? set 'stopblankline' to false")
      savtext <- FALSE
      break
    }
  }
  close(con)  
  return(mytext)
}

# Zoek metabolites in 'log.out' in het stuk tussen 'transport' en 'tox' 
getmetabs <- function(text) {
  
  # pak de metabolites
  metabolites <- sort(unlist(unique(regmatches(text, regexec("[A-Z]\\([0-9]", text)))))
  metabs <- substr(metabolites, 1, 1)
  values <- substr(metabolites, 3, 3)
  # pak de energy metabolites
  energy <- sort(unlist(unique(regmatches(text, regexec("[A-Z]\\*\\([0-9]", text)))))
  metabs <- c(metabs, substr(energy, 1, 1))
  values <- c(values, substr(energy, 4, 4))
  # stop ze in een data frame
  return(data.frame(metabs, as.numeric(values), stringsAsFactors = FALSE))
}

# gets metabolite types from a piece of text
gettypes<-function(text){
  # look in the log.out file between 'toxcities' and 'degradation rates' to get the
  # metabolite classes: energy*, {influx}, [building block], intermediate)
  # as these are listed in alphabetical order, we can just cbind them to our data frame
  types <- sort(unlist(unique(regmatches(text, regexec("[a-z]\\.0*.", text)))))
  types <- substr(types, 4, 4)
  types <- sub("}", "influx", types)
  types <- sub("\\*", "energy", types)
  types <- sub(" ", "intermediate", types)
  types <- sub("]", "building block", types) # don't sub these before intermediate :)
  return(types)
}


# makes a filename from a directory
makename <- function(dir, affix){
  # output name is: ~/mu<mutant nr>_<basename of the dir>_<affix>  
  mutant.index <- regexpr("(+|^)mutant($|[^a-zA-Z])|([^a-z]+|^)vit e($|[^a-zA-Z])", dir)  
  mutant.index <- regexpr("mutant[0-9]+", dir)
  mutant.name <- substr(args[1], mutant.index[1]+ 6, mutant.index[1] + attr(mutant.index,"match.length"))    
  mutant.name <- paste0("mu", sub("/$", "", mutant.name))                                                                 # remove last character if this is is a "/" (otherwise illegal pdfName))
  
  dir.name <- basename(dir)              
  
  if(missing(affix)) {
    name <- paste0("~/", mutant.name, "_", dir.name)
  } else { 
    name <- paste0("~/", mutant.name, "_", dir.name, "_", affix)
    }
  
  return(name)
}


#plots energy left on the grid as a function of diversity
plotenvsdiv <- function (div, energy, n = 1, main = main, label, xaxt = 's', yaxt = 's', cex = 1)
{
  plot(div, energy, type = 'n', xlim = c(0, xmax), ylim = c(0, ymax), ylab = '', xlab = '', xaxt = xaxt, yaxt = yaxt)
  prevlabel <- 0
  abline(v = seq(0, xmax), lty = 3, col = 'grey')
  abline(h = seq(0, ymax), lty = 3, col = 'grey')
  mtext(main, side = 3, line = -1.5)
  #text(div[1], energy[1], label = import$logo[1], cex = 0.8)
  col <- rainbow(length(div), end = 0.8)
  
  #main part: draw div vs energy
  for( i in seq(1, length(div), by = n)){
    text(div[i], energy[i], label = label[i], col = col[i], cex = cex) 
  }
  
  # add annotation for change in pump count
  if(annotate == TRUE) {
    for( i in seq(1, length(div), by = n))
    {
      if (label[i] < prevlabel) {
        #points(div[i], energy[i], pch = 20, col = col[i], cex = 3) 
        text(div[i], energy[i], label = "-", col = 'black', cex = 1.3, font = 2) 
        
      } else if (label[i] > prevlabel){
        #points(div[i], energy[i], pch = 20, col = col[i], cex = 3) 
        text(div[i], energy[i], label = "+", col = 'black', cex = 1.3, font = 2) 
      }  
      prevlabel <- label[i]
    }
  }
}






affix <- "diven"
if(annotate){affix <- paste0("annotated", "_", affix)}
name <- makename(args[1], affix)


# Load data ####
cat("Now loading files...\n")

## Filenames
# list of grid concentration filenames
filenames <- list(ecology = list.files(paste0(args[1], "/data/ecology_dat")))
filenames$ecology <- filenames$ecology[grep("^concentration", filenames$ecology, perl = TRUE)]
filenames$ecology <- paste0(args[1], '/data/ecology_dat/', filenames$ecology)

## Overzicht metabolieten
# get metabolites, their values & type
mytext <- readtext(paste0(args[1], "/log.out"), 'transport', 'tox', stopblankline = TRUE)
metabolites <- getmetabs(mytext)
mytext <- readtext(paste0(args[1], "/log.out"), "tox", "degradation")
metabolites <- cbind(metabolites, gettypes(mytext))
colnames(metabolites) <- c('name', 'energy content', 'type')
rm(mytext)


## Energy on grid Timeseries
# vul data frame met timeseries van average gridconcentraties
gridcon <- NULL
for (filename in filenames$ecology){
  a <- read.csv(filename)
  
  if (is.null(gridcon)) {
    gridcon <- data.frame(time_point = a$time_point, filename = a$avrg)
  }
  else{
    gridcon <- cbind(gridcon, filename = a$avrg)
  }
}

colnames(gridcon) <- c("time_point", metabolites[,1])
rownames(gridcon) <- gridcon[,1]
gridcon <- gridcon[,-1]

energy_total <- rowSums(data.frame(mapply('*', gridcon, metabolites[,2])))
energy_influxed <- rowSums(data.frame(mapply('*', gridcon[,metabolites$type == 'influx'], metabolites[metabolites$type == 'influx',2])))
energy_bblock <- rowSums(data.frame(mapply('*', gridcon[,metabolites$type == 'building block'], metabolites[metabolites$type == 'building block',2])))
energy_intermediate <- rowSums(data.frame(mapply('*', gridcon[,metabolites$type == 'intermediate'], metabolites[metabolites$type == 'intermediate',2])))


## Reaction Counts timeseries
# Reaction fraction timeseries ####
reactioncounts <- read.csv(paste0(args[1], "/data/population_dat/reaction_counts.csv"), header = TRUE, check.names = FALSE) # check.names False because of weird characters in header
reactioncounts[is.na(reactioncounts)]<- 0  # change NA values to 0 
names(reactioncounts) <- gsub("False", "import", names(reactioncounts)) # remove false ..
names(reactioncounts) <- gsub("True", "export", names(reactioncounts)) # .. and true from column names

# columns uit data frame subsetten: alleen pumps
#indices bepalen
pump.index <- grep('^.{3}\\*', names(reactioncounts))
enzyme.index <- grep('^.{3}\\*', names(reactioncounts), invert = TRUE)
enzyme.index <- enzyme.index[2:length(enzyme.index)] # remove 1st item (timecourse)

# eigen data frame voor pumps en enzymes
pop.pump.counts <- reactioncounts[pump.index]
pop.enzyme.counts <- reactioncounts[enzyme.index]

# clean up names: remove import from reaction names
names(pop.enzyme.counts) <- gsub("import", "", names(pop.enzyme.counts)) 




## Calculate Shannon diversity ####
div <- apply(cbind(pop.enzyme.counts, pop.pump.counts)[,-1], 1, shannondiversity)

## Logo maken van import pomps ####
import <- pop.pump.counts[grep("import", names(pop.pump.counts))]
import <- import[,order(names(import))] # order names
names(import) <- LETTERS[seq(ncol(import))]
#logo <- apply(import, 1, function(x) paste(names(x)[x > 0.1], collapse = ""))
count_total <- apply(import, 1, function(x)sum(x>0.1))
count_influx <- apply(import[,metabolites$type =='influx'], 1, function(x)sum(x>0.1))
count_bblocks <- apply(import[,metabolites$type =='building block'], 1, function(x)sum(x>0.1))
count_ininter <- apply(import[,metabolites$type =='intermediate'], 1, function(x)sum(x>0.1))
options(scipen=999)




## Plotting Part ####

# Initialise plot
# We make a 10 x 5 matrix where:
# The title, axis legend and rainbow legend are plotted on the outer sides (IDs 1, 2, 3, 4)
# main plots are plotted in IDs 5,6,7,8
# per metabolite small inset plots are plotted in IDs 9 thru 24
# ID 25 is an empty spacer for layout purposes

pdf(file = if(length(args) > 3) args[4] else 'Rplot.pdf', width = 14, height = 10)
layout(matrix(c(1,  1,  1, 1,  1, 1,
                2,  5,  6, 9,  17, 3,
                2,  5,  6, 10, 18, 3,
                2,  5,  6, 11, 19, 3,
                2,  5,  6, 12, 20, 3,
                2,  7,  8, 13, 21, 3,
                2,  7,  8, 14, 22, 3,
                2,  7,  8, 15, 23, 3,
                2,  7,  8, 16, 24, 3,
                25, 4,  4, 4, 4, 25), 
              
              10, 6, byrow = TRUE), widths = c(0.7, 5, 5, 1, 1), heights = c(1, 1.25,1.25,1.25,1.25, 1.25,1.25,1.25,1.25, 1,25, 1.2))


#Title in 1
par(mar=c(1,1,1,1))
plot.ts(1:10, col="white", axes=FALSE, ylab='', xlab='')       # plot leeg vlak op 1,1 voor tekst
mtext(side=3, name,  cex = 1.5, line = -1, adj = 0)
mtext("numbers: unique pump count in >10% of population", side = 3, line =-1, adj = 1, cex = 1)
if(annotate){mtext("+ / - indicate count in / decrease", side = 3, line =-3, adj = 1)}

# Text in 2 (left side)
par(mar=c(1,1,1,1))
plot.ts(1:10, col="white", axes=FALSE, ylab='', xlab='')       # plot leeg vlak op 1,1 voor tekst
mtext("average energy left per grid cell", side = 2, cex = 1.5, line = -1)

# Rainbow legend in 3 (right side)
col <- rainbow(length(div), end = 0.8)
legend_image <- as.raster(matrix(col, ncol=1))
par(mar=c(0, 1, 2, 1.5))
plot(c(0,2),c(0,1),type = 'n', axes = F,xlab = '', ylab = '', main = 'Time Point', cex.main = 1)
text(x=1.5, y = seq(0,1,l=6), labels = rev(seq(0, tail(reactioncounts$time_point, n = 1), l = 6)), cex = 1)
rasterImage(legend_image, 0, 0, 0.3, 1)

# Text in 4 (bottom)
par(mar=c(1,1,1,1))
plot.ts(1:10, col="white", axes=FALSE, ylab='', xlab='')       # plot leeg vlak op 1,1 voor tekst
Shannon <- expression(paste(plain(Diversity) ==-sum(p[i]*logp[i],"i = 1", n), italic("   (where "), p[i], italic(" is the fraction of gene "), i, italic(" in the population)")), sep = " ")
mtext(Shannon, side = 1, cex = 1.3, line = -0.2, adj = 0.5)

# Main Graphs 
#5
par(mar=c(0,0,0,0))
xmax <- max(10, max(div))
ymax <- max(10, max(energy_total))
plotenvsdiv(div, energy_total, n=n, main = 'Total Energy', label = count_total, xaxt = 'n')
#6
par(mar=c(0,0,0,0))
plotenvsdiv(div, energy_influxed, n = n, main = "{Influxed Energy}", label = count_influx, xaxt = 'n', yaxt = 'n')
#7
par(mar=c(0,0,0,0))
ymax <- 1.1 * max(max(energy_intermediate), max(energy_bblock))
plotenvsdiv(div, energy_intermediate, n = n, main = "intermediate energy", label = count_ininter)

#8
par(mar=c(0,0,0,0))
plotenvsdiv(div, energy_bblock, n = n, main = "[building blocks]", label = count_bblocks, yaxt = 'n')


#small inset graphs. There is space for 16 of these, ID 9-24
# influx
n = 5 * n
annotate <- FALSE
par(mar=c(0,0,0,0))
ymax <- max(10, max(energy_total))
for (i in as.numeric(rownames(metabolites[metabolites$type=='influx',]))){
  energy_t <- metabolites$`energy content`[i] * gridcon[[i]]
  plotenvsdiv(div, energy_t, n = n, main = paste0("{", metabolites$name[i], "}"),  label = rep(metabolites$name[i], each = length(energy_t)), cex = 0.3, xaxt = 'n', yaxt = 'n')
}

#intermediates
ymax <- 1.1 * max(max(energy_intermediate), max(energy_bblock))

for (i in as.numeric(rownames(metabolites[metabolites$type=='intermediate',]))){
  energy_t <- metabolites$`energy content`[i] * gridcon[[i]]
  plotenvsdiv(div, energy_t, n = n, main = metabolites$name[i], label = rep(metabolites$name[i], each = length(energy_t)), cex = 0.3, xaxt = 'n', yaxt = 'n')
}

# building blocks
for (i in as.numeric(rownames(metabolites[metabolites$type=='building block',]))){
  energy_t <- metabolites$`energy content`[i] * gridcon[[i]]
  plotenvsdiv(div, energy_t, n = n, main = paste0("[", metabolites$name[i], "]"), label = rep(metabolites$name[i], each = length(energy_t)), cex = 0.3, xaxt = 'n', yaxt = 'n')
}




#Empty squares in 17
plot.ts(1:10, col="white", axes=FALSE, ylab='', xlab='')       # plot leeg vlak op 1,1 voor tekst



# optie om plot op te slaan
if(args[length(args)] == 'sav') {
  savePlot(filename = paste0(name, ".png"), type = 'png', device = dev.cur())
  cat(paste0("Plot saved as ", name), "\n")
}


message("Press Enter To Continue")
invisible(readLines("stdin", n=1))