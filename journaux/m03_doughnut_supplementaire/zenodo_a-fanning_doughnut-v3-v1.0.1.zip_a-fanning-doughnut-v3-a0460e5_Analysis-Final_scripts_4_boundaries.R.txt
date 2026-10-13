# This script adds social and planetary boundaries to the database

#read in latest dataset
#myData3 <- read_csv("./myData/3_20250108_doughnutData.csv") %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice"))) %>%
  arrange(domain, dimension, type, group)
#---------------------------------------------------------------------------------------
#					prep myData for global boundaries
#---------------------------------------------------------------------------------------
global <- myData3 %>%
  filter(type == "global doughnut")
  
#---------------------------------------------------------------------------------------
#calculate global shares of chemicals hazardous to health and drop
chem <- global %>%
  filter(indicator %in% c("chemicalsMt", "EUshare_hzdHealth")) %>%
  select(-populationTotal, -GNIperCap) %>%
  pivot_wider(names_from=indicator, values_from=value) %>%
  rowwise() %>%
  mutate(value = EUshare_hzdHealth/100*chemicalsMt) %>%
  ungroup() %>%
  select(-chemicalsMt, -EUshare_hzdHealth) %>%
  add_column(indicator = "chemicalsMt_Hzd", populationTotal=NA, GNIperCap=NA)  %>%
  relocate(indicator, .before=date) %>%
  relocate(value, .after=GNIperCap) %>%
  arrange(date)

global1 <- rbind(global, chem) %>%
  filter(!indicator %in% c("chemicalsMt", "EUshare_hzdHealth")) %>%
  arrange(domain, dimension, type, group, indicator, date)

rm(global, chem)
#---------------------------------------------------------------------------------------
#	note racial inequality is totally missing  
#--------------------------------------------------------------------------------------------------
#create global boundaries tibble
boundaries <- global1 %>%
  count(domain, dimension, type, group, indicator) %>%
  select(-n)

boundVals <- tibble(boundary = c(350, 1, 2.75, 60, 62, 6.2, 0.1, 10.2, 11.1, 47.9, 10, 5.59, 276,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, NA, 0, 0, 0, 0, 0))

boundaries1 <- cbind(boundaries, boundVals)

#join boundaries1 to global data
global2 <- left_join(global1, boundaries1, by=c("domain", "dimension", "type", "group", "indicator"))

rm(global1, boundaries, boundVals, boundaries1)

#---------------------------------------------------------------------------------------
#					prep myData for 2017 national boundaries
#---------------------------------------------------------------------------------------
national <- myData3 %>%
  filter(type == "national aggregate")
#---------------------------------------------------------------------------------------  
#create national boundaries 2017 table
boundaries <- national %>%
  count(domain, dimension, type, indicator) %>%
  select(-n) %>%
  add_column(date=as.numeric(2017))


boundVals <- tibble(boundary = c(0.95, NA, NA, 8.5, 0.85, NA, 384, NA, 1.47, 0.51, NA,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, NA, 0, 0, 0, 0, 0))

boundaries1 <- cbind(boundaries, boundVals)

#join boundaries1 to national data
national1 <- left_join(national, boundaries1, by=c("domain", "dimension", "type", "indicator", "date"))

rm(national, boundaries, boundVals, boundaries1)

#---------------------------------------------------------------------------------------
#		re-join global doughnut and national aggregate with respective boundaries
#---------------------------------------------------------------------------------------
myData4 <- rbind(global2, national1) %>%
  arrange(domain, dimension, type, group, indicator, date)

rm(global2, national1)
#--------------------------------------------------------------------------------------------------
#			WRITE TO FILE
#--------------------------------------------------------------------------------------------------
#write_csv(myData4, "./myData/4_20250108_doughnutData-boundaries.csv")

rm(myData3, myData4)


