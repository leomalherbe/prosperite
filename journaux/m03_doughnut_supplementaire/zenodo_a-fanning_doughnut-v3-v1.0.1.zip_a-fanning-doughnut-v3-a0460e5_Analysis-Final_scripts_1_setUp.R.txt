#Set working directory, load libraries, and themes

setwd("C:/Users/afann/Documents/DoughnutEconomics/Research/Doughnut_v3/Analysis")

library(jsonlite)
library(tidyverse)
library(zoo)
library(scales)
library(ggpubr)
library(lmtest)
library(sandwich)
#library(tsibble)
#library(fable)

options(tibble.width = Inf)
#------------------------------------------------------------------------------------------
#-----------------------------------
#ggplot themes
#----------------------------------
# BASIC THEME
theme_chart <- 
  theme(legend.position = "right") +
  theme(panel.background = element_rect(fill = "white", colour = "grey50")) +
  theme(plot.title = element_text(size=16, family="sans", face="bold", hjust=0, color="#666666")) +
  theme(panel.grid = element_line(colour = "#efefef")) +
  theme(axis.title = element_text(size=10, family="sans", color="#666666"))

# SCATTERPLOT THEME
theme_chart_SCATTER <- theme_chart +
  theme(axis.title.x = element_text(hjust=0, vjust=-.5))

# HISTOGRAM THEME
theme_chart_HIST <- theme_chart +
  theme(axis.title.x = element_text(hjust=0, vjust=-.5))

# SMALL MULTIPLE THEME
theme_chart_SMALLM <- theme_chart +
  theme(panel.grid.minor = element_blank()) +
  theme(strip.background = element_rect(fill="white", colour="grey50")) +
  theme(strip.text = element_text(size=8, family="sans", color="#666666")) +
  theme(axis.text = element_text(size=8, family="sans", color="#666666")) +
  theme(axis.title = element_text(size=10, family="sans", color="#666666"))


#------------------------------------------------------------------------
#	MY FUNCTIONS TO EXTRACT AND SPREAD VALUES FOR JSON NESTING
#------------------------------------------------------------------------
#functions
#get minMax ranges by indicator code
rangeRatio <- function(dat, ...){
  args <- rlang::enexprs(...)
  dat %>% filter(!!! args) %>%
  group_by(grp, grpCode) %>%
  summarise(min = min(ratio, na.rm=T),
	max = max(ratio, na.rm=T)) %>%
  ungroup()
}

#get ratios by indicator code
spreadRatio <- function(dat, ...){
  args <- rlang::enexprs(...)
  dat %>% filter(!!! args) %>%
  select(grp, grpCode, date, ratio) %>%
  pivot_wider(names_from=date, values_from=ratio)
}

#make blank tibbles to fill global series1 or series2 (NOTE: "WORLD"/"WLD" ARE HARD-CODED/NOT SCALABLE)
#(depending on if there are 1 or 2 indicators per dimension)
blankRatio <- function(){
  tibble(grp="World", grpCode="WLD", date=2000:2022, val=0) %>%
  pivot_wider(names_from=date, values_from=val)
}

#make blank group tibbles to fill series1 or series2
#(depending on if there are 1 or 2 indicators per dimension)
blankRatioGrp <- function(dat, ...){
  args <- rlang::enexprs(...)
  dat %>% filter(!!! args) %>%
  select(grp, grpCode, date, ratio) %>%
  mutate(ratio=0) %>%
  pivot_wider(names_from=date, values_from=ratio)
}


#loop to pull out variable values and put into a list
pullVars <- function(dat,index){
  dat <- dat %>% select(-grp, -grpCode)
  for(j in 1:ncol(dat)){
    myList[j] <- list(
    dat[[j]][index])
  }
  myList
}

#------------------------------------------------------------------------
#  MY FUNCTIONS TO ESTIMATE DYNAMIC STATISTICAL FORECASTS (NOT USED IN REV 2)
#------------------------------------------------------------------------
#function to compare ETS and ARIMA by minimising root mean standard error
chooseModel <- function(x) {
  mod <- x %>%
	slice(-n()) %>%
	stretch_tsibble(.init=10) %>% #normally 10 unless series has less than 10 (blueDev, HANPP, foodInsecurity)
	model(ETS(value),
	  ARIMA(value)) %>%
	forecast(h=1) %>%
	accuracy(x) %>%
	select(.model, RMSE)
  mod %>%
	filter(RMSE == min(RMSE)) %>%
	select(.model)
}

#function to estimate best-fitting forecasts to 2030
fcast <- function(dat, model, yearN){
  fwd <- dat %>%
	model(eval(rlang::parse_expr(model$.model))) %>%
	forecast(h=yearN)
  fwd
}

#function to extract median and 66% confidence intervals
extractVars <- function(fwd) {
  fcastVars <- fwd %>%
	hilo(level=66) %>%
	unpack_hilo(`66%`) %>%
  	select(-.model, -value) %>%
  	rename(value = .mean, BAU_low = `66%_lower`, BAU_high = `66%_upper`)
  fcastVars
}


