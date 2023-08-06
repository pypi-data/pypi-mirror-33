#!/usr/bin/env Rscript
###               PLOT GENE FREQUENCIES                          	###
###                   	HOW TO USE                               	###
# Navigate to your folder on the mutant in the terminal	            #
# start the script using by :                                       #
# "Rscript /pathtothisscript/gene_fix_in_pop <arg>.R                #
# Substitue arg for the folders you wish to plot                    #

library("optparse")

option_list = list(
    make_option(
        c("-n", "--nrsteps"),
        type = "integer",
        default = 1,
        help = "Number of steps to plot."
    ),
    make_option(
        c("-m", "--movie"),
        type = "character",
        default = NULL,
        help = "movie type"
    ),
    make_option(
        c("-f", "--file"),
        type = "character",
        default = NULL,
        help = "save file name"
    ),
    make_option(
        c('--tempdir'),
        type = 'character',
        default = 'temp_images',
        help = 'temporary save dir for image files'
    )
)

opt_parser = OptionParser(usage = "%prog [options] dir", option_list = option_list)

arguments <- parse_args(opt_parser, positional_arguments = 1)
opts = arguments$options
dir <- arguments$args
args <- commandArgs(trailingOnly = TRUE)
n = as.integer(args[2])

# make window


cat("Now loading file...\n")

#args <-c("/hosts/linuxhome/mutant26/tmp/jeroen/ha_death_fluct0_bas0.03_prodprot_pseed41", 10)
# make plot
make.mov <- function(img_dir, img_ext = 'png', movie_name = 'gene_fix'){
    movie_name <- paste(movie_name, 'mp4', sep='.')
    unlink(movie_name)
    img_glob <- file.path('.',img_dir, paste0('*.', img_ext))
    #command <- "convert -delay 0.5 /tmp/foo*.jpg plot.mpg"
    command <- paste0('ffmpeg-static -pattern_type glob -i \"', img_glob, '\" -c:v libx264 -preset veryslow -qp 0 -pix_fmt yuv444p')
    system(paste(command,movie_name))
}

genefix <-
    read.csv(
        paste0(args[1], "/data/population_dat/reaction_counts.csv"),
        header = TRUE,
        check.names = FALSE,
        row.names = 1
    )
genefix[is.na(genefix)] <- 0  # change NA values to 0

# indices voor pumps en enzymes bepalen
genefix <-
    genefix[, order(colnames(genefix), decreasing = TRUE)] # order by name
pump_index <- grep('^.{3}\\*', names(genefix))
enzyme_index <- grep('^.{3}\\*', names(genefix), invert = TRUE)

# Big list of nice contrasting colours. Always using the same colours is nice if you compare different folders.
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

if(dir.exists(opts$tempdir)){
    unlink(opts$tempdir, recursive = TRUE)
}
if(! is.null(opts$movie)){
    dir.create(opts$tempdir)
    png(paste0(opts$tempdir,'/gene_fix%08d.png'),
        width = 480, height = 800, units = "px", pointsize = 10)
} else{
    X11(width = 10, height = 15)
}


# namen opschonen
names(genefix) <-
    gsub("False", "import", names(genefix)) # remove false ..
names(genefix) <-
    gsub("True", "export", names(genefix)) # .. and true from column names
names(genefix)[enzyme_index]  <-
    gsub("import", "", names(genefix)[enzyme_index]) # remove import from enzyme names
names(genefix)[-enzyme_index] <-
    gsub("\\d.*-->\\s1\\s", "", names(genefix)[-enzyme_index])

genefix <-
    cbind(
        genefix,
        "Enzymes -----------------" = 0,
        "Pumps   -----------------" = 0
    )
order <- c(enzyme_index, ncol(genefix) - 1, pump_index, ncol(genefix))
genefix <- genefix[order]

t <- t(genefix)
par(mar = c(4, 16, 2, 2)) # margins for upper plot

barplot(
    100 * t[, 1],
    space = 0.3,
    xlab = "",
    ylab = "",
    beside = TRUE,
    border = NA,
    cex.names = 1,
    col = colours,
    horiz = TRUE,
    names.arg = colnames(genefix),
    las = 2,
    axes = FALSE,
    xlim = c(0, 100),
    main = paste0("Gene Fixation at t = ", rownames(genefix[1, ]))
)
abline(v = c(25, 50 , 75),
       lty = 3,
       col = "black")

#mtext("Reactions", side = 3, lin = -8, at = 0.1, outer = TRUE, cex = 1.15)
#mtext("Pumps", side = 3, outer = TRUE, cex = 1.2, lin  = -48.7, at = 0.115)
#mtext("% of population carrying gene", side = 1, outer = TRUE, lin  = -1.6, cex = 1, at = 0.57)

#layout(matrix(c(1,2), ncol = 1), widths = c(1), heights = c(1,6))

for (i in seq(1, nrow(genefix), by = opts$nrsteps))
{
    barplot(
        100 * t[, i],
        space = 0.3,
        xlab = "% of population carrying gene",
        ylab = "",
        beside = TRUE,
        border = NA,
        cex.names = 1,
        col = colours,
        horiz = TRUE,
        names.arg = colnames(genefix),
        las = 2,
        axes = TRUE,
        xlim = c(0, 100),
        main = paste0("Gene Fixation at t = ", rownames(genefix[i, ])),
        add = FALSE
    )
}

if(! is.null(opts$movie)){
    dev.off()
    make.mov(img_dir=opts$tempdir, movie_name=opts$movie)
}

message("Press Enter To Continue")
invisible(readLines("stdin", n = 1))
