#this script pulls out variability within and across country groups

#read in cleaned data file
myData6 <- read_csv("./myData/5_20250108_doughnutDat-boundariesRatios.csv") %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice")))
#-------------------------------------------------------------------------------------------------------
# pull out 2017 social and ecological data by country group
#-------------------------------------------------------------------------------------------------------
#social
grpSoc <- myData6 %>%
  filter(date == 2017, type == "national aggregate", domain == "social", group != "World", indCode != "EQ2")

#replace public transport 2017 NA with 2020 value
trans <- myData6 %>% 
  filter(type == "national aggregate", indicator == "publicTrans", date == 2020, group != "World") %>%
  mutate(date = 2017)

grpSoc1 <- grpSoc %>%
  filter(indicator != "publicTrans") %>%
  rbind(., trans) %>%
  mutate(ratio = 1 - ratio, 
    indCode = factor(indCode, levels = c("NU1", "NU2", "HE1", "HE2", "ED1", "ED2", 
      "IW1", "IW2", "WA1", "WA2", "EN1", "EN2", "CO1", "CO2", "HO1", "EQ1", "SC1", "SC2", 
      "PV1", "PJ1", "PJ2"))) %>%
  arrange(dimension, indCode)

rm(grpSoc, trans)

#ecological
grpEco <- myData6 %>%
  filter(date == 2017, type == "national aggregate", domain == "ecological", group != "World",
    indCode %in% c("CC3", "NP3", "NP4", "FD3", "BB3", "BB4")) %>% 
  mutate(indCode = factor(indCode, levels = c("CC3", "NP3", "NP4", "FD3", "BB3", "BB4")),
    ratio = ratio-1) %>%
  arrange(dimension, indCode)

#-----------------------------------------------------------------------------------------------------
#ranges
#-----------------------------------------------------------------------------------------------------
#look at social shortfall range across groups (N=21)

ggplot(grpSoc1, aes(x=group, y=ratio)) +
  geom_hline(yintercept = 0, lwd=3, col="#227443") +
  geom_boxplot(aes(group = group), outlier.shape=NA) +
  geom_jitter(width=0.2) +
  scale_y_reverse(limits=c(1,-0.01), labels = scales::percent) +
  scale_x_discrete(labels=c("Poorest 40%", "Middle 40%", "Richest 20%"), expand = c(0,0.4)) +
#  scale_y_continuous(labels = scales::percent) +
#  coord_cartesian(ylim=c(1,0), xlim=c(2000,2022)) +
  labs(x="Country cluster", y="Range of shortfall across social\nindicators (0 = no shortfall)") +
  theme_bw()

#save figure to file
#ggsave("./figures/ExtDataFig8_shortfallRange-by-group_Boxplots_final.png", width = 120, height = 80, units = "mm", device="png")

#get data
g <- ggplot(grpSoc1, aes(group, ratio)) +
  geom_boxplot(aes(group = group))

socRange <- layer_data(g)
rm(g)

#log one outlier in R2 update: Top-20 control of corruption = 0.609

socRange1 <- socRange %>%
  select(-outliers, -newx) %>%
  tibble()

#write boxplot data to file
#write_csv(socRange1, "./myData/11_20250122_socialShortfall-grpBoxPlotData.csv")

rm(socRange, socRange1)

#-----------------------------------------------------------------------------------------------------
#look at ecological overshoot range across groups

ggplot(grpEco, aes(group, ratio)) +
  geom_hline(yintercept = 0, lwd = 3, col="#227443") + 
  geom_boxplot(aes(group = group), outlier.shape=NA) + 
  geom_jitter(width=0.2) +
  scale_y_continuous(breaks=c(-1,0,2.5,5,7.5,10, 12.5), labels = c("*", "0%", "250%", "500%", "750%", "1,000%", "1,250%")) +
  scale_x_discrete(labels=c("Poorest 40%", "Middle 40%", "Richest 20%"), expand = c(0,0.4)) +
  labs(x = "Country cluster", y = "Range of overshoot across ecological\nindicators (0 = no overshoot)") +
  theme_bw()

#ggsave("./figures/ExtDataFig9_overshootRange-by-group_Boxplots_final.png", width = 120, height = 80, units = "mm", device="png")

#get data
g <- ggplot(grpEco, aes(group, ratio)) +
  geom_boxplot(aes(group = group))

ecoRange <- layer_data(g) 
rm(g)

#log one outlier in R2 update: Top-20 carbon footprint = 11.263

ecoRange1 <- ecoRange %>%
  select(-outliers, -newx) 


#write boxplot data to file
#write_csv(ecoRange1, "./myData/11_20250122_EcologicalOvershoot-grpBoxPlotData.csv")

rm(ecoRange, ecoRange1, grpDat1, grpEco, grpSoc1, myDat1, myData6)

