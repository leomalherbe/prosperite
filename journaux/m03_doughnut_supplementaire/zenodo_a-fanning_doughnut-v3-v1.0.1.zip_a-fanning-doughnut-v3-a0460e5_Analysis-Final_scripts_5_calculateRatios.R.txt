# This script calculates social and ecological performance with respect to global and national aggregate boundaries

#read in latest dataset, if needed
#myData4 <- read_csv("./myData/4_20250108_doughnutData-boundaries.csv") %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice")))
#---------------------------------------------------------------------------------------
#					GLOBAL
#---------------------------------------------------------------------------------------
#Calculate global overshoot and shortfall ratios (put blueDev in percentage terms)
global <- myData4 %>%
  filter(type == "global doughnut") %>%
  rowwise() %>%
  mutate(value = ifelse(indicator == "blueDev", value*100, value)) %>%
  ungroup()

global1 <- global %>%
  rowwise() %>%
  mutate(ratio = ifelse(indicator == "co2_ppm", (value - 280)/(boundary - 280), #normalised to pre-industrial 280 ppm
	  ifelse(indicator == "omega_a", (1-value/3.44)/(1-boundary/3.44), #normalised to pre-industrial 3.44 from Rockstrom et al
	  ifelse(indicator == "totalOzone", (1-value/290)/(1-boundary/290), #normalised to pre-industrial 290 from Rockstrom et al
	  ifelse(indicator == "forestAreaMKM2", (1 - value/63.87)/(1 - boundary/63.87),#note 47.9 million km2 is from Steffen et al
	  ifelse(indicator == "interhemAOD", (value - 0.03)/(boundary - 0.03), #normalised to pre-industrial 0.03 from Richardson et al 
	  ifelse(domain == "social", (100-value)/100, value/boundary))))))) %>%
  ungroup()

rm(global)

#---------------------------------------------------------------------------------------
#Look at normalised ecological values
ecoData <- global1 %>%
  filter(domain == "ecological") %>%
  mutate(indicator = factor(indicator, levels = c("co2_ppm", "erf_wm2", "omega_a", "chemicalsMt_Hzd", "phosphorusMt", "nitrogenMt",
    "blueDev", "soilDev", "forestAreaMKM2", "extinction1900", "hanppGtC", "interhemAOD", "totalOzone")))
  
ggplot(data=ecoData, aes(x=date)) +
  geom_hline(yintercept = 1, col = "black", linetype=6, lwd=0.8, alpha=0.5) +
  geom_line(data=ecoData, aes(y=ratio, colour=indicator), lwd=0.8) +
  geom_point(data=ecoData, aes(y=ratio, colour=indicator), size=1.5) +
  #geom_ribbon(data=ecoData %>% filter(date > 2021), aes(ymin=ratio_low, ymax=ratio_high, fill=indicator), alpha=0.3) +
  #geom_line(data=ecoData %>% filter(date > 2021), aes(y=ratio, colour=indicator), alpha=0.6, lwd=0.8) +
  scale_y_continuous(labels=scales::percent_format(big.mark=",")) +
  coord_cartesian(ylim=c(0,4)) +
  facet_wrap(~dimension, ncol=4) +
  labs(subtitle = "The ecological ceiling and its indicators of global overshoot", x = "Year", y = "Ecological overshoot (100% = planetary boundary)") +
  theme_chart_SMALLM

#ggsave("./figures/5_ecologicalIndicators_400pctCut.png", device="png")
#---------------------------------------------------------------------------------------
#Look at normalised social values
socData <- global1 %>%
  filter(domain == "social") %>% 
  mutate(indicator = factor(indicator, levels=c("undernourishment", "foodInsecurity", "under5death", "UHCindex", "adultLiteracy",
    "secondarySchool", "societalPoverty", "youthNEET", "drinkingH2O", "sanitation", "energyAccess", "energyIndoor", "publicTrans", "internet", 
    "urbanSlums", "genderGapIndex", "racialInequality", "socialSupport", "palma", "govRegimes", "controlCorruption", "homicideOver5")),
  ratio = 1-ratio)
  
ggplot(data=socData, aes(x=date)) +
  geom_hline(yintercept = 0, col = "black", linetype=6, lwd=0.8, alpha=0.5) +
  geom_line(data=socData, aes(y=ratio, colour=indicator), lwd=0.8) +
  geom_point(date=socData, aes(y=ratio, colour=indicator), size=1.3) +
  #geom_ribbon(data=socData %>% filter(date > 2021), aes(ymin=ratio_low, ymax=ratio_high, fill=indicator), alpha=0.3) +
  #geom_line(data=socData %>% filter(date > 2021), aes(y=ratio, colour=indicator), alpha=0.6, lwd=0.8) +
  scale_y_reverse(labels=scales::percent) +
  facet_wrap(~dimension, ncol=4) +
  labs(subtitle = "The social foundation and its indicators of global shortfall", x = "Year", y = "Social shortfall (0% = social foundation)") +
  theme_chart_SMALLM

#ggsave("./figures/5_socialIndicators.png", device="png")


rm(ecoData, socData)

#---------------------------------------------------------------------------------------
#					NATIONAL AGGREGATES
#---------------------------------------------------------------------------------------
#Calculate national overshoot and shortfall ratios 
national <- myData4 %>%
  filter(type == "national aggregate")

national1 <- national %>%
  rowwise() %>%
  mutate(ratio = ifelse(domain == "social", (100-value)/100, value/boundary)) %>%
  ungroup() 

rm(national)

#---------------------------------------------------------------------------------------
#Look at normalised ecological values
ecoData <- national1 %>%
  filter(domain == "ecological", group != "World", date == 2017) %>%
  mutate(indicator = factor(indicator, levels = c("co2_footprint", "omega_a_footprint", "hzdChemicals_footprint",
    "P_footprint", "N_footprint", "airPollution_footprint", "blueH2O_footprint","land_footprint", "species_footprint",
    "hanpp_footprint", "ozone_footprint")))
  
ggplot(data=ecoData, aes(x=indicator)) +
  geom_hline(yintercept = 1, col = "black", linetype=6, lwd=0.8, alpha=0.5) +
  geom_col(aes(y=ratio, fill=group), position="dodge2") +
  scale_y_continuous(labels=scales::percent_format(big.mark=",")) +
  #coord_cartesian(ylim=c(0,4)) +
  labs(subtitle = "The ecological ceiling and its indicators of overshoot by national income group in 2017", x = "Indicator", y = "Ecological overshoot (100% = planetary boundary)") +
  theme_chart_SMALLM +
  theme(axis.text.x = element_text(angle = 45, vjust = 0.6, hjust = 0.7))

#ggsave("./figures/5_ecologicalIndicators_countryGroups.png", device="png")
#---------------------------------------------------------------------------------------
#Look at normalised social values
socData <- national1 %>%
  filter(domain == "social", group != "World", date == 2017) %>% 
  mutate(indicator = factor(indicator, levels=c("undernourishment", "foodInsecurity", "under5death", "UHCindex", "adultLiteracy",
    "secondarySchool", "societalPoverty", "youthNEET", "drinkingH2O", "sanitation", "energyAccess", "energyIndoor", "publicTrans", "internet", 
    "urbanSlums", "genderGapIndex", "racialInequality", "socialSupport", "palma", "govRegimes", "controlCorruption", "homicideOver5")),
  ratio = 1-ratio)
  
ggplot(data=socData, aes(x=indicator)) +
  geom_hline(yintercept = 0, col = "black", linetype=6, lwd=0.8, alpha=0.5) +
  geom_col(aes(y=ratio, fill=group), position="dodge2") +
  scale_y_reverse(labels=scales::percent) +
  #facet_wrap(~dimension) +
  labs(subtitle = "The social foundation and its indicators of shortfall by national income group in 2017", x = "Indicator", y = "Social shortfall (0% = social foundation)") +
  theme_chart_SMALLM + 
  theme(axis.text.x = element_text(angle = 45, vjust = 0.6, hjust = 0.7))

#ggsave("./figures/5_socialIndicators_countryGroups.png", device="png")


rm(ecoData, socData)

#---------------------------------------------------------------------------------------
#		re-join global doughnut and national aggregate with respective ratios
#---------------------------------------------------------------------------------------
myData5 <- rbind(global1, national1) %>%
  arrange(domain, dimension, type, indicator, group, date)

rm(myData4, global1, national1)


#---------------------------------------------------------------------------------------
#Add groupCodes and indicatorCodes
myData6 <- myData5 %>%
  rowwise() %>%
  mutate(grpCode = ifelse(group == "Bottom-40", "B40", 
	ifelse(group == "Middle-40", "M40", 
	ifelse(group == "Top-20", "T20", 
	ifelse(group == "World", "WLD", "ERROR")))),
    indCode = ifelse(indicator == "co2_ppm", "CC1",
	ifelse(indicator == "erf_wm2", "CC2",
	ifelse(indicator == "co2_footprint", "CC3",
	ifelse(indicator == "omega_a", "OA1",
	ifelse(indicator == "omega_a_footprint", "OA3",
	ifelse(indicator == "chemicalsMt_Hzd", "CP1",
	ifelse(indicator == "hzdChemicals_footprint", "CP3",
	ifelse(indicator == "phosphorusMt", "NP1",
	ifelse(indicator == "nitrogenMt", "NP2",
	ifelse(indicator == "P_footprint", "NP3",
	ifelse(indicator == "N_footprint", "NP4",
	ifelse(indicator == "interhemAOD", "AP1",
	ifelse(indicator == "airPollution_footprint", "AP3",
	ifelse(indicator == "blueDev", "FD1",
	ifelse(indicator == "soilDev", "FD2",
	ifelse(indicator == "blueH2O_footprint", "FD3",
	ifelse(indicator == "forestAreaMKM2", "LC1",
	ifelse(indicator == "land_footprint", "LC3",
	ifelse(indicator == "extinction1900", "BB1",
	ifelse(indicator == "hanppGtC", "BB2",
	ifelse(indicator == "species_footprint", "BB3",
	ifelse(indicator == "hanpp_footprint", "BB4",
	ifelse(indicator == "totalOzone", "OD1",
	ifelse(indicator == "ozone_footprint", "OD3",
	ifelse(indicator == "undernourishment", "NU1",
	ifelse(indicator == "foodInsecurity", "NU2",
	ifelse(indicator == "under5death", "HE1",
	ifelse(indicator == "UHCindex", "HE2",
	ifelse(indicator == "adultLiteracy", "ED1",
	ifelse(indicator == "secondarySchool", "ED2",
	ifelse(indicator == "societalPoverty", "IW1",
	ifelse(indicator == "youthNEET", "IW2",
	ifelse(indicator == "drinkingH2O", "WA1",
	ifelse(indicator == "sanitation", "WA2",
	ifelse(indicator == "energyAccess", "EN1",
	ifelse(indicator == "energyIndoor", "EN2",
	ifelse(indicator == "publicTrans", "CO1",
	ifelse(indicator == "internet", "CO2",
	ifelse(indicator == "urbanSlums", "HO1",
	ifelse(indicator == "genderGapIndex", "EQ1",
	ifelse(indicator == "racialInequality", "EQ2",
	ifelse(indicator == "socialSupport", "SC1",
	ifelse(indicator == "palma", "SC2",
	ifelse(indicator == "govRegimes", "PV1",
	ifelse(indicator == "controlCorruption", "PJ1",
	ifelse(indicator == "homicideOver5", "PJ2", "ERROR"))))))))))))))))))))))))))))))))))))))))))))))) %>%
  ungroup() %>%
  relocate(grpCode, .after=group) %>%
  relocate(indCode, .after=indicator) 

rm(myData5)

#-----------------------------------------------------------------------------------
#					write to file
#-------------------------------------------------------------------------------------
#write_csv(myData6, "./myData/5_20250108_doughnutDat-boundariesRatios.csv")

rm(myData6)

