#This script creates a multi-panel chart of all social and eco indicators in the disaggregated Doughnuts

#read in cleaned data file
myData6 <- read_csv("./myData/5_20250108_doughnutDat-boundariesRatios.csv") %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice")))
#-------------------------------------------------------------------------------------------------------
# pull out 2017 ecological data by country group
#-------------------------------------------------------------------------------------------------------
grpEco <- myData6 %>%
  filter(date == 2017, type == "national aggregate", domain == "ecological", group != "World",
    indCode %in% c("CC3", "NP3", "NP4", "FD3", "BB3", "BB4")) %>% 
  mutate(indCode = factor(indCode, levels = c("CC3", "NP3", "NP4", "FD3", "BB3", "BB4"))) %>%
  arrange(dimension, indCode)

#-------------------------------------------------------------------------------------------------------
#prep visual vars

#define colours
#cols <- c("CC3"="#7e0129", "NP3"="#7e0129", "NP4"="#b9026b", "FD3"="#7e0129", "BB3"="#7e0129", "BB4"="#b9026b")
cols <- c("Bottom-40"="#f3d225", "Middle-40"="#b7bca3", "Top-20"="#3d85c6")

#set axis labels
dimLabsY <- tibble(dimLabY = c("*", "0%", "200%", "400%", "600%", "800%", "1,000%"))

#set indicator labels for annotation
indicatorLabs <- grpEco %>%
  count(dimension, indCode, indicator) %>%
  select(-n) %>%
  mutate(indLabel.ch = c("carbon\nfootprint", "phosphorus\nfootprint", "nitrogen\nfootprint", "blue water\nfootprint", 
    "species-loss\nfootprint", "hanpp\nfootprint"))

#set label positions for indicators (x1, y1) and equations (x2, y2)
pos <- tibble(
  x1 = c(2017, 2016.75, 2017.25, 2017, 2016.75, 2017.25), 
  y1 = c(11.5, 11.5, 11.5, 11.5, 11.5, 11.5))

#join coordinates to labels 
indicatorLabs1 <- cbind(indicatorLabs, pos)

#create ribbon vals
ribbon <- tibble(
  x=c(2016, 2018),
  ymin=c(0,0),
  ymax=c(1,1))

#-------------------------------------------------------------------------------------------------------
#plot!
ecoPanels <- ggplot() + 
  geom_col(data = grpEco, aes(x=date, y=ratio, , group=indCode, fill=group), position="dodge2") +
  geom_ribbon(data = ribbon, aes(x=x, ymin=ymin, ymax=ymax), alpha=0.5, fill="#6eb446") + #
  geom_hline(yintercept = 1, col = "#227443", lwd=1.5) +
  geom_text(data = indicatorLabs1, aes(x = x1, y = y1, label = indLabel.ch), vjust=1, hjust=0.5, size=2) +
  facet_wrap(~dimension, ncol=4, strip.position="bottom") +
  scale_fill_manual(name="Indicators", values=cols) +
#  scale_colour_manual(values=cols) +
  scale_y_continuous(limits=c(0,12.5), labels=dimLabsY$dimLabY, breaks=c(0,1,3,5,7,9,11), expand=c(0,0)) +
  scale_x_continuous(expand=c(0,0)) +
  coord_cartesian(xlim=c(2016.5, 2017.5)) +
  labs(x = "", y = "Ecological overshoot\n(0% = per capita boundary)") +
  theme_bw() +
  theme(legend.position="none",
    panel.grid=element_blank(),
    strip.background=element_rect(fill="white"),
    strip.text=element_text(size=7),
    axis.title=element_text(size=7),
    axis.text=element_text(size=6),
    axis.text.x=element_blank(),
    axis.ticks.x=element_blank())

#ggsave("./figures/11_grpEco_barIndicators_R2.png", width = 183, height = 50, units = "mm", device = "png")

rm(cols, dimLabsY, indicatorLabs, indicatorLabs1, pos, ribbon)

#-------------------------------------------------------------------------------------------------------
# pull out 2017 social data by country group
#-------------------------------------------------------------------------------------------------------
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

#-------------------------------------------------------------------------------------------------------
#prep visual vars

#define colours
cols <- c("Bottom-40"="#f3d225", "Middle-40"="#b7bca3", "Top-20"="#3d85c6")


#set indicator labels for annotation
indicatorLabs <- grpSoc1 %>%
  count(dimension, indCode, indicator) %>%
  select(-n) %>%
  mutate(indLabel.ch = c("under-\nnourished", "food\ninsecurity", "under-5\nmortality",
    "lack of\nhealth\nservices", "illiteracy\nrate", "incomplete\nsecondary\nschool", "societal\npoverty", "youth\nNEET",
    "unsafe\ndrinking\nwater", "unsafe\nsanitation", "lack of\nelectricity", "lack of\nclean fuels\nindoors",
    "lack of\npublic\ntransport", "lack of\ninternet", "slums or\ninformal housing", "gender\ninequality",
    "lack of\nsocial\nsupport", "income\ninequality", "autocratic\nregimes",
    "perceptions of\ncorruption", "homicide\nrate"))

#set label positions for indicators (x1, y1) and equations (x2, y2)
pos <- tibble(
  x1 = c(2016.75, 2017.25, 2016.75, 2017.25, 2016.75, 2017.25, 2016.75, 2017.25,
    2016.75, 2017.25, 2016.75, 2017.25, 2016.75, 2017.25, 2017,
    2017, 2016.75, 2017.25, 2017, 2016.75, 2017.25), 
  y1 = c(1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 
    1.05, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05))

#join coordinates to labels 
indicatorLabs1 <- cbind(indicatorLabs, pos)

#create ribbon vals
ribbon <- tibble(
  x=c(2016, 2018),
  ymin=c(-0.1,-0.1),
  ymax=c(0,0))

#-------------------------------------------------------------------------------------------------------
#plot!
socPanels <- ggplot() + 
  geom_col(data = grpSoc1, aes(x=date, y=ratio, group=indCode, fill=group), position="dodge2") +
  geom_ribbon(data = ribbon, aes(x=x, ymin=ymin, ymax=ymax), alpha=0.5, fill="#6eb446") + #
  geom_hline(yintercept = 0, col = "#227443", lwd=1.5) +
  geom_text(data = indicatorLabs1, aes(x = x1, y = y1, label = indLabel.ch), vjust=0, hjust=0.5, size=2) +
  facet_wrap(~dimension, ncol=4) +
  scale_fill_manual(name="Indicators", values=cols) +
#  scale_colour_manual(values=cols) +
  scale_y_reverse(labels = scales::percent_format(big.mark=","), expand = c(0,0.01)) +
  scale_x_continuous(expand=c(0,0)) +
  coord_cartesian(ylim=c(1.1,-0.1), xlim=c(2016.5, 2017.5)) +
  labs(x = "", y = "Social shortfall\n(0% = social foundation)") +
  theme_bw() +
  theme(legend.position="none",
    panel.grid=element_blank(),
    strip.background=element_rect(fill="white"),
    strip.text=element_text(size=7),
    axis.title=element_text(size=7),
    axis.text=element_text(size=6),
    axis.text.x=element_blank(),
    axis.ticks.x=element_blank())

#ggsave("./figures/11_grpSoc_barIndicators_R2.png", width = 183, height = 150, units = "mm", device = "png")

rm(cols, indicatorLabs, indicatorLabs1, pos, ribbon)

#-----------------------------------------------------------------------------------------------
# merge charts into one figure and write group bar-data to file
#-----------------------------------------------------------------------------------------------

ggarrange(ecoPanels, socPanels, ncol=1, labels=c("a", "b"), font.label=list(size=8),
  align="v", heights = c(1,2.5)) #

#ggsave("./figures/11_grp_barIndicators_R2_v1.pdf", width = 183, height = 180, units = "mm", device = "pdf")

rm(ecoPanels, socPanels)
#-----------------------------------------------------------------------------------------------
fig4data <- rbind(grpEco, grpSoc1) %>%
  mutate(ratio = ifelse(domain=="ecological", ratio - 1, ratio))

#write_csv(fig4data, "./myData/11_20250115_multiPanelData.csv")

rm(grpEco, grpSoc1, fig4data, myData6)
