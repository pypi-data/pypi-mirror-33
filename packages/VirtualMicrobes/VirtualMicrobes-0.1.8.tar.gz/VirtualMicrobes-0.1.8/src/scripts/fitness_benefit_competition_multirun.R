# Competition fitness measure
#x[,colSums(is.na(x)) != nrow(x)]

# This only works when all sims have run for the same ammount of time!

time_k = 350
mu = 39
seed = 1
wt = 14
speciesfile = paste0("/hosts/linuxhome/mutant",mu,"/tmp/brem/Lenski",wt,"_CompeteWithAnc_1longwave",time_k,"k_seed",seed,"/data/population_dat/")
competition_start = time_k*1000
competition_duration = 30

dat = read.csv(paste0(speciesfile, "species_counts.csv"))
pop = read.csv(paste0(speciesfile, "population_size.csv"))
#dat = tail(dat,100)
dat = dat[dat$time_point > competition_start-1,]
pop = pop[pop$time_point > competition_start-1,]
dat = dat[,colSums(is.na(dat)) != nrow(dat)]
#dat = tail(dat, 100)
dat[is.na(dat)] <- 0
wildtype = c(0.0,0.5,dat[1:competition_duration,2]*pop[1:competition_duration,2],0.0)
wildtype[is.na(wildtype)] <- 0.0
ancestor = c(0.0,0.5,dat[1:competition_duration,3]*pop[1:competition_duration,2],0.0)
ancestor[is.na(ancestor)] <- 0.0

diff = wildtype / ancestor
diff[is.na(diff)] <- 0.0
fitness = sum(diff) / length(which(wildtype > 0.0))
#fitness = diff[length(diff)-1]
par(xaxs='i', yaxs='i')
cat(paste("Fitness = ", fitness,"\n"))
ts.plot(wildtype, ylim=c(0,1600), gpars=list(xaxt="n"), lwd=0, xlim=c(2,competition_duration), main=paste("Fitness benefit = ",fitness,"(= avg dist)"), ylab="Frequency of species") #WT
polygon(wildtype, col=adjustcolor("#3884aa", alpha.f=0.50), lty=1, lwd=2, border="#3884aa")
polygon(ancestor, col=adjustcolor("#ffe527", alpha.f=0.50), lty=1, lwd=2, border="#ffe527")
axis(4)
axis(1, at=seq(0,competition_duration, by=50))



time_k = 440
mu = 39
seed = 1
wt = 14
speciesfile = paste0("/hosts/linuxhome/mutant",mu,"/tmp/brem/Lenski",wt,"_CompeteWithAnc_1longwave",time_k,"k_seed",seed,"/data/population_dat/")
competition_start = time_k*1000
competition_duration = 30

dat = read.csv(paste0(speciesfile, "species_counts.csv"))
pop = read.csv(paste0(speciesfile, "population_size.csv"))
#dat = tail(dat,100)
dat = dat[dat$time_point > competition_start-1,]
pop = pop[pop$time_point > competition_start-1,]
dat = dat[,colSums(is.na(dat)) != nrow(dat)]
#dat = tail(dat, 100)
dat[is.na(dat)] <- 0
wildtype = c(0.0,0.5,dat[1:competition_duration,2]*pop[1:competition_duration,2],0.0)
wildtype[is.na(wildtype)] <- 0.0
ancestor = c(0.0,0.5,dat[1:competition_duration,3]*pop[1:competition_duration,2],0.0)
ancestor[is.na(ancestor)] <- 0.0

diff = wildtype / ancestor
diff[is.na(diff)] <- 0.0
fitness = sum(diff) / length(which(wildtype > 0.0))
#fitness = diff[length(diff)-1]
par(xaxs='i', yaxs='i')
cat(paste("Fitness = ", fitness,"\n"))
#ts.plot(wildtype, ylim=c(0,1600), gpars=list(xaxt="n"), lwd=0, xlim=c(2,competition_duration), main=paste("Fitness benefit = ",fitness,"(= avg dist)"), ylab="Frequency of species") #WT
polygon(wildtype, col=adjustcolor("#ffe527", alpha.f=0.00), lty=1, lwd=2, border="#ffe527")
polygon(ancestor, col=adjustcolor("#ffe527", alpha.f=0.00), lty=1, lwd=2, border="#ffe527")
axis(4)
axis(1, at=seq(0,competition_duration, by=50))