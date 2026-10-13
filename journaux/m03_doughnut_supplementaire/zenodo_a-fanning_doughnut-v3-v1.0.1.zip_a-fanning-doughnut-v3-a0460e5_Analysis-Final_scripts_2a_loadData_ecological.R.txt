#Load ecological data files

#--------------------------------------------------------------------
#		ecological indicators
#--------------------------------------------------------------------

#--------------------------------------------------------------------
#		climate change
#--------------------------------------------------------------------

co2 <- read_csv("./cleanData/eco-1_climateChange_clean.csv")

ggplot(co2, aes(x=date, y=value, col=group)) +
  geom_line() +
  geom_point() + 
  facet_wrap(~indicator, scales="free") +
  #scale_y_continuous(limits=c(350, 450)) +
  #geom_hline(yintercept=350, color="green") +
  #geom_hline(yintercept=450, color="red") +
  theme_chart

#--------------------------------------------------------------------
#		ocean acidification
#--------------------------------------------------------------------

oceanAcid <- read_csv("./cleanData/eco-2_oceanAcid_clean.csv")

#join
myData <- rbind(co2, oceanAcid)

rm(co2, oceanAcid)

#--------------------------------------------------------------------
#		chemical pollution
#--------------------------------------------------------------------

chemPollution <- read_csv("./cleanData/eco-3_chemPollution_clean.csv") %>%
	group_by(type, group, indicator) %>%
	mutate(value = na.approx(value, na.rm=F)) %>%
	ungroup()

ggplot(chemPollution, aes(x=date, y=value, col=group)) +
  geom_line() +
  geom_point() + 
  facet_wrap(~indicator, scales="free") +
  #scale_y_continuous(limits=c(350, 450)) +
  #geom_hline(yintercept=350, color="green") +
  #geom_hline(yintercept=450, color="red") +
  theme_chart

#join
myData <- rbind(myData, chemPollution)

rm(chemPollution)

#--------------------------------------------------------------------
#		nutrient pollution
#--------------------------------------------------------------------

fertilizer <- read_csv("./cleanData/eco-4_nutrientPollution_clean.csv")

ggplot(fertilizer, aes(x=date, y=value, col=group)) +
  geom_line() +
  geom_point() + 
  facet_wrap(~indicator, scales="free") +
  #scale_y_continuous(limits=c(350, 450)) +
  #geom_hline(yintercept=350, color="green") +
  #geom_hline(yintercept=450, color="red") +
  theme_chart

#join
myData <- rbind(myData, fertilizer)

rm(fertilizer)

#--------------------------------------------------------------------
#		air pollution
#--------------------------------------------------------------------

airPollution <- read_csv("./cleanData/eco-8_airPollution_clean.csv") %>%
  group_by(type, group, indicator) %>%
  mutate(value = na.approx(value, na.rm=F)) %>%
  ungroup()

ggplot(airPollution, aes(x=date, y=value, col=group)) +
  geom_line() +
  geom_point() + 
  facet_wrap(~indicator, scales="free") +
  #scale_y_continuous(limits=c(350, 450)) +
  #geom_hline(yintercept=350, color="green") +
  #geom_hline(yintercept=450, color="red") +
  theme_chart


#join
myData <- rbind(myData, airPollution)

rm(airPollution)

#--------------------------------------------------------------------
#		freshwater disruption
#--------------------------------------------------------------------

freshwater <- read_csv("./cleanData/eco-5_freshwaterDisruption_clean.csv")

ggplot(freshwater, aes(x=date, y=value, col=group)) +
  geom_line() +
  geom_point() + 
  facet_wrap(~indicator, scales="free") +
  #scale_y_continuous(limits=c(350, 450)) +
  #geom_hline(yintercept=350, color="green") +
  #geom_hline(yintercept=450, color="red") +
  theme_chart

#join
myData <- rbind(myData, freshwater)

rm(freshwater)

#--------------------------------------------------------------------
#		land conversion
#--------------------------------------------------------------------

landCon <- read_csv("./cleanData/eco-6_landConversion_clean.csv")

ggplot(landCon, aes(x=date, y=value, col=group)) +
  geom_line() +
  geom_point() + 
  facet_wrap(~indicator, scales="free") +
  #scale_y_continuous(limits=c(350, 450)) +
  #geom_hline(yintercept=350, color="green") +
  #geom_hline(yintercept=450, color="red") +
  theme_chart

#join
myData <- rbind(myData, landCon)

rm(landCon)

#--------------------------------------------------------------------
#		biodiversity breakdown
#--------------------------------------------------------------------

biodiversity <- read_csv("./cleanData/eco-7_biodiversityBreakdown_clean.csv") %>%
	group_by(type, group, indicator) %>%
	mutate(value = na.approx(value, na.rm=F)) %>%
	ungroup()

ggplot(biodiversity, aes(x=date, y=value, col=group)) +
  geom_line() +
  geom_point() + 
  facet_wrap(~indicator, scales="free") +
  #scale_y_continuous(limits=c(350, 450)) +
  #geom_hline(yintercept=350, color="green") +
  #geom_hline(yintercept=450, color="red") +
  theme_chart

#join
myData <- rbind(myData, biodiversity)
rm(biodiversity)

#--------------------------------------------------------------------
#		ozone depletion
#--------------------------------------------------------------------

ozoneDepletion <- read_csv("./cleanData/eco-9_ozoneDepletion_clean.csv")

ggplot(ozoneDepletion, aes(x=date, y=value, col=group)) +
  geom_line() +
  geom_point() + 
  facet_wrap(~indicator, scales="free") +
  #scale_y_continuous(limits=c(350, 450)) +
  #geom_hline(yintercept=350, color="green") +
  #geom_hline(yintercept=450, color="red") +
  theme_chart

#join
myData <- rbind(myData, ozoneDepletion)

rm(ozoneDepletion)


#--------------------------------------------------------------------
#		WRITE TO FILE
#--------------------------------------------------------------------
ecoData <- myData
rm(myData)
#write_csv(ecoData, "./myData/2_20241226_ecoData.csv")
rm(ecoData)

