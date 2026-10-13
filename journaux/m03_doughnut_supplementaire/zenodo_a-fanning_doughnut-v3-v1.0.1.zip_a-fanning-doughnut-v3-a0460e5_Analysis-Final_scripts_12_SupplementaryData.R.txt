#This script outputs a near-final Supplementary Data spreadsheet.
#Tab 1: global analysis data all years (with indicator units)
#Tab 2: global historical trend full regression estimates
#Tab 3: national groups 2017 analysis data (with indicator units) 
#-----------------------------------------------------------------------------------------------------------------------
#read in cleaned global data file
myData6 <- read_csv("./myData/5_20250108_doughnutDat-boundariesRatios.csv") %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice")))

#read in regression data
lmData <- read_csv("./myData/8_20250515_lmModelCoefficients.csv") %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice"))) %>%
  arrange(domain, dimension, indCode)

#-----------------------------------------------------------------------------------------------------------------------
#prep 2000-2022 supplementary global dataset with units

allYears <- myData6 %>%
  filter(type == "global doughnut") %>%
  rowwise() %>%
  mutate(shortfallOvershoot_pct = ifelse(domain == "social", (1 - ratio)*100, (ratio-1)*100)) %>%
  ungroup() %>%
  select(-populationTotal, -GNIperCap, -ratio)
  
#unit tibble
units <- allYears %>% 
  count(domain, dimension, indCode, indicator) %>%
  select(-n) %>%
  mutate(unit = c("ppm CO2", "Watt per m2", "omega aragonite", "million tonnes", "million tonnes P", "million tonnes N",
    "interhemispheric AOD", "percent", "percent", "million km2", "extinctions per million species-years", "billion tonnes C", 
    "Dobson units", "percent", "percent", "percent", "percent", "percent", "percent", "percent", "percent", "percent", 
    "percent", "percent", "percent", "percent", "percent", "percent", "0-100 scale", "Not available", "percent", "percent",
    "percent", "percent", "percent")) 

#merge units with data
allYears1 <- left_join(allYears, units, by=c("domain", "dimension", "indCode", "indicator")) %>%
  relocate(unit, .before=date) %>%
  mutate(value = round(value,digits=2),
    shortfallOvershoot_pct = round(shortfallOvershoot_pct, digits=1)) %>%
  rowwise() %>%
  mutate(indicator = ifelse(indCode == "EQ1", "genderInequalityIndex", indicator)) %>%
  ungroup() %>%
  arrange(domain, dimension, indCode)

#write to file
#write_csv(allYears1, "./myData/12_20250515_globalDoughnutData_2000-2022.csv")

rm(allYears, units, allYears1)
#-----------------------------------------------------------------------------------------------------------------------
#prep global regression results supplementary data
regData <- lmData %>%
  select(domain, dimension, indicator, indCode, slope, SE_slope = stdErrorSlope, `p-value_slope` = pValSlope,
    intercept, SE_intercept = stdErrorIntercept, `p-value_intercept` = pValIntercept, 
    `adj-R2`=adjr2, `p-value_regression` = lmPval) %>%
  mutate(slope = round(slope, digits=3), 
    intercept = round(intercept, digits=3), 
    `adj-R2` = round(`adj-R2`, digits = 3)) %>%
  add_column(type="global doughnut", group = "World", grpCode="Wld") %>%
  relocate(type, group, grpCode, .before=indicator)

# write to file
#write_csv(regData, "./myData/12_20250515_globalDoughnutData_regressions.csv")

rm(regData, lmData)
#-----------------------------------------------------------------------------------------------------------------------
#prep 2017 supplementary national groups' dataset with units
grpDat <- myData6 %>%
  filter(type == "national aggregate", date == 2017, group != "World") %>%
  rowwise() %>%
  mutate(shortfallOvershoot_pct = ifelse(domain == "social", (1 - ratio)*100, (ratio-1)*100)) %>%
  ungroup() %>%
  select(-populationTotal, -GNIperCap, -ratio)

#replace public transport 2017 NA with 2020 value
trans <- myData6 %>% 
  filter(type == "national aggregate", indicator == "publicTrans", date == 2020, group != "World") %>%
  rowwise() %>%
  mutate(shortfallOvershoot_pct = ifelse(domain == "social", (1 - ratio)*100, (ratio-1)*100)) %>%
  ungroup() %>%
  select(-populationTotal, -GNIperCap, -ratio) %>%
  mutate(date = 2017, boundary = 0)

grpDat1 <- grpDat %>%
  filter(indicator != "publicTrans") %>%
  rbind(., trans) %>%
  arrange(dimension, indCode)

rm(grpDat, trans)

#unit tibble
units <- grpDat1 %>% 
  count(domain, dimension, indCode, indicator) %>%
  select(-n) %>%
  mutate(unit = c("tonnes CO2 per capita", "Not available", "Not available", "kg P per capita", "kg N per capita",
    "Not available", "m3 H2O per capita", "Not available", "species-loss (MSA-loss) per hectare per capita",
    "tonnes C per capita", "Not available", "percent", "percent", "percent", "percent", "percent", "percent", "percent", "percent", "percent", 
    "percent", "percent", "percent", "percent", "percent", "percent", "0-100 scale", "Not available", "percent", "percent",
    "percent", "percent", "percent")) 

#merge units with data
grpDat2 <- left_join(grpDat1, units, by=c("domain", "dimension", "indCode", "indicator")) %>%
  relocate(unit, .before=date) %>%
  mutate(value = round(value,digits=2),
    shortfallOvershoot_pct = round(shortfallOvershoot_pct, digits=1)) %>%
  rowwise() %>%
  mutate(indicator = ifelse(indCode == "EQ1", "genderInequalityIndex", indicator)) %>%
  ungroup()

#write to file
#write_csv(grpDat2, "./myData/12_20250515_groupDoughnutData_2017.csv")
  
rm(grpDat1, units, grpDat2, myData6)



