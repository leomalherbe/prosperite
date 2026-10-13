# This script calculates linear rates of change needed to eliminate social shortfall and ecological overshoot
# for each indicator by 2050, based on current levels.

#read in cleaned data file
myData6 <- read_csv("./myData/5_20250108_doughnutDat-boundariesRatios.csv") %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice"))) 

ecoSoc <- read_csv("./myData/7_20250112_baguetteData.csv") %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice")))

lmData <- read_csv("./myData/8_20250515_lmModelCoefficients.csv") %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice"))) %>%
  select(-lmPval, -intercept, -stdErrorIntercept, -pValIntercept) %>%
  add_column(type = "global doughnut", group = "World", grpCode = "WLD") %>%
  relocate(type, group, grpCode)

#-------------------------------------------------------------------------------------------------------------------
#get 2021-22 overshoot/shortfall values and calculate linear rates of change needed to live within the Doughnut
# by 2030 for the social foundation and 2050 for the ecological ceiling.

ecoSoc1 <- ecoSoc %>%
  add_column(endYear = 0) %>% 
  rowwise() %>%
  mutate(t = ifelse(domain == "ecological", 2050-2022, 2030-2022),
    slopeD = (endYear - ratioEnd)/t*100) %>%
  ungroup() %>%
  select(-endYear)

rm(ecoSoc)

#add estimated trends based on observed ratios to ecoSoc to have table data on file
ecoSoc2 <- left_join(ecoSoc1, lmData, by=c("type", "group", "grpCode", "domain", "dimension", "indicator", "indCode")) %>%
  arrange(type, domain, dimension, indCode) %>%
  relocate(t, slopeD, .after=adjr2)

rm(ecoSoc1, lmData)

#calculate/round scale of ambition needed
ecoSoc3 <- ecoSoc2 %>%
  mutate(valueStart = round(valueStart, 3),
    valueEnd = round(valueEnd, 3),
    ratioStart = round(ratioStart*100, 3),
    ratioEnd = round(ratioEnd*100, 3),
    diff = round(diff*100, 3),
    slopeD = round(slopeD, 3),
    slope = round(slope, 3),
    stdErrorSlope = round(stdErrorSlope, 5),
    pValSlope = round(pValSlope, 5),
    adjr2 = round(adjr2, 4))

rm(ecoSoc2)
#------------------------------------------------------------------------------------------
#write this data to file as input to Tables 1 and 2, and do final clean up in Excel.
#write_csv(ecoSoc3, "./myData/9_20250516_Doughnut-GlobalTablesData.csv")

rm(ecoSoc3, myData6)