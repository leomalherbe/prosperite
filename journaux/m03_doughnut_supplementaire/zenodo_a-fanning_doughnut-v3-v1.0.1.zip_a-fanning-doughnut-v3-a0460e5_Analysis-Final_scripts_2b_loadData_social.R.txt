#Load social data files and create doughnut database

#ecoData <- read_csv("./myData/2_20241226_ecoData.csv")

#--------------------------------------------------------------------
#		social indicators
#--------------------------------------------------------------------
#--------------------------------------------------------------------
#		food
#--------------------------------------------------------------------

dat1 <- read_csv("./cleanData/soc-1_food_clean.csv") %>%
  add_column(type = "national aggregate") %>%
  relocate(type, .after=dimension)

dat2 <- dat1 %>%
  filter(group == "World") %>%
  mutate(type = "global doughnut")

food <- rbind(dat2, dat1)

rm(dat1, dat2)

ggplot(food, aes(x=date, y=value, col=group)) +
  geom_hline(yintercept=0, color="green") +  
  geom_line() +
  facet_wrap(~indicator) +
  scale_y_reverse(limits=c(100, 0))  +
  #geom_hline(yintercept=261, color="red") +
  theme_chart

#--------------------------------------------------------------------
#		health
#--------------------------------------------------------------------

dat1 <- read_csv("./cleanData/soc-2_health_clean.csv") %>%
  add_column(type = "national aggregate") %>%
  relocate(type, .after=dimension)

dat2 <- dat1 %>%
  filter(group == "World") %>%
  mutate(type = "global doughnut")

dat <- rbind(dat2, dat1)

rm(dat1, dat2)

ggplot(dat, aes(x=date, y=value, col=group)) +
  geom_hline(yintercept=0, color="green") +  
  geom_line() +
  facet_wrap(~indicator) +
  scale_y_reverse(limits=c(100, 0))  +
  #geom_hline(yintercept=261, color="red") +
  theme_chart

#join
socData <- rbind(food, dat)

rm(food, dat)

#--------------------------------------------------------------------
#		education
#--------------------------------------------------------------------

dat1 <- read_csv("./cleanData/soc-3_education_clean.csv") %>%
  add_column(type = "national aggregate") %>%
  relocate(type, .after=dimension) %>%
  mutate(value = 100 - value)

dat2 <- dat1 %>%
  filter(group == "World") %>%
  mutate(type = "global doughnut")

dat <- rbind(dat2, dat1)

rm(dat1, dat2)

ggplot(dat, aes(x=date, y=value, col=group)) +
  geom_hline(yintercept=0, color="green") +  
  geom_line() +
  facet_wrap(~indicator) +
  scale_y_reverse(limits=c(100, 0))  +
  #geom_hline(yintercept=261, color="red") +
  theme_chart

#join
socData <- rbind(socData, dat)

rm(dat)
#--------------------------------------------------------------------
#		income & work
#--------------------------------------------------------------------

dat1 <- read_csv("./cleanData/soc-4_incomeWork_clean.csv") %>%
  add_column(type = "national aggregate") %>%
  relocate(type, .after=dimension) %>%
  rowwise() %>%
  mutate(value = ifelse(indicator == "societalPoverty", value*100, value)) %>%
  ungroup()

dat2 <- dat1 %>%
  filter(group == "World") %>%
  mutate(type = "global doughnut")

dat <- rbind(dat2, dat1)

rm(dat1, dat2)

ggplot(dat, aes(x=date, y=value, col=group)) +
  geom_hline(yintercept=0, color="green") +  
  geom_line() +
  facet_wrap(~indicator) +
  scale_y_reverse(limits=c(100, 0))  +
  #geom_hline(yintercept=261, color="red") +
  theme_chart

#join
socData <- rbind(socData, dat)

rm(dat)
#--------------------------------------------------------------------
#		water
#--------------------------------------------------------------------

dat1 <- read_csv("./cleanData/soc-5_water_clean.csv") %>%
  add_column(type = "national aggregate") %>%
  relocate(type, .after=dimension) %>%
  rowwise() %>%
  mutate(value = 100 - value)

dat2 <- dat1 %>%
  filter(group == "World") %>%
  mutate(type = "global doughnut")

dat <- rbind(dat2, dat1)

rm(dat1, dat2)

ggplot(dat, aes(x=date, y=value, col=group)) +
  geom_hline(yintercept=0, color="green") +  
  geom_line() +
  facet_wrap(~indicator) +
  scale_y_reverse(limits=c(100, 0))  +
  #geom_hline(yintercept=261, color="red") +
  theme_chart

#join
socData <- rbind(socData, dat)

rm(dat)
#--------------------------------------------------------------------
#		energy
#--------------------------------------------------------------------

dat1 <- read_csv("./cleanData/soc-6_energy_clean.csv") %>%
  add_column(type = "national aggregate") %>%
  relocate(type, .after=dimension) %>%
  rowwise() %>%
  mutate(value = 100 - value)

dat2 <- dat1 %>%
  filter(group == "World") %>%
  mutate(type = "global doughnut")

dat <- rbind(dat2, dat1)

rm(dat1, dat2)

ggplot(dat, aes(x=date, y=value, col=group)) +
  geom_hline(yintercept=0, color="green") +  
  geom_line() +
  facet_wrap(~indicator) +
  scale_y_reverse(limits=c(100, 0))  +
  #geom_hline(yintercept=261, color="red") +
  theme_chart

#join
socData <- rbind(socData, dat)

rm(dat)

#--------------------------------------------------------------------
#		connectivity
#--------------------------------------------------------------------

dat1 <- read_csv("./cleanData/soc-7_connectivity_clean.csv") %>%
  add_column(type = "national aggregate") %>%
  relocate(type, .after=dimension) %>%
  rowwise() %>%
  mutate(value = 100 - value)

dat2 <- dat1 %>%
  filter(group == "World") %>%
  mutate(type = "global doughnut")

dat <- rbind(dat2, dat1)

rm(dat1, dat2)

ggplot(dat, aes(x=date, y=value, col=group)) +
  geom_hline(yintercept=0, color="green") +  
  geom_line() +
  geom_point() +
  facet_wrap(~indicator) +
  scale_y_reverse(limits=c(100, 0))  +
  #geom_hline(yintercept=261, color="red") +
  theme_chart

#join
socData <- rbind(socData, dat)

rm(dat)

#--------------------------------------------------------------------
#		housing
#--------------------------------------------------------------------

dat1 <- read_csv("./cleanData/soc-8_housing_clean.csv") %>%
  filter(indicator == "urbanSlums") %>%
  add_column(type = "national aggregate") %>%
  relocate(type, .after=dimension) 

dat2 <- dat1 %>%
  filter(group == "World") %>%
  mutate(type = "global doughnut")

dat <- rbind(dat2, dat1)

rm(dat1, dat2)

ggplot(dat, aes(x=date, y=value, col=group)) +
  geom_hline(yintercept=0, color="green") +  
  geom_line() +
  geom_point() +
  facet_wrap(~indicator) +
  scale_y_reverse(limits=c(100, 0))  +
  #geom_hline(yintercept=261, color="red") +
  theme_chart

#join
socData <- rbind(socData, dat)

rm(dat)
#--------------------------------------------------------------------
#		equality
#--------------------------------------------------------------------

dat1 <- read_csv("./cleanData/soc-9_equality_clean.csv") %>%
  add_column(type = "national aggregate") %>%
  relocate(type, .after=dimension) %>%
  mutate(value = value * 100) 

dat2 <- dat1 %>%
  filter(group == "World") %>%
  mutate(type = "global doughnut")

dat <- rbind(dat2, dat1)

rm(dat1, dat2)

ggplot(dat, aes(x=date, y=value, col=group)) +
  geom_hline(yintercept=0, color="green") +  
  geom_line() +
  geom_point() +
  facet_wrap(~indicator) +
  scale_y_reverse(limits=c(100, 0))  +
  #geom_hline(yintercept=261, color="red") +
  theme_chart

#join
socData <- rbind(socData, dat)

rm(dat)
#--------------------------------------------------------------------
#		social cohesion
#--------------------------------------------------------------------

dat1 <- read_csv("./cleanData/soc-10_socialCohesion_clean.csv") %>%
  add_column(type = "national aggregate") %>%
  relocate(type, .after=dimension)

dat2 <- dat1 %>%
  filter(group == "World") %>%
  mutate(type = "global doughnut")

dat <- rbind(dat2, dat1)

rm(dat1, dat2)

ggplot(dat, aes(x=date, y=value, col=group)) +
  geom_hline(yintercept=0, color="green") +  
  geom_line() +
  geom_point() +
  facet_wrap(~indicator) +
  scale_y_reverse(limits=c(100, 0))  +
  #geom_hline(yintercept=261, color="red") +
  theme_chart

#join
socData <- rbind(socData, dat)

rm(dat)

#--------------------------------------------------------------------
#		political voice
#--------------------------------------------------------------------

dat1 <- read_csv("./cleanData/soc-11_politicalVoice_clean.csv") %>%
  add_column(type = "national aggregate") %>%
  relocate(type, .after=dimension)

dat2 <- dat1 %>%
  filter(group == "World") %>%
  mutate(type = "global doughnut")

dat <- rbind(dat2, dat1)

rm(dat1, dat2)

ggplot(dat, aes(x=date, y=value, col=group)) +
  geom_hline(yintercept=0, color="green") +  
  geom_line() +
  geom_point() +
  facet_wrap(~indicator) +
  scale_y_reverse(limits=c(100, 0))  +
  #geom_hline(yintercept=261, color="red") +
  theme_chart

#join
socData <- rbind(socData, dat)

rm(dat)
#--------------------------------------------------------------------
#		peace and justice
#--------------------------------------------------------------------

dat1 <- read_csv("./cleanData/soc-12_peaceJustice_clean.csv") %>%
  add_column(type = "national aggregate") %>%
  relocate(type, .after=dimension)

dat2 <- dat1 %>%
  filter(group == "World") %>%
  mutate(type = "global doughnut")

dat <- rbind(dat2, dat1)

rm(dat1, dat2)

ggplot(dat, aes(x=date, y=value, col=group)) +
  geom_hline(yintercept=0, color="green") +  
  geom_line() +
  geom_point() +
  facet_wrap(~indicator) +
  scale_y_reverse(limits=c(100, 0))  +
  #geom_hline(yintercept=261, color="red") +
  theme_chart

#join
socData <- rbind(socData, dat)

rm(dat)

#--------------------------------------------------------------------
#		JOIN WITH ECODATA AND WRITE LONG AND WIDE TO FILE
#--------------------------------------------------------------------
myData <- rbind(ecoData, socData)

myData1 <- myData %>%
  select(-populationTotal, -GNIperCap) %>%	
  pivot_wider(names_from=date, values_from=value)


#write_csv(myData, "./myData/2_20250108_doughnutv3-data.csv")
#write_csv(myData1, "./myData/2_20250108_doughnutv3-data_wide.csv")

rm(ecoData, socData, myData, myData1)

