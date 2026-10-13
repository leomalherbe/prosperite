# This script creates box plots of shortfall and overshoot by year, and pulls out relevant stats discussed in Main.

#read in cleaned data file
myData6 <- read_csv("./myData/5_20250108_doughnutDat-boundariesRatios.csv") %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice")))

ecoSoc3 <- read_csv("./myData/9_20250516_Doughnut-GlobalTablesData.csv") %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice")))

#-----------------------------------------------------------------------------------------------------------
#read in population data
popData <- read_csv("./cleanData/WPP2022_PopulationData_1950-2100.csv") 

wld <- popData %>%
  group_by(date) %>%
  summarise(population = sum(population, na.rm=T)) %>%
  ungroup() %>%
  add_column(variant = "estimate", country = "World", iso3c = "WLD") %>%
  relocate(variant, country, iso3c)

#write world population to file
#write_csv(wld, "./myData/10_worldPopulation_1950-2100.csv")
rm(popData)

#-----------------------------------------------------------------------------------------------------------
#Pull out 2000-01 and 2021-22 population results to discuss
wldPopStart <- wld %>% 
  filter(date %in% c(2000, 2001)) %>%
  select(group = country, grpCode = iso3c, date, populationStart = population) %>%
  group_by(group, grpCode) %>%
  summarise(populationStart = mean(populationStart)) %>%
  ungroup()

wldPopEnd<- wld %>% 
  filter(date %in% c(2021, 2022)) %>%
  select(group = country, grpCode = iso3c, date, populationEnd = population) %>%
  group_by(group, grpCode) %>%
  summarise(populationEnd = mean(populationEnd)) %>%
  ungroup()

wldPop <- full_join(wldPopStart, wldPopEnd, by=c("group", "grpCode"))

rm(wldPopStart, wldPopEnd)

ecoSoc4 <- left_join(ecoSoc3, wldPop, by=c("group", "grpCode"))

rm(ecoSoc3, wld, wldPop)
#-----------------------------------------------------------------------------------------------------
#ranges
#-----------------------------------------------------------------------------------------------------
#look at change in social shortfall range by year (bring first observation backward to remove structural breaks
#from missing vals)

socFull <- myData6 %>%
  filter(type == "global doughnut", domain == "social", !indCode %in% c("NU2", "EQ2", "CO1")) %>%
  mutate(ratio = 1-ratio,
    ratio = na.locf(ratio, fromLast=T, na.rm=F)) 

ggplot(socFull, aes(date, ratio)) +
  geom_hline(yintercept = 0, lwd=3, col="#227443") +
  geom_boxplot(aes(group = date), outlier.shape=NA) +
  geom_jitter(width=0.2) +
  scale_y_reverse(limits=c(1,0), labels = scales::percent) +
  scale_x_continuous(expand = c(0,0.1)) +
#  scale_y_continuous(labels = scales::percent) +
#  coord_cartesian(ylim=c(1,0), xlim=c(2000,2022)) +
  labs(x="Year", y="Range of shortfall across social\nindicators (0 = no shortfall)") +
  theme_bw()

#save figure to file
#ggsave("./figures/ExtDataFig3_shortfallRange-by-year_Boxplots_final.png", width = 180, height = 80, units = "mm", device="png")

#get data
g <- ggplot(socFull, aes(date, ratio)) +
  geom_boxplot(aes(group = date))

socRange <- layer_data(g)
rm(g)

# i don't have time to figure out how to save the listed outliers to file. 
#they are values for societal poverty and perceptions of corruption in 2020 (74% and 75.7%), 
#2021 (72.5% and 74.6%), and 2022 (72.5% and 74.8%)

#socOutliers <- socRange %>%
#  select(outliers, x) %>%
#  unnest(outliers)

socRange1 <- socRange %>%
  select(-outliers, -newx) %>%
  tibble()
   #%>%
#  left_join(., socOutliers, by="x")

#write boxplot data to file
#write_csv(socRange1, "./myData/10_20250204_SocialShortfall-boxPlotData.csv")

rm(socRange, socRange1, socOutliers)
#-----------------------------------------------------------------------------------------------------
#look at change in ecological overshoot range by year
ecoFull <- myData6 %>%
  filter(type == "global doughnut", domain == "ecological") %>%
  mutate(ratio = ratio-1)

ggplot(ecoFull, aes(date, ratio)) +
  geom_hline(yintercept = 0, lwd = 3, col="#227443") + 
  geom_boxplot(aes(group = date)) + 
  geom_jitter(width=0.2) +
  coord_cartesian(ylim = c(-1,3), xlim = c(2000,2022)) +
  scale_y_continuous(breaks=c(-1,0,1,2,3), labels = c("*", "0%", "100%", "200%", "300%")) +
  scale_x_continuous(expand = c(0,0.5)) +
  labs(x = "Year", y = "Range of overshoot across ecological\nindicators (0 = no overshoot)") +
  theme_bw()

#ggsave("./figures/ExtDataFig4_overshootRange-by-year_Boxplots_final.png", width = 180, height = 80, units = "mm", device="png")

#get data
g <- ggplot(ecoFull, aes(date, ratio)) +
  geom_boxplot(aes(group = date))

ecoRange <- layer_data(g) 
rm(g)

# i don't have time to figure out how to save the listed outliers to file. 
#they are repeated values for extinction rate and chemical pollution, at 900% and 1400+% respectively

ecoRange1 <- ecoRange %>%
  select(-outliers, -newx) 


#write boxplot data to file
#write_csv(ecoRange1, "./myData/10_20250113_EcologicalOvershoot-boxPlotData.csv")
#------------------------------------------------------------------------------------------
#			pull out most recent vals (2022)
#------------------------------------------------------------------------------------------
myData6 %>% filter(type == "global doughnut", date == 2022, domain == "social", value > 70)# %>% summary()
myData6 %>% filter(type == "global doughnut", date == 2022, domain == "ecological") %>% mutate(ratio-1) %>% summary()


#------------------------------------------------------------------------------------------
#look at start/end periods
#------------------------------------------------------------------------------------------
soc <- ecoSoc4 %>% 
  filter(type == "global doughnut", domain == "social") %>%
  rowwise() %>%
  mutate(ratioStart = ifelse(indicator == "racialEquality", NA, ratioStart),
    ratioEnd = ifelse(indicator == "racialEquality", NA, ratioEnd)) %>%
  ungroup()

eco <- ecoSoc4 %>%
  filter(type == "global doughnut", domain == "ecological")
#------------------------------------------------------------------------------------------
#Check number of indicators by range of shortfall 
#------------------------------------------------------------------------------------------
#Check number of indicators with more than 50%  
soc %>% filter(ratioStart >= 0.5) #10
soc %>% filter(ratioEnd >= 0.5) #5

soc %>% filter(ratioStart >= 0.25) #15
soc %>% filter(ratioEnd >= 0.25) #15

soc %>% filter(diff <= -0.2)
soc %>% filter(diff >= -0.06)

#------------------------------------------------------------------------------------------
#Check % worsening of overshoot 
#------------------------------------------------------------------------------------------
eco %>% filter(betterWorse == "worsening", indCode != "FD1") %>%
  rowwise() %>% mutate(pctWorse = (ratioEnd-ratioStart)/ratioStart*100)

#------------------------------------------------------------------------------------------
#Historical trends 
#------------------------------------------------------------------------------------------
#Check ecological interquartile range across indicators w/ available time series (N=8) 
eco %>% 
  filter(!indicator %in% c("blueDev", "extinction1900", "interhemAOD", "omega_a"), betterWorse == "worsening") %>%
  summary() 
#Start: 97% [52,133%]  End: 193% [89,227%]
#Ambition to reach 0 by 2050: 

#Check social interquartile range across indicators w/ available time series
soc %>% 
  filter(!indicator %in% c("publicTrans","racialInequality")) %>%
  summary() ##Start: 46% [24,72%]  End: 34% [23,42%]

#------------------------------------------------------------------------------------------
#Comparing social indicators with significant improving trends with pathway to eliminate social shortfall by 2030 (N=17)
#------------------------------------------------------------------------------------------
#Pull out median and interquartile range of increased ambition needed to meet human needs by 2030 for improving trends  
soc %>% 
  filter(!indicator %in% c("publicTrans","racialEquality"), betterWorse == "improving") %>% 
  rowwise() %>%
  #mutate(ambition = (slopeD - slope)/ slope) %>%
  mutate(ambition = slopeD / slope) %>%
  ungroup() %>% summary() #filter(ambition > 2 & ambition <= 9)

#check ranges
soc1 %>% filter(ambition > 9) #(N=6)
soc1 %>% filter(ambition <= 2) #(N=3)
soc1 %>% filter(ambition > 2 & ambition <= 8) #(N=8)

#------------------------------------------------------------------------------------------
#Clean up
#------------------------------------------------------------------------------------------
rm(eco, ecoFull, ecoRange, ecoRange1, ecoSoc4, myData6, rangeRatio, soc, soc1, socFull)
