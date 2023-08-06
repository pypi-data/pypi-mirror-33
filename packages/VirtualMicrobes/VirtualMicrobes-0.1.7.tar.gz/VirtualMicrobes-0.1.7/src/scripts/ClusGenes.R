#!/usr/bin/env Rscript
# k means clustering of Virtual Microbe ecosystem through time
# based on gene fractions in the population

library("optparse")

#"Example:", "\n",
#"./Rscript ClusGenes.R --dir=/hosts/linuxhome/mutant3/tmp/jeroen/superexcitingexperiment_3 --start=25000 --end=35000", "\n",
#"Plots a timeseries from 25000 to 35000 of clustered genes without saving anything. Super exciting!", "\n",
#"\n"

option_list = list(
    make_option(
        c("-d", "--dir"),
        type = "character",
        default = NULL,
        help = "dataset file name"
    ),
    make_option(
        c("-s", "--start"),
        type = "numeric",
        default = 0,
        help = "start time point"
    ),
    make_option(
        c("-e", "--end"),
        type = "numeric",
        default = NULL,
        help = "end time point"
    ),
    make_option(
        c("-n", "--nrsteps"),
        type = "integer",
        default = 100,
        help = "Number of steps to plot."
    ),
    make_option(
        c("-c", "--clustime"),
        action = "store_true",
        default = FALSE,
        help = "Number of steps to plot."
    ),
    make_option(
        c("-f", "--file"),
        type = "character",
        default = "clustering.pdf",
        help = "save file name",
        metavar = "character"
    )
)


opt_parser = OptionParser(option_list = option_list)

opt = parse_args(opt_parser)


## Load data. (Required to parse the rest of the arguments)
opt$dir <- gsub(" ", "", opt$dir)
file <- opt$dir
data <-
    read.csv(
        paste0(file, "/data/population_dat/reaction_counts.csv"),
        header = TRUE,
        check.names = FALSE,
        row.names = 1
    )
data[is.na(data)] <- 0  # change NA values to 0

# Clean up row and column names
colnames(data) <-
    gsub("False", "import", colnames(data)) # remove false ..
colnames(data) <-
    gsub("True", "export", colnames(data)) # .. and true from column names
colnames(data)[1:(ncol(data) - 16)] <-
    gsub("import", "", colnames(data[, 1:(ncol(data) - 16)]))

## set argument defaults
if (is.null(opt$end)) {
    opt$end <- as.numeric(tail(rownames(data), n = 1))
}

# Make a sequence to subset the data for the interval provided. As the data is saved in intervals
# we check if NrSteps isn't bigger than the number of actual data points between StartTime and EndTime.
# We then round the sequence to the nearest rownumber.
# compute Interval and compare to interval in the data

MaxStep <- (opt$end - opt$start) /  as.numeric(rownames(data[2, ]))
opt$nrsteps <- min(opt$nrsteps, MaxStep)

SubIndex <-
    round(seq(
        which(rownames(data) == opt$start),
        which(rownames(data) == opt$end),
        length.out = opt$nrsteps
    ))

# creating function wssplot
# not used at the moment.
wssplot <- function(data, nc = 15, seed = 1234) {
    wss <- (nrow(data) - 1) * sum(apply(data, 2, var))
    for (i in 2:nc) {
        set.seed(seed)
        wss[i] <- sum(kmeans(data, centers = i)$withinss)
    }
    plot(1:nc,
         wss,
         type = "b",
         xlab = "Number of Clusters",
         ylab = "Within groups sum of squares")
}

# makes a filename from a directory
makename <- function(dir, affix) {
    # output name is: ~/mu<mutant nr>_<basename of the dir>_<affix>
    mutant.index <-
        regexpr("(+|^)mutant($|[^a-zA-Z])|([^a-z]+|^)vit e($|[^a-zA-Z])",
                dir)
    mutant.index <- regexpr("mutant[0-9]+", dir)
    mutant.name <-
        substr(dir,
               mutant.index[1] + 6,
               mutant.index[1] + attr(mutant.index, "match.length"))
    mutant.name <-
        paste0("mu", sub("/$", "", mutant.name))                                                                 # remove last character if this is is a "/" (otherwise illegal pdfName))
    
    dir.name <- basename(dir)
    
    if (missing(affix)) {
        name <- paste0("~/", mutant.name, "_", dir.name)
    } else {
        name <- paste0("~/", mutant.name, "_", dir.name, "_", affix)
    }
    
    return(name)
}

pdf(file = opt$file ,
    width = 16,
    height = 11)

#Timeplot (cluster only genes)
if (opt$clustime == TRUE) {
    affix <- "heatmap_tg.png"
    heatmap(
        t(as.matrix(data[SubIndex, ])),
        margins = c(10, 10),
        scale = 'none',
        main = file,
        sub = paste0(
            "Time point ",
            opt$start,
            " - ",
            opt$end,
            " in ",
            opt$nrsteps,
            " steps"
        )
    )
    
} else {
    affix <- "heatmap_g.png"
    heatmap(
        t(as.matrix(data[SubIndex, ])),
        Colv = NA,
        margins = c(10, 10),
        scale = 'none',
        main = file,
        sub = paste0(
            "Time point ",
            opt$start,
            " - ",
            opt$end,
            " in ",
            opt$nrsteps,
            " steps"
        )
    )
}

message("Press Enter To Continue")
invisible(readLines("stdin", n = 1))
