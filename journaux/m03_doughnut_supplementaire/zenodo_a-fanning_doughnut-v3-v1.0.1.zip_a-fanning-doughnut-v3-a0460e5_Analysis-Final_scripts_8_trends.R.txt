#This script estimates statistical linear trend lines from observed values

#read in data file if needed.
#myData6 <- read_csv("./myData/5_20250108_doughnutDat-boundariesRatios.csv") %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice")))

#read in non-interpolated data file to estimate statistical trends
myData1 <- read_csv("./myData/2_20250108_doughnutv3-data.csv")
#-------------------------------------------------------------------------------------------------
#add 2000-2017 hazardous chemicals data to myData1
hzdChem <- myData6 %>%
  filter(indicator == "chemicalsMt_Hzd") %>% 
  select(domain, dimension, type, group, indicator, date, populationTotal, GNIperCap, value) %>%
  rowwise() %>%
  mutate(value = ifelse(date > 2017, NA, value)) %>%
  ungroup()

myData2 <- rbind(myData1, hzdChem) %>%
  arrange(domain, dimension)

rm(hzdChem, myData1)
#-------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------
#			join ratio values to myData1 non-interpolated data  
#-------------------------------------------------------------------------------------------------
#get global ratios
ratios <- myData6 %>%
  filter(type == "global doughnut") %>%
  select(type, domain, dimension, group, grpCode, indicator, indCode, date, ratio) %>%
  rowwise() %>%
  mutate(ratio = ifelse(domain == "social", (1 - ratio)*100, (ratio-1)*100)) %>%
  ungroup()


lmData <- myData2 %>%
  filter(type == "global doughnut") %>%
  left_join(., ratios, by=c("domain", "dimension", "type", "group", "indicator", "date")) %>%
  select(-populationTotal, -GNIperCap) %>%
  relocate(value, .before=ratio) %>%
  relocate(indCode, .before=date) %>%
  relocate(grpCode, .before=indicator)

rm(ratios, myData2)

#---------------------------------------------------------------------------------------
#Drop NAs and transform date so 0 is 2000 (for a meaningful intercept coefficient) 
lmData1 <- lmData %>%
  drop_na() %>%
  rowwise() %>%
  mutate(t = date - 2000) %>%
  ungroup()  

rm(lmData)

#---------------------------------------------------------------------------------------
#little function to fit lm models by year
mod_fit <- function(data){
  lm(ratio ~ t, data=data)
}
#---------------------------------------------------------------------------------------
#estimate lm models by group and extract coefficients and fitted values
#mods <- lmData1 %>%
#  group_nest(domain, dimension, type, group, grpCode, indicator, indCode) %>%
#  mutate(model = map(data, mod_fit), 
#    glance = map(model, broom::glance),
#    tidy = map(model, broom::tidy),
#    augment = map(model, broom::augment))

mods <- lmData1 %>%
  group_nest(domain, dimension, type, group, grpCode, indicator, indCode) %>%
  mutate(model = map(data, mod_fit), 
    augment = map(model, broom::augment)) %>%
  rowwise() %>%
  mutate(glance = list(broom::glance(coeftest(model, df=Inf, vcov = NeweyWest(model, lag = 4, prewhite=FALSE), save=T))),
    tidy = list(broom::tidy(coeftest(model, df=Inf, vcov = NeweyWest(model, lag = 4, prewhite=FALSE))))) %>%
  ungroup()

#---------------------------------------------------------------------------------------
#get fitted values to visualise
mods_aug <- mods %>%
  unnest(augment) %>%
  select(domain, dimension, indicator, indCode, ratio, t, .fitted)
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
#	QUICK DIVE INTO WHY THE FOOD INDICATOR TRENDS MOVE IN OPPOSING DIRECTIONS (Ref 3)
#---------------------------------------------------------------------------------------
#get comparable time series for both indicators, starting from 2015

food <- lmData1 %>% filter(dimension == "food", date >= 2015) 

food1 <- food %>%
  group_nest(domain, dimension, type, group, grpCode, indicator, indCode) %>%
  mutate(model = map(data, mod_fit), 
    augment = map(model, broom::augment)) %>%
  rowwise() %>%
  mutate(glance = list(broom::glance(coeftest(model, df=Inf, vcov = NeweyWest(model, lag = 4, prewhite=FALSE), save=T))),
    tidy = list(broom::tidy(coeftest(model, df=Inf, vcov = NeweyWest(model, lag = 4, prewhite=FALSE))))) %>%
  ungroup()

food1 %>% unnest(glance, tidy)
# by comparing trends over comparable time series (2015-2022), 
# we estimate increasing deprivation for both food indicators, significant at 99.9% level:
# 0.3%pt per year for undernourishment and 1.1%pt per year for food insecurity. 

#---------------------------------------------------------------------------------------
#			EXTENDED DATA FIGURE 5 - social line charts
#---------------------------------------------------------------------------------------
#look at social data and fitted values
socData <- mods_aug %>%
  filter(domain == "social") %>%
  rowwise() %>%
  mutate(date = t + 2000) %>%
  ungroup() %>%
  mutate(dimension = factor(dimension, levels = c("food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice")),
    indCode = factor(indCode, levels=c("NU1", "NU2", "HE1", "HE2", "ED1", "ED2",
    "IW1", "IW2", "WA1", "WA2", "EN1", "EN2", "CO1", "CO2", "HO1", "EQ1", "EQ2",
    "SC1", "SC2", "PV1", "PJ1", "PJ2"))) %>%
  arrange(dimension, indCode)

#set 2-colour scheme by dimension 
cols <- c("NU1"="#7f7f7f", "NU2"="#262626", "HE1"="#7f7f7f", "HE2"="#262626", 
    "ED1"="#7f7f7f", "ED2"="#262626", "IW1"="#262626", "IW2"="#7f7f7f", "WA1"="#7f7f7f", 
    "WA2"="#262626", "EN1"="#7f7f7f", "EN2"="#262626", "CO1"="#7f7f7f", "CO2"="#262626", 
    "HO1"="#262626", "EQ1"="#262626", "SC1"="#7f7f7f", "SC2"="#262626", 
    "PV1"="#262626", "PJ1"="#262626", "PJ2"="#7f7f7f")


#set indicator labels for annotation
indicatorLabs <- socData %>%
  count(dimension, indCode, indicator) %>%
  select(-n) %>%
  mutate(indLabel.ch = c("undernourished", "food insecurity", "under-5 mortality",
    "lack of health services", "illiteracy rate", "incomplete secondary school", "societal poverty", "youth NEET",
    "unsafe drinking water", "unsafe sanitation", "lack of electricity", "lack of clean fuels indoors",
    "lack of public transport", "lack of internet", "slums or informal housing", "gender inequality",
    "lack of social support", "income inequality", "autocratic regimes",
    "perception of corruption", "homicide rate"))

#get regression data for annotation
eqnData <- mods %>%
  filter(domain == "social") %>%
  unnest(glance, tidy) %>%
  select(dimension, indicator, indCode, adjR2 = adj.r.squared, nobs, term, estimate) %>%
  pivot_wider(names_from = "term", values_from = "estimate") %>%
  rename(intercept = `(Intercept)`, slope = t) %>%
  mutate(dimension = factor(dimension, levels = c("food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice")),
    indCode = factor(indCode, levels=c("NU1", "NU2", "HE1", "HE2", "ED1", "ED2",
    "IW1", "IW2", "WA1", "WA2", "EN1", "EN2", "CO1", "CO2", "HO1", "EQ1", "EQ2",
    "SC1", "SC2", "PV1", "PJ1", "PJ2"))) 

#join equation data to labels
indicatorLabs1 <- left_join(indicatorLabs, eqnData, by=c("dimension", "indicator", "indCode")) %>%
  rowwise() %>%
  mutate(slope = ifelse(indicator == "publicTrans", 0, slope),
    formula = sprintf("italic(y) == %.0f %+.1f * italic(x) * ',' ~~ italic(r)^2 ~ '=' ~ %.2f", 
      round(intercept, 0), round(slope, 1), round(adjR2, 2))) %>%
  ungroup()

pos <- tibble(
  x1 = c(2000, 2012, 2000, 2012, 2012, 2000, 2000, 2012, 2012, 2000, 2012, 2000, 2000, 2012, 2000, 2000, 2012, 2000, 2000, 2000, 2012), 
  x2 = c(2000, 2012, 2000, 2012, 2012, 2000, 2000, 2012, 2012, 2000, 2012, 2000, 2000, 2012, 2000, 2000, 2012, 2000, 2000, 2000, 2012), 
  y1 = c(1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05),
  y2 = c(1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13))

indicatorLabs2 <- cbind(indicatorLabs1, pos)
#--------------------------------------------------------------------------------------------------
#plot!

ggplot(data = socData %>% mutate(ratio = ratio/100, .fitted = .fitted/100)) +
  geom_hline(yintercept = 0, col = "#227443", lwd=1.5) +
  geom_line(aes(x=date, y=.fitted, col=indCode), lwd=0.5) + 
  geom_point(aes(x=date, y=ratio, col=indCode), size=0.6) + 
  coord_cartesian(ylim=c(1.15, 0)) +
  scale_y_reverse(labels=scales::percent, breaks=seq(0,1,0.25)) + 
  scale_colour_manual(values=cols) +
  facet_wrap(~dimension, ncol=3) +
  geom_text(data = indicatorLabs2, aes(x = x1, y = y1, label = indLabel.ch, col=indCode), hjust=0, size=2) +
  geom_text(data = indicatorLabs2, aes(x = x2, y = y2, label = formula, col=indCode), parse=TRUE, hjust=0, size=2) +
  labs(x = "Year", y = "Social shortfall (0% = social foundation)") +
  theme_chart_SMALLM +
  theme(legend.position="none",
    panel.grid=element_blank())

#save Extended Data Figure 5 to file
#ggsave("./figures/ExtDataFig5_socialIndicators-dataAndTrends_final.png", width = 180, height = 184, units = "mm", device="png")

rm(cols, indicatorLabs, eqnData, indicatorLabs1, pos, indicatorLabs2)

#---------------------------------------------------------------------------------------
#			EXTENDED DATA FIGURE 6 - ecological line charts
#---------------------------------------------------------------------------------------
#Look at ecological values and fitted values
ecoData <- mods_aug %>%
  filter(domain == "ecological") %>%
  rowwise() %>%
  mutate(date = t + 2000) %>%
  ungroup() %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion")),
    indicator = factor(indicator, levels = c("co2_ppm", "erf_wm2", "omega_a", "chemicalsMt_Hzd", "phosphorusMt", "nitrogenMt",
      "interhemAOD", "blueDev", "soilDev", "forestAreaMKM2", "extinction1900", "hanppGtC", "totalOzone")))
  
#set 2-colour scheme by dimension 
#cols <- c("co2_ppm"="#f6914c", "erf_wm2"="#9f1523", "omega_a"="#6eaf46", "chemicalsMt_Hzd"="#9f1523", "phosphorusMt"="#9f1523", 
 # "nitrogenMt"="#f6914c", "blueDev"="#9f1523", "soilDev"="#f6914c", "forestAreaMKM2"="#9f1523", "extinction1900"="#9f1523",
  #"hanppGtC"="#f6914c", "interhemAOD"="#6eaf46", "totalOzone"="#6eaf46")

cols <- c("co2_ppm"="#7f7f7f", "erf_wm2"="#262626", "omega_a"="#262626", "chemicalsMt_Hzd"="#262626", "phosphorusMt"="#262626", 
  "nitrogenMt"="#7f7f7f", "interhemAOD"="#262626", "blueDev"="#262626", "soilDev"="#7f7f7f", "forestAreaMKM2"="#262626",
  "extinction1900"="#262626", "hanppGtC"="#7f7f7f", "totalOzone"="#262626")


#set y-axis labels
dimLabsY <- tibble(dimLabY = c("*", "0%", "100%", "200%", "300%"))

#set indicator labels for annotation
indicatorLabs <- ecoData %>%
  count(dimension, indicator) %>%
  select(-n) %>%
  mutate(indLabel.ch = c("CO2 concentration", "radiative forcing", "aragonite saturation", "hazardous chemicals", "phosphorus",
    "nitrogen", "interhemispheric aerosols", "blue water", "green water", "forest area", "extinction rate", "hanpp",
    "stratospheric ozone"))

#get regression data for annotation
eqnData <- mods %>%
  filter(domain == "ecological") %>%
  unnest(glance, tidy) %>%
  select(dimension, indicator, adjR2 = adj.r.squared, nobs, term, estimate) %>%
  spread(term, estimate) %>%
  rename(intercept = `(Intercept)`, slope = t) %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion")),
    indicator = factor(indicator, levels = c("co2_ppm", "erf_wm2", "omega_a", "chemicalsMt_Hzd", "phosphorusMt", "nitrogenMt",
      "interhemAOD", "blueDev", "soilDev", "forestAreaMKM2", "extinction1900", "hanppGtC", "totalOzone")))

#join equation data and indicator labels
indicatorLabs1 <- left_join(indicatorLabs, eqnData, by=c("dimension", "indicator")) %>%
  rowwise() %>%
  mutate(adjR2 = ifelse(indicator %in% c("extinction1900", "interhemAOD"),0, adjR2),
    formula = sprintf("italic(y) == %.1f %+.1f * italic(x) * ',' ~~ italic(r)^2 ~ '=' ~ %.2f", 
      round(intercept, 0), round(slope, 1), round(adjR2, 3))) %>%
  ungroup()

#set label positions for indicators (x1, y1) and equations (x2, y2)
pos <- tibble(
  x1 = c(2011, 2000, 2000, 2000, 2000, 2011, 2000, 2011, 2000, 2000, 2011, 2000, 2000), 
  x2 = c(2011, 2000, 2000, 2000, 2000, 2011, 2000, 2011, 2000, 2000, 2011, 2000, 2000), 
  y1 = c(4.2, 4.2, 4.2, 4.2, 4.2, 4.2, 4.2, 4.2, 4.2, 4.2, 4.2, 4.2, 4.2), 
  y2 = c(3.9, 3.9, 3.9, 3.9, 3.9, 3.9, 3.9, 3.9, 3.9, 3.9, 3.9, 3.9, 3.9))

#join coordinates to labels 
indicatorLabs2 <- cbind(indicatorLabs1, pos)

#--------------------------------------------------------------------------------------------------
#plot!

ggplot(data = ecoData %>% mutate(ratio = (ratio/100)+1, .fitted = (.fitted/100)+1)) +
  geom_hline(yintercept = 1, col = "#227443", lwd=1.5) +
  geom_line(aes(x=date, y=.fitted, col=indicator), lwd=0.5) + 
  geom_point(aes(x=date, y=ratio, col=indicator), size=0.6) + 
  scale_y_continuous(labels=dimLabsY$dimLabY, breaks=seq(0,4,1)) +
  scale_colour_manual(values=cols) +
  coord_cartesian(ylim=c(0,4.2)) +
  facet_wrap(~dimension, ncol=3) +
  geom_text(data = indicatorLabs2, aes(x = x1, y = y1, label = indLabel.ch, col=indicator), hjust=0, size=2) +
  geom_text(data = indicatorLabs2, aes(x = x2, y = y2, label = formula, col=indicator), parse=TRUE, hjust=0, size=2) +
  labs(x = "Year", y = "Ecological overshoot (0% = planetary boundary)") +
  theme_chart_SMALLM +
  theme(legend.position="none",
    panel.grid=element_blank())

#save Figure 4 to file
#ggsave("./figures/ExtDatFig6_ecologicalIndicators-dataAndTrends_final.png", width = 180, height = 140, units = "mm", device="png")

rm(cols, indicatorLabs, eqnData, indicatorLabs1, pos, indicatorLabs2, dimLabsY)
#---------------------------------------------------------------------------------------
##write time series and fitted values to file

obsFit <- rbind(ecoData, socData) %>%
  select(-t) %>%
  relocate(date, .before=ratio) %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "freshwater disruption", "land conversion", "biodiversity breakdown", "air pollution",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice"))) %>%
  arrange(domain, dimension, indCode)


#write_csv(obsFit, "./myData/8_20250515_ratios-observedAndFitted.csv")

rm(mods_aug, obsFit, socData, ecoData)
#---------------------------------------------------------------------------------------
#get full regression results
mods_reg <- mods %>%
  unnest(glance, tidy) %>%
  select(domain, dimension, indicator, indCode, adjr2 = adj.r.squared, lmPval = p.value) %>%
  group_by(domain, dimension, indicator, indCode) %>%
  summarise(adjr2 = mean(adjr2, na.rm=T),
    lmPval = mean(lmPval, na.rm=T)) %>%
  ungroup

#get coefficients
mods_coef1 <- mods %>%
  unnest(glance, tidy) %>%
  select(domain, dimension, indicator, indCode, term, estimate) %>%
  pivot_wider(names_from = "term", values_from = "estimate") %>%
  rename(intercept = `(Intercept)`, slope = t)

#get std errors
mods_coef2 <- mods %>%
  unnest(glance, tidy) %>%
  select(domain, dimension, indicator, indCode, term, stdError = std.error) %>%
  pivot_wider(names_from = "term", values_from = "stdError") %>%
  rename(stdErrorIntercept = `(Intercept)`, stdErrorSlope = t)

#get pVals
mods_coef3 <- mods %>%
  unnest(glance, tidy) %>%
  select(domain, dimension, indicator, indCode, term, coefPval = p.value1) %>%
  pivot_wider(names_from = "term", values_from = "coefPval") %>%
  rename(pValIntercept = `(Intercept)`, pValSlope = t)

#join
myReg <- full_join(mods_coef1, mods_coef2, by=c("domain", "dimension", "indicator", "indCode"))
myReg1 <- full_join(myReg, mods_coef3, by=c("domain", "dimension", "indicator", "indCode"))

myReg2 <- full_join(myReg1, mods_reg, by=c("domain", "dimension", "indicator", "indCode")) %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "freshwater disruption", "land conversion", "biodiversity breakdown", "air pollution",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice"))) %>%
  arrange(domain, dimension, indCode)

rm(mods_reg, mods_coef1, mods_coef2, mods_coef3, myReg, myReg1)

#write regression results to file
#write_csv(myReg2, "./myData/8_20250515_lmModelCoefficients.csv")

rm(mods, myReg2, mod_fit, lmData1, myData6)


