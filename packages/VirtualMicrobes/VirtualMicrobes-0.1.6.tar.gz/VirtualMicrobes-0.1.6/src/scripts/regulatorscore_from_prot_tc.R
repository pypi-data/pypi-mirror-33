# This function calculates a self-invented regulator score, that measures the de facto 
# qualitative changes in protein concentrations (variance in derivative of log)
calc=function(mu,pop,env,plot=TRUE){
  library(matrixStats)
  path = paste0("/hosts/linuxhome/mutant",mu,"/tmp/brem/WT_Regulators_pop",pop,"_env",env,"/")
  ma <- function(x,n=5){filter(x,rep(1/n,n), sides=2)}
  regulatorness = 0.0
  enzymescore=0.0
  totalscore=0.0
  par(mfrow=c(2,2))
  file = "enzymes_old.csv"
  file = paste0(path,"data/best_dat/", file)
  # EERST ENZYMES
  prot = read.csv(file, header=T, row.names=1)
  prot = prot[seq(0,dim(prot)[1], by=2),] #(ommit extra rows caused by integrator)
  prot = prot[ , colSums(is.na(prot)) == 0] # filter out gained genes (HGT)
  meancolsum = mean(colSums(prot)) # MEAN CUM EXPRESSION
  
  prot = prot[ , colSums(prot) > meancolsum*0.1] # FILTERS OUT LOST GENES, (OR) IF VERY LOW EXPRESSED
  
  begin = 100 # Skip early life of cell, much bias of mutations
  eind = dim(prot)[1]-1
  cat(eind)
  cat("\n")
  varderiv = rowVars(as.matrix(diff(as.matrix(prot))[begin:eind,]) / as.matrix(prot)[begin:eind,],na.rm=T)
  varderiv = varderiv[varderiv>0.0001]
  regulatorness = sum(varderiv)/dim(prot)[1]
  enzymescore = regulatorness
  cat("Plotting 1")
  if(plot) ts.plot(rowVars(as.matrix(diff(as.matrix(prot))[begin:eind,]) / as.matrix(prot)[begin:eind,],na.rm=T),ylim=c(0,0.001), main=regulatorness*10000)
  cat("Plotting 2")
  if(plot) ts.plot(prot[begin:eind,1], ylim=c(0,5))
  cat("Plotting 3")
  if(plot) for(i in 2:3) { lines(prot[begin:eind,i], lty=i) }
  cat("Done plotting")
  # EN NU PUMPS
  
  file = "pumps_old.csv"
  file = paste0(path,"data/best_dat/", file)
  prot = read.csv(file, header=T, row.names=1)
  prot = prot[seq(0,dim(prot)[1], by=2),] #(ommit extra rows caused by integrator)
  prot = prot[ , colSums(is.na(prot)) == 0] # filter out gained genes (HGT)
  meancolsum = mean(colSums(prot))
  cat(colSums(prot))
  cat("\n")
  cat(meancolsum)
  cat(dim(prot))
  prot = prot[ , colSums(prot) > meancolsum*0.1] # filter out lost genes
  cat("\n")
  cat(dim(prot))
  begin = 100 # Skip early life of cell, much bias of mutations
  eind = dim(prot)[1]-1

  
  varderiv = rowVars(as.matrix(diff(as.matrix(prot))[begin:eind,]) / as.matrix(prot)[begin:eind,],na.rm=T)
  varderiv = varderiv[varderiv>0.0001]
  regulatorness = sum(varderiv)/dim(prot)[1]
  totalscore = (enzymescore + regulatorness)*10000
  cat("Plotting 1")
  if(plot) ts.plot(rowVars(as.matrix(diff(as.matrix(prot))[begin:eind,]) / as.matrix(prot)[begin:eind,],na.rm=T),ylim=c(0,0.001), main=regulatorness*10000)
  if(plot) ts.plot(prot[begin:eind,1], ylim=c(0,5))
  if(plot) for(i in 2:3) { lines(prot[begin:eind,i], lty=i) }
  return(totalscore)
}

calc(37,43,23)
