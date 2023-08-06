#!/usr/bin/env Rscript
# Plots gene frequencies in a population for a given timepoint
# from /data/population_dat/reaction_counts.csv

# How to use: run from terminal and provide 1-3 arguments in the following order:
# "folder"                : folder to plot
# "timepoint" (optional)  : select timepoint for which to make the plot
# "sav" (optional)        : save the plot to ~/folder.png
# e.g. "Rscript gene_fix_in_pop.R EvoIHGT 150000 sav" will open a window where the gene frequencies at t=150000
# are plotted, and will save a copy of the plot to ~/EvoIHGT.png
# "Rscript gene_fix_in_pop.R EvoIHGT" will open a window with the gene frequencies plotted at the final timepoint.

library("optparse")

option_list = list(
    #make_option(c("-d", "--dir"), type="character", default=NULL,
    #            help="dataset file name"),
    make_option(
        c("-t", "--timepoint"),
        type = "numeric",
        default = NULL,
        help = "time point to plot"
    ),
    make_option(
        c("-f", "--file"),
        type = "character",
        default = NULL,
        help = "save file name",
        metavar = "character"
    )
)


opt_parser = OptionParser(usage = "%prog [options] dir", option_list = option_list)

arguments <- parse_args(opt_parser, positional_arguments = 1)
opts = arguments$options
dir <- arguments$args
args <- commandArgs(trailingOnly = TRUE)

# make window
X11(width = 7, height = 11)

cat("Now loading file...\n")
cat(dir)

cat("This file...\n")
# Test bit to test script, ignore this:
#args <-c("/hosts/linuxhome/mutant26/tmp/jeroen/ha_death_fluct0_bas0.03_prodprot_pseed41, 9999999")


# If no argument for time is provided take the last timestep by default
if (is.null(opts$timepoint)) {
    genefix <-
        tail(read.csv(
            paste0(dir, "/data/population_dat/reaction_counts.csv"),
            header = TRUE,
            check.names = FALSE,
            row.names = 1
        ),
        n = 1)
    
    # If argument for time is provided take that timestep
} else {
    cat(opts$timepoint)
    genefix <-
        read.csv(
            paste0(dir, "/data/population_dat/reaction_counts.csv"),
            header = TRUE,
            check.names = FALSE,
            row.names = 1
        )
    genefix <- genefix[opts$timepoint, ]
}

genefix[is.na(genefix)] <- 0  # change NA values to 0

# indices voor pumps en enzymes bepalen
genefix <-
    genefix[, order(colnames(genefix), decreasing = TRUE)] # order by name
pump_index <- grep('^.{3}\\*', names(genefix))
enzyme_index <- grep('^.{3}\\*', names(genefix), invert = TRUE)
print(genefix)
cat(enzyme_index)

# Big list of nice contrasting colours. Using the same colours is nice if you compare different folders.
# if you don't, or need more colours, use something like:
# colours <-sample(rainbow(ncol(genefix)))
colours <-
    c(
        "#00D8FFFF",
        "#FF1A00FF",
        "#FF0034FF",
        "#FF001AFF",
        "#FF9C00FF",
        "#5F00FFFF",
        "#45FF00FF",
        "#FF00B6FF",
        "#00FF09FF",
        "#FF4E00FF",
        "#2BFF00FF",
        "#00F2FFFF",
        "#FF0082FF",
        "#9300FFFF",
        "#00A4FFFF",
        "#00FFD8FF",
        "#FF0068FF",
        "#0009FFFF",
        "#00FFF2FF",
        "#FB00FFFF",
        "#0070FFFF",
        "#FF8200FF",
        "#FFE900FF",
        "#11FF00FF",
        "#FF009CFF",
        "#008AFFFF",
        "#00FF8AFF",
        "#E1FF00FF",
        "#FF00E9FF",
        "#FBFF00FF",
        "#FF6800FF",
        "#C700FFFF",
        "#00FFBEFF",
        "#4500FFFF",
        "#C7FF00FF",
        "#0056FFFF",
        "#00FF3DFF",
        "#E100FFFF",
        "#5FFF00FF",
        "#FF3400FF",
        "#7900FFFF",
        "#FF004EFF",
        "#FFCF00FF",
        "#00FF70FF",
        "#AD00FFFF",
        "#FFB600FF",
        "#79FF00FF",
        "#00BEFFFF",
        "#0023FFFF",
        "#1100FFFF",
        "#00FF23FF",
        "#FF0000FF",
        "#2B00FFFF",
        "#ADFF00FF",
        "#003DFFFF",
        "#00FFA4FF",
        "#00FF56FF",
        "#FF00CFFF",
        "#93FF00FF"
    )


# namen opschonen
names(genefix) <-
    gsub("False", "import", names(genefix)) # remove false ..
names(genefix) <-
    gsub("True", "export", names(genefix)) # .. and true from column names
names(genefix)[enzyme_index]  <-
    gsub("import", "", names(genefix)[enzyme_index]) # remove import from enzyme names
names(genefix)[-enzyme_index] <-
    gsub("\\d.*-->\\s1\\s", "", names(genefix)[-enzyme_index])


layout(matrix(c(1, 2, 3), ncol = 1),
       widths = c(1),
       heights = c(1, 6, 4))
par(mar = c(1, 0, 1, 0))
plot.new()
text(
    0.5,
    0.5,
    paste0("Population Gene Fixation at t = ", rownames(genefix)),
    cex = 2,
    font = 2
)
par(mar = c(0, 20, 0, 2)) # nieuwe margins voor linkerplot met reactienamen
barplot(
    100 * t(genefix)[enzyme_index, 1],
    space = 0.3,
    xlab = "",
    ylab = "",
    beside = TRUE,
    border = NA,
    cex.names = 1,
    col = colours[enzyme_index],
    horiz = TRUE,
    names.arg = colnames(genefix)[enzyme_index],
    las = 2,
    axes = FALSE,
    xlim = c(0, 100)
)
abline(v = c(0, 25, 50 , 75, 100),
       lty = 3,
       col = "black")
par(mar = c(4, 20, 0, 2)) # nieuwe margins voor linkerplot met reactienamen
barplot(
    100 * t(genefix)[pump_index, 1],
    space = 0.3,
    xlab = "",
    ylab = "",
    beside = TRUE,
    border = NA,
    cex.names = 1,
    col = colours[pump_index],
    horiz = TRUE,
    names.arg = colnames(genefix)[pump_index],
    las = 2,
    axes = FALSE,
    xlim = c(0, 100)
)
axis(
    1,
    at = c(0, 25, 50, 75, 100),
    labels = c(0, 25, 50, 75, 100),
    cex.axis = 1.6
)
abline(v = c(0, 25, 50 , 75, 100),
       lty = 3,
       col = "black")

mtext(
    "Reactions",
    side = 3,
    lin = -8.8,
    at = 0.2,
    outer = TRUE,
    cex = 1.15
)
mtext(
    "Pumps",
    side = 3,
    outer = TRUE,
    cex = 1.2,
    lin  = -53.7,
    at = 0.23
)
mtext(
    "% of population carrying gene",
    side = 1,
    outer = TRUE,
    lin  = -1.6,
    cex = 1,
    at = 0.57
)

if (!is.null(opts$file)) {
    savePlot(filename = opts$file,
             type = 'png',
             device = dev.cur())
}

message("Press Enter To Continue")
invisible(readLines("stdin", n = 1))
