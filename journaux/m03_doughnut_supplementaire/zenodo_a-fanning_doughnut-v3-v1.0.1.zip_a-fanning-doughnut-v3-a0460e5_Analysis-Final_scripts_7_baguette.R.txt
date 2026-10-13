#This script creates an 'unrolled' global Doughnut
#note if coming from previous 6_convertToJSON script, 
#it'd be a good idea to clear the global environment by restarting R (and re-run '1_setup.r')

#Read in data file if needed.
#myData6 <- read_csv("./myData/5_20250108_doughnutDat-boundariesRatios.csv") %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice")))

#-------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------
#					PREP SOCIAL VARIABLES 
#-------------------------------------------------------------------------------------------------
#get global social data
socData <- myData6 %>% 
  filter(type == "global doughnut", domain == "social")
#-------------------------------------------------------------------------------------------------
#get 2000-01 values for social indicators (except indicators that start later) 
socStart <- socData %>%
  filter(date %in% c(2000,2001),
    !indicator %in% c("foodInsecurity", "youthNEET", "socialSupport", "controlCorruption")) %>%
  select(-populationTotal, -GNIperCap) %>%
  group_by(type, group, grpCode, domain, dimension, indicator, indCode) %>%
  summarise(valueStart = mean(value, na.rm=T),
    ratioStart = mean(ratio, na.rm=T)) %>%
  ungroup()

#get first observations from 2005-06 for youthNEET, socialSupport, and controlCorruption
soc05 <- socData %>%
  filter(date %in% c(2005, 2006), 
    indicator %in% c("youthNEET", "socialSupport", "controlCorruption")) %>%
  select(-populationTotal, -GNIperCap) %>%
  group_by(type, group, grpCode, domain, dimension, indicator, indCode) %>%
  summarise(valueStart = mean(value, na.rm=T),
    ratioStart = mean(ratio, na.rm=T)) %>%
  ungroup()

#get first observations from 2015-16 for foodInsecurity (which is already a 3-year average, see metadata)
soc15 <- socData %>%
  filter(date %in% c(2015,2016), indicator == "foodInsecurity") %>%
  select(-populationTotal, -GNIperCap) %>%
  group_by(type, group, grpCode, domain, dimension, indicator, indCode) %>%
  summarise(valueStart = mean(value, na.rm=T),
    ratioStart = mean(ratio, na.rm=T)) %>%
  ungroup()

socStart1 <- rbind(socStart, soc05, soc15)  %>%
  arrange(dimension, indCode)

rm(socStart, soc05, soc15)
#-------------------------------------------------------------------------------------------------
#get 2021-22 values for social indicators 
socEnd <- socData %>%
  filter(date %in% c(2021,2022)) %>%
  select(-populationTotal, -GNIperCap) %>%
  group_by(type, group, grpCode, domain, dimension, indicator, indCode) %>%
  summarise(valueEnd = mean(value, na.rm=T),
    ratioEnd = mean(ratio, na.rm=T)) %>%
  ungroup()

#join start and end values/ratios
soc <- full_join(socStart1, socEnd, by=c("type", "group", "grpCode", "domain", "dimension", "indicator",
    "indCode"))

rm(socStart1, socEnd)

#calculate change between start and end periods for each indicator
soc1 <- soc %>%
  arrange(dimension, indCode) %>%
  mutate(ratioStart = 1 - ratioStart, ratioEnd = 1 - ratioEnd) %>%
  rowwise() %>%
  mutate(ratioStart = ifelse(indicator == "publicTrans", ratioEnd, ratioStart),
    diff = ratioEnd - ratioStart,
    betterWorse = ifelse(diff > 0, "worsening", "improving")) %>%
  ungroup()

rm(socData, soc)

soc2 <- soc1 %>% 
  mutate(indCode = factor(indCode, levels=c("NU1", "NU2", "HE1", "HE2", "ED1", "ED2",
    "IW1", "IW2", "WA1", "WA2", "EN1", "EN2", "CO1", "CO2", "HO1", "EQ1", "EQ2",
    "SC1", "SC2", "PV1", "PJ1", "PJ2"))) %>%
  rowwise() %>%
  mutate(weight = ifelse(dimension == "housing" || dimension == "political voice", 100, 50),
    diffBetter = ifelse(diff <= 0, abs(diff), NA),
    diffWorse = ifelse(diff <= 0, NA, diff),
    mainBetter = ifelse(diff <= 0, ratioStart - diffBetter, NA),
    mainWorse = ifelse(diff > 0, ratioEnd - diffWorse, NA)) %>%
  ungroup()

rm(soc1)
#---------------------------------------------------------------------------------------------------------
#prep visual vars
#---------------------------------------------------------------------------------------------------------
#gather data and calculate x-axis bar positions
socChart <- soc2 %>%
  select(-valueStart, -ratioStart, -valueEnd, -ratioEnd, -diff) %>%
  pivot_longer(c(10:13), names_to = "changeBar", values_to = "value") %>%
  group_by(changeBar) %>%
  mutate(pos = 0.5 * (cumsum(weight) + cumsum(c(0, weight[-length(weight)])))) %>%
  ungroup()

#define colours
colours <- c("mainBetter"="#cc0243", "diffBetter" = "#febbd1", 
  "mainWorse" = "#cc0243", "diffWorse"="#920130") # #f68f98 #a51523

#define dimension labels
dimLabs <- socChart %>%
  count(dimension) %>%
  select(-n) %>%
  mutate(pos = seq(50, 1150, 100),
    dimLab.ch = c("food", "health", "education", "income\n& work", "water", "energy", "connectivity",
	"housing", "equality", "social\ncohesion", "political\nvoice", "peace &\njustice"),
    dimLabs = factor(dimLab.ch, levels=c("food", "health", "education", "income\n& work", "water", "energy", "connectivity",
	"housing", "equality", "social\ncohesion", "political\nvoice", "peace &\njustice"))) %>%
  select(-dimension, -dimLab.ch)

#define axis labels
axisLabs <- tibble(labs.ch = c("under-\nnourished", "food\ninsecurity", "under-5\nmortality",
    "lack of\nhealth\nservices", "illiteracy\nrate", "incomplete\nsecondary\nschool", "societal\npoverty", "youth\nNEET",
    "unsafe\ndrinking\nwater", "unsafe\nsanitation", "lack of\nelectricity", "lack of\nclean fuels\nindoors",
    "lack of\npublic\ntransport", "lack of\ninternet", "slums or\ninformal\nhousing", "gender\ninequality",
    "racial\ninequality", "lack of\nsocial\nsupport", "income\ninequality", "autocratic\nregimes",
    "corruption", "homicide\nrate"),
  labs = factor(labs.ch, levels = c("food\ninsecurity", "under-\nnourished", "lack of\nhealth\nservices",
    "under-5\nmortality", "illiteracy\nrate", "incomplete\nsecondary\nschool", "societal\npoverty", "youth\nNEET",
    "unsafe\ndrinking\nwater", "unsafe\nsanitation", "lack of\nelectricity", "lack of\nclean fuels\nindoors",
    "lack of\ninternet", "lack of\npublic\ntransport", "slums or\ninformal\nhousing", "gender\ninequality",
    "racial\ninequality", "lack of\nsocial\nsupport", "income\ninequality", "autocratic\nregimes",
    "corruption", "homicide\nrate"))) %>% select(-labs.ch)

#get top column positions
colLabs <- soc2 %>%
  select(dimension, indicator, indCode, ratioStart, ratioEnd) %>%
  rowwise() %>%
  mutate(topVal = max(ratioStart, ratioEnd)) %>%
  ungroup() %>%
  cbind(axisLabs) %>%
  select(-ratioStart, -ratioEnd) %>% tibble()

#get xpos values for labels
pos <- socChart %>%
  select(dimension, indicator, indCode, pos) %>%
  group_by(dimension, indicator, indCode) %>%
  summarise(pos = mean(pos)) %>%
  ungroup() %>%
  arrange(dimension, indCode)

colLabs1 <- left_join(colLabs, pos, by=c("dimension", "indicator", "indCode")) %>%
  mutate(topVal = ifelse(indicator %in% c("UHCindex", "secondarySchool", "drinkingH2O", 
    "energyIndoor", "publicTrans", "urbanSlums"), topVal + 0.07,
      ifelse(indicator %in% c("internet", "racialEquality"), 0.85,
      ifelse(indicator == "controlCorruption", topVal + 0.03, topVal + 0.05))),
    constVal = 0.84,
    myCol = "black")

rm(colLabs, pos)

#---------------------------------------------------------------------------------------------------------
#plot!
#---------------------------------------------------------------------------------------------------------
socBars <- ggplot(socChart, aes(x=pos, y=value, width=weight-2, group=changeBar)) +
  geom_bar(aes(fill=changeBar), stat="identity") + 
  geom_vline(xintercept = seq(100,1100,100), colour = "#ffffff", lwd=1.5) +
  geom_vline(xintercept = seq(100,1100,100), colour = "#f0f0f0", lwd=0.5) +
  geom_hline(yintercept = 0, colour="#227443", lwd=2.5) +
  annotate("rect", xmin=851, xmax=897, ymin=0, ymax=2, alpha=0.2) +
  annotate("text", x = colLabs1$pos, y = colLabs1$constVal, label = colLabs1$labs,
    colour = colLabs1$myCol, vjust=1, size=1.58) +
  scale_fill_manual(name = "Change in\nsocial shortfall,\n2022 versus 2000", limits=c("mainBetter", "mainWorse", "diffBetter", "diffWorse"),
    labels=c("Reference1", "Reference2", "Improving from 2000", "Worsening from 2000"), values=colours) +
  coord_cartesian(ylim=c(1,0)) +
  scale_y_reverse(labels = scales::percent_format(big.mark=","), expand = c(0,0.01)) +
  scale_x_continuous(labels = dimLabs$dimLabs, breaks=dimLabs$pos, position = "top", expand=c(0,0.05)) +
  labs(x=element_blank(), y="Social shortfall") +
  theme_classic() +
  theme(
    plot.margin = margin(0.5, 0.1, 0.1, 0.1, "cm"),
    panel.grid.major.x = element_blank(),
    panel.grid.minor.x = element_blank(),
    panel.grid.minor.y = element_blank(),
    legend.position = "none",
    axis.title = element_text(size=8),
    axis.text = element_text(size=6),
    axis.line = element_blank(),
    axis.ticks.x = element_blank())

rm(socChart, colours, axisLabs, colLabs1, dimLabs)

#-------------------------------------------------------------------------------------------------
#					PREP ECOLOGICAL VARIABLES 
#-------------------------------------------------------------------------------------------------
#get global ecological data
ecoData <- myData6 %>% 
  filter(type == "global doughnut", domain == "ecological")

#get 2-year average 2000-01 values for ecological indicators, except ozone
ecoStart <- ecoData %>%
  filter(date %in% c(2000,2001), indicator != "totalOzone") %>%
  select(-populationTotal, -GNIperCap) %>%
  group_by(type, group, grpCode, domain, dimension, indicator, indCode) %>%
  summarise(valueStart = mean(value, na.rm=T),
    ratioStart = mean(ratio, na.rm=T)) %>%
  ungroup()

#get 5-year average 2000-2004 values for ozone
ecoStartOz <- ecoData %>%
  filter(date %in% c(2000:2004), indicator == "totalOzone") %>%
  select(-populationTotal, -GNIperCap) %>%
  group_by(type, group, grpCode, domain, dimension, indicator, indCode) %>%
  summarise(valueStart = mean(value, na.rm=T),
    ratioStart = mean(ratio, na.rm=T)) %>%
  ungroup()

ecoStart1 <- rbind(ecoStart, ecoStartOz) %>%
  arrange(dimension, indCode)

rm(ecoStart, ecoStartOz)

#get 2-year avg 2020-21 values for ecological indicators, except ozone
ecoEnd <- ecoData %>%
  filter(date %in% c(2021,2022), indicator != "totalOzone") %>%
  select(-populationTotal, -GNIperCap) %>%
  group_by(type, group, grpCode, domain, dimension, indicator, indCode) %>%
  summarise(valueEnd = mean(value, na.rm=T),
    ratioEnd = mean(ratio, na.rm=T)) %>%
  ungroup()

#get 5-year average 2017-2021 values for ozone
ecoEndOz <- ecoData %>%
  filter(date %in% c(2018:2022), indicator == "totalOzone") %>%
  select(-populationTotal, -GNIperCap) %>%
  group_by(type, group, grpCode, domain, dimension, indicator, indCode) %>%
  summarise(valueEnd = mean(value, na.rm=T),
    ratioEnd = mean(ratio, na.rm=T)) %>%
  ungroup()

ecoEnd1 <- rbind(ecoEnd, ecoEndOz) %>%
  arrange(dimension, indCode)

rm(ecoEnd, ecoEndOz)

#join start and end average values
eco <- full_join(ecoStart1, ecoEnd1, by=c("type", "group", "grpCode", "domain", "dimension", "indicator",
    "indCode")) 

rm(ecoStart1, ecoEnd1)

eco1 <- eco %>%
  rowwise() %>%
  mutate(diff = ratioEnd - ratioStart,
    betterWorse = ifelse(diff > 0, "worsening", "improving")) %>%
  ungroup()

rm(ecoData, eco)

eco2 <- eco1 %>% 
  mutate(indCode = factor(indCode, levels=c("CC1", "CC2", "OA1", "CP1", "NP1", "NP2", "AP1", "FD1", "FD2", 
    "LC1", "BB1", "BB2", "OD1"))) %>%
  rowwise() %>%
  mutate(weight = ifelse(dimension == "ocean acidification" || dimension == "chemical pollution" || 
	dimension == "land conversion" || dimension == "air pollution" || dimension == "ozone depletion", 100, 50),
    diffBetter = ifelse(diff <= 0, abs(diff), NA),
    diffWorse = ifelse(diff <= 0, NA, diff),
    mainBetter = ifelse(diff <= 0, ratioStart - diffBetter, NA),
    mainWorse = ifelse(diff > 0, ratioEnd - diffWorse, NA)) %>%
  ungroup() %>%
  arrange(dimension, indCode)

rm(eco1)
#---------------------------------------------------------------------------------------------------------
#prep visual vars
#---------------------------------------------------------------------------------------------------------
#gather data
ecoChart <- eco2 %>%
  select(-valueStart, -ratioStart, -valueEnd, -ratioEnd, -diff) %>%
  pivot_longer(c(10:13), names_to = "changeBar", values_to = "value") %>%
  group_by(changeBar) %>%
  mutate(pos = 0.5 * (cumsum(weight) + cumsum(c(0, weight[-length(weight)])))) %>%
  ungroup()

#define colours
colours <- c("mainBetter"="#cc0243", "diffBetter" = "#febbd1", 
  "mainWorse" = "#cc0243", "diffWorse"="#920130") # #f68f98 #a51523

#define dimension labels
dimLabs <- ecoChart %>%
  count(dimension) %>%
  select(-n) %>%
  mutate(pos = seq(50, 850, 100),
    dimLab.ch = c("climate\nchange", "ocean\nacidification", "chemical\npollution",
	"nutrient\npollution", "air\npollution", "freshwater\ndisruption", "land\nconversion", "biodiversity\nbreakdown",
	"ozone layer\ndepletion"),
    dimLabs = factor(dimLab.ch, levels=c("climate\nchange", "ocean\nacidification", "chemical\npollution",
	"nutrient\npollution", "air\npollution", "freshwater\ndisruption", "land\nconversion", "biodiversity\nbreakdown",
	"ozone layer\ndepletion"))) %>%
  select(-dimension, -dimLab.ch)

dimLabsY <- tibble(dimLabY = c("*", "0%", "100%", "200%", "300%"))

#define axis labels
axisLabs <- tibble(labs.ch = c("CO2\nconcentration", "radiative\nforcing", "aragonite\nsaturation",
    "hazardous\nchemicals", "phosphorus", "nitrogen", "interhemispheric\naerosols", "blue\nwater", "green\nwater",
    "forest\narea", "extinction\nrate", "hanpp", "stratospheric\nozone"),
  labs = factor(labs.ch, levels = c("CO2\nconcentration", "radiative\nforcing", "aragonite\nsaturation",
    "hazardous\nchemicals", "phosphorus", "nitrogen", "interhemispheric\naerosols", "blue\nwater", "green\nwater",
    "forest\narea", "extinction\nrate", "hanpp", "stratospheric\nozone"))) %>% select(-labs.ch)

#get top column positions
colLabs <- eco2 %>%
  select(dimension, indicator, indCode, ratioStart, ratioEnd) %>%
  rowwise() %>%
  mutate(topVal = max(ratioStart, ratioEnd)) %>%
  ungroup() %>%
  cbind(axisLabs) %>%
  select(-ratioStart, -ratioEnd) %>% tibble()

#get xpos values for labels
pos <- ecoChart %>%
  select(dimension, indicator, indCode, pos) %>%
  group_by(dimension, indicator, indCode) %>%
  summarise(pos = mean(pos)) %>%
  ungroup() %>%
  arrange(dimension, indCode)

colLabs1 <- left_join(colLabs, pos, by=c("dimension", "indicator", "indCode")) %>%
  mutate(topVal = ifelse(indicator %in% c("omega_a", "interhemAOD", "totalOzone"), 1.35,
      ifelse(indicator %in% c("chemicalsMt_Hzd", "extinction1900"), 4.4, topVal + 0.25)),
    constVal = 4.5,
    myCol = ifelse(indicator %in% c("chemicalsMt_Hzd", "extinction1900"), "white", "black")) 

rm(colLabs, pos)

#---------------------------------------------------------------------------------------------------------
#plot!
#---------------------------------------------------------------------------------------------------------
ecoBars <- ggplot(ecoChart, aes(x=pos, y=value, width = weight-2, group=changeBar)) +
  geom_bar(aes(fill=changeBar), stat="identity") + 
  geom_vline(xintercept = seq(100,800,100), colour = "#ffffff", lwd=1.5) +
  geom_vline(xintercept = seq(100,800,100), colour = "#f0f0f0", lwd=0.5) +
  geom_hline(yintercept = 1, colour="#227443", lwd=2.5) +
  annotate("text", x = colLabs1$pos, y = colLabs1$constVal, label = colLabs1$labs, 
    colour = colLabs1$myCol, vjust=1, size = 1.58) +
  scale_fill_manual(name = "Change in\necological overshoot,\n2021 versus 2000",
    limits=c("mainBetter", "mainWorse", "diffBetter", "diffWorse"),
    labels=c("Reference1", "Reference2", "Improving from 2000", "Worsening from 2000"), values=colours) +
  coord_cartesian(ylim=c(0,4.9)) +
  scale_y_continuous(labels = dimLabsY$dimLabY, breaks=seq(0,4,1), expand = c(0,0.01)) +
  scale_x_continuous(labels = dimLabs$dimLabs, breaks=dimLabs$pos, expand=c(0,0.05)) + #ecoChart$indicator
  labs(x=element_blank(), y="Ecological overshoot") +
  theme_classic() +
  theme(
    plot.margin = margin(0.1, 0.1, 0.5, 0.1, "cm"),
    panel.grid.major.x = element_blank(),
    panel.grid.minor.x = element_blank(),
    panel.grid.minor.y = element_blank(),
    legend.position = "none",
    axis.title = element_text(size=8),
    axis.text = element_text(size=6),
    axis.line = element_blank(),
    axis.ticks.x = element_blank())

rm(ecoChart, colours, axisLabs, colLabs1, dimLabs, dimLabsY)


#-----------------------------------------------------------------------------------------------
# merge charts into one figure and write baguette data to file
#-----------------------------------------------------------------------------------------------

ggarrange(ecoBars, socBars, ncol=1) #, labels=c("a", "b"), font.label=list(size=8)

#ggsave("./figures/7_baguette_R2.png", width = 183, height = 100, units = "mm", device = "png")

rm(ecoBars, socBars)
#-----------------------------------------------------------------------------------------------
ecoSoc <- rbind(eco2,soc2) %>%
  select(-diffBetter, -diffWorse, -mainBetter, -mainWorse, -weight) %>%
  mutate(ratioStart = ifelse(domain=="ecological", ratioStart-1, ratioStart),
    ratioEnd = ifelse(domain=="ecological", ratioEnd-1, ratioEnd))

#write_csv(ecoSoc, "./myData/7_20250112_baguetteData.csv")

rm(eco2, soc2, ecoSoc, myData6)