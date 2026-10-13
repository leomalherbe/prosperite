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
#shares of total overshoot / shortfall
#-----------------------------------------------------------------------------------------------------
#calculate share of total shortfall held by each group
grpSoc2 <- grpSoc1 %>%
  rowwise() %>%
  mutate(shareAbs = value/100*populationTotal) %>%
  ungroup()

rm(grpSoc1)

sumAbs <- grpSoc2 %>%
  group_by(domain, dimension, type, indicator, indCode, date) %>%
  summarise(totalAbs = sum(shareAbs)) %>%
  ungroup()

grpSoc3 <- left_join(grpSoc2, sumAbs, by=c("domain", "dimension", "type", "indicator", "indCode", "date")) %>%
  rowwise() %>%
  mutate(share = shareAbs/totalAbs) %>%
  ungroup() %>%
  mutate(group = factor(group, levels=c("Bottom-40", "Middle-40", "Top-20")))

rm(grpSoc2, sumAbs)
#-----------------------------------------------------------------------------------------------------
#calculate share of excess footprints held by each group
grpEco1 <- grpEco %>%
  rowwise() %>%
  mutate(shareAbs = ifelse((value-boundary)*populationTotal < 0, 0, (value-boundary)*populationTotal)) %>%
  ungroup()

rm(grpEco)

sumAbs <- grpEco1 %>%
  group_by(domain, dimension, type, indicator, indCode, date) %>%
  summarise(totalAbs = sum(shareAbs)) %>%
  ungroup()

grpEco2 <- left_join(grpEco1, sumAbs, by=c("domain", "dimension", "type", "indicator", "indCode", "date")) %>%
  rowwise() %>%
  mutate(share = ifelse(is.na(shareAbs/totalAbs), 0, shareAbs/totalAbs)) %>%
  ungroup() %>%
  mutate(group = factor(group, levels=c("Bottom-40", "Middle-40", "Top-20")))


rm(grpEco1, sumAbs)
#------------------------------------------------------------------------------------------
#prep visual vars and labels
cols <- c("Bottom-40"="#f3d225", "Middle-40"="#b7bca3", "Top-20"="#3d85c6")

socAxisLab <- grpSoc3 %>%
  count(dimension, indCode, indicator) %>%
  select(-n) %>%
  mutate(axisLab = c("under-\nnourished", "food\ninsecurity", "under-5\nmortality",
      "lack of\nhealth services", "illiteracy\nrate", "incomplete\nsecondary school", "societal\npoverty", "youth\nNEET",
      "unsafe\ndrinking water", "unsafe\nsanitation", "lack of\nelectricity", "lack of clean\nfuels indoors",
      "lack of\npublic transport", "lack of\ninternet", "slums or\ninformal housing", "gender\ninequality",
      "lack of\nsocial support", "income\ninequality", "autocratic\nregimes",
      "perceptions of\ncorruption", "homicide\nrate"),
    axisLab = factor(axisLab, levels=c("under-\nnourished", "food\ninsecurity", "under-5\nmortality",
      "lack of\nhealth services", "illiteracy\nrate", "incomplete\nsecondary school", "societal\npoverty", "youth\nNEET",
      "unsafe\ndrinking water", "unsafe\nsanitation", "lack of\nelectricity", "lack of clean\nfuels indoors",
      "lack of\npublic transport", "lack of\ninternet", "slums or\ninformal housing", "gender\ninequality",
      "lack of\nsocial support", "income\ninequality", "autocratic\nregimes",
      "perceptions of\ncorruption", "homicide\nrate")))

socChart <- left_join(grpSoc3, socAxisLab, by=c("dimension", "indCode", "indicator"))

ecoAxisLab <- grpEco2 %>%
  count(dimension, indCode, indicator) %>%
  select(-n) %>%
  mutate(axisLab = c("carbon\nfootprint", "phosphorus\nfootprint", "nitrogen\nfootprint", "blue water\nfootprint", 
      "species-loss\nfootprint", "hanpp\nfootprint"),
    axisLab = factor(axisLab, levels=c("carbon\nfootprint", "phosphorus\nfootprint", "nitrogen\nfootprint",
      "blue water\nfootprint", "species-loss\nfootprint", "hanpp\nfootprint")))

ecoChart <- left_join(grpEco2, ecoAxisLab, by=c("dimension", "indCode", "indicator"))
#------------------------------------------------------------------------------------------
#plot social!
socShares <- ggplot(socChart, aes(x=axisLab, y=share, fill=group)) +
  geom_col() +
  scale_x_discrete(limits=rev, expand=c(0,0), labels=socAxisLab) +
  scale_y_continuous(labels=scales::percent_format(big.mark=","), expand=c(0,0)) +
  coord_flip() +
  scale_fill_manual(name="Country cluster", labels=c("poorest 40%", "middle 40%", "richest 20%"), values=cols) +
  labs(x="", y="Share of global social shortfall") +
  theme_bw() +
  theme(
    panel.grid=element_blank(),
    legend.title = element_text(size=7, face="bold"),
    legend.text = element_text(size=7),
    axis.title=element_text(size=7),
    axis.text=element_text(size=6),
  )

#plot ecological!
ecoShares <- ggplot(ecoChart, aes(x=axisLab, y=share, fill=group)) +
  geom_col() +
  scale_x_discrete(limits=rev, expand=c(0,0), labels=socAxisLab) +
  scale_y_continuous(labels=scales::percent_format(big.mark=","), expand=c(0,0)) +
  coord_flip() +
  scale_fill_manual(name="Country cluster", labels=c("poorest 40%", "middle 40%", "richest 20%"), values=cols) +
  labs(x="", y="Contribution to global ecological overshoot") +
  theme_bw() +
  theme(
    panel.grid=element_blank(),
    legend.title = element_text(size=7, face="bold"),
    legend.text = element_text(size=7),
    axis.title=element_text(size=7),
    axis.text=element_text(size=6),
  )

#-----------------------------------------------------------------------------------------------
# merge charts into one figure and write group bar-data to file
#-----------------------------------------------------------------------------------------------

ggarrange(ecoShares, socShares, ncol=1, labels=c("a", "b"), font.label=list(size=8),
  heights = c(1,2.8), align="v", common.legend=T, legend="right") #

#ggsave("./figures/ExtDataFig10_group-Shares_final.png", width = 183, height = 180, units = "mm", device = "png")

rm(ecoShares, socShares, cols, ecoAxisLab, socAxisLab, grpEco2, grpSoc3)

chartData <- rbind(ecoChart, socChart) %>% select(-axisLab)

#write_csv(chartData, "./myData/11_20250127-grpDataAndShares.csv")
rm(ecoChart, socChart)

#-----------------------------------------------------------------------------------------
#				COUNTRY GROUP STATS FOR WRITING
#-----------------------------------------------------------------------------------------
#figure out relative proportions of overshoot/shortfall with respect to best-performing group

#ecological
propEco <- chartData %>%
  filter(domain == "ecological") %>%
  select(-populationTotal, -GNIperCap, -value, -boundary, -group, -shareAbs, -totalAbs, -share) %>%
  pivot_wider(names_from = grpCode, values_from = ratio) %>%
  rowwise() %>%
  mutate(M40wrtB40 = (M40+1)/(B40+1),
    T20wrtB40 = (T20+1)/(B40+1)) %>%
  ungroup() 

#social
propSoc <- chartData %>%
  filter(domain == "social") %>%
  select(-populationTotal, -GNIperCap, -value, -boundary, -group, -shareAbs, -totalAbs, -share) %>%
  pivot_wider(names_from = grpCode, values_from = ratio) %>%
  mutate(T20 = ifelse(T20 < 0.01, 0.01, T20)) %>%
  rowwise() %>%
  mutate(B40wrtT20 = (B40)/(T20),
    M40wrtT20 = (M40)/(T20)) %>%
  ungroup() 

summary(propSoc)
chartData %>% filter(domain == "social", grpCode == "B40", ratio > 0.5) #(N=12)
chartData %>% filter(domain == "social", grpCode == "M40", ratio > 0.5) #(N=4)
chartData %>% filter(domain == "social", grpCode == "T20", ratio > 0.5) #(N=1)

chartData %>% filter(domain == "social", grpCode == "B40", ratio <= 0.1) #(N=0)
chartData %>% filter(domain == "social", grpCode == "M40", ratio <= 0.1) #(N=4)
chartData %>% filter(domain == "social", grpCode == "T20", ratio > 0.15) #(N=13)



#look at groups
chartData %>% filter(domain == "ecological", grpCode == "M40")

#figure out summary stats for shares
chartData %>%
  filter(domain == "ecological", indCode != "FD3") %>%
  select(-populationTotal, -GNIperCap, -value, -boundary, -ratio, -group, -shareAbs, -totalAbs) %>%
  pivot_wider(names_from = grpCode, values_from = share) %>%
  summary()

chartData %>%
  filter(domain == "social") %>%
  select(-populationTotal, -GNIperCap, -value, -boundary, -ratio, -group, -shareAbs, -totalAbs) %>%
  pivot_wider(names_from = grpCode, values_from = share) %>%
  summary()

#-----------------------------------------------------------------------------------------
#				FIGURE OUT POPULATION SHARES COVERED BY NATIONAL AGGREGATES
#-----------------------------------------------------------------------------------------
popShares <- myData6 %>%
  filter(type=="national aggregate", grpCode=="WLD", date==2017) %>%
  drop_na(ratio)

maxPop <- max(popShares$populationTotal)

popShares1 <- popShares %>%
  add_column(maxPop = maxPop) %>%
  rowwise() %>%
  mutate(popShare = populationTotal / maxPop) %>%
  ungroup()

rm(popShares, maxPop)

popShares1 %>% filter(domain=="social") %>% summary()
popShares1 %>% filter(domain=="ecological") %>% summary()



