# This script extrapolates missing values to 2022 (forest area, hanpp, ozone depletion, freshwater, public transport)

#read in latest dataset, if needed
#myData <- read_csv("./myData/2_20250108_doughnutv3-data.csv")

#---------------------------------------------------------------------------------------
#Filter variables to extrapolate linearly
extrap <- myData %>%
  filter(indicator %in% c("chemicalsMt", "hanppGtC", "forestAreaMKM2")) %>%
  group_by(indicator) %>%
  mutate(value2 = coalesce(value, predict(lm(value ~ date), across(date)))) %>%
  ungroup()

ggplot(extrap) +
  geom_line(aes(x=date, y=value2), col="red") +
  geom_line(aes(x=date, y=value), col="black") +
  facet_wrap(~indicator, scales="free") +
  theme_bw()

extrap1 <- extrap %>%
  select(-value) %>%
  rename(value = value2)

rm(extrap)

#join extrapolated indicators to myData
myData1 <- myData %>%
  filter(!indicator %in% c("chemicalsMt", "hanppGtC", "forestAreaMKM2")) %>%
  rbind(., extrap1)

rm(myData, extrap1)
#---------------------------------------------------------------------------------------
#filter variables to repeat last observed value
rept <- myData1 %>% 
  filter(indicator %in% c("totalOzone", "blueDev", "soilDev")) %>%
  group_by(indicator) %>%
  mutate(value2 = na.approx(value, na.rm=F, rule=2)) %>%
  ungroup()

ggplot(rept) +
  geom_line(aes(x=date, y=value2), col="red") +
  geom_line(aes(x=date, y=value), col="black") +
  facet_wrap(~indicator, scales="free") +
  theme_bw()

rept1 <- rept %>%
  select(-value) %>%
  rename(value = value2)

rm(rept)

#join repeated indicators to myData
myData2 <- myData1 %>%
  filter(!indicator %in% c("totalOzone", "blueDev", "soilDev")) %>%
  rbind(., rept1)

rm(myData1, rept1)

#---------------------------------------------------------------------------------------
#repeat public transport indicator from 2020
trans2020 <- myData2 %>%
  filter(indicator == "publicTrans", date == 2020)

trans2021 <- myData2 %>%
  filter(indicator == "publicTrans", date == 2020) %>%
  mutate(date = as.numeric(2021))

trans2022 <- myData2 %>%
  filter(indicator == "publicTrans", date == 2020) %>%
  mutate(date = as.numeric(2022))

trans2019down <- myData2 %>%
  filter(indicator == "publicTrans", date < 2020)

trans <- rbind(trans2019down, trans2020, trans2021, trans2022)

rm(trans2019down, trans2020, trans2021, trans2022)

#look
ggplot(trans, aes(x=date, y=value)) +
  geom_line() +
  facet_wrap(~group) +
  theme_bw()

#join repeated indicators to myData
myData3 <- myData2 %>%
  filter(indicator != "publicTrans") %>%
  rbind(., trans)

rm(myData2, trans)

 
#--------------------------------------------------------------------
#		write data to file with extrapolated values
#--------------------------------------------------------------------
#write_csv(myData3, "./myData/3_20250108_doughnutData.csv")

rm(myData3)

