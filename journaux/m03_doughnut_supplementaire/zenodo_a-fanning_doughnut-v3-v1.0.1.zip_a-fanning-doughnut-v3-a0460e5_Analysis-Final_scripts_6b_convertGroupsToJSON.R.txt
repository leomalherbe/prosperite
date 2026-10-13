#This script converts the global and national aggregate data into JSON format for visualising
#It's a good idea to restart R to clean up library / avoid variable mix-ups with global

#Read in data file if needed.
#myData6 <- read_csv("./myData/5_20250108_doughnutDat-boundariesRatios.csv") %>%
  rename(grp = group) %>%
  mutate(dimension = factor(dimension, levels = c("climate change", "ocean acidification", "chemical pollution",
	"nutrient pollution", "air pollution", "freshwater disruption", "land conversion", "biodiversity breakdown",
	"ozone depletion", "food", "health", "education", "income and work", "water", "energy", "connectivity",
	"housing", "equality", "social cohesion", "political voice", "peace and justice")))


#-------------------------------------------------------------------------------------------------
#					PREP COUNTRY-GROUP VARIABLES FOR NESTING
national <- myData6 %>%
  filter(type == "national aggregate", date == 2017)

# check missings
national %>% count(indicator, value) %>% filter(is.na(value))

#replace public transport 2017 NA with 2020 value
trans <- myData6 %>% 
  filter(type == "national aggregate", indicator == "publicTrans", date == 2020) %>%
  mutate(date = 2017)

national1 <- national %>%
  filter(indicator != "publicTrans") %>%
  rbind(., trans) %>%
  arrange(domain, dimension, indicator)

national2 <- myData6 %>%
  filter(type == "national aggregate", date != 2017) %>%
  rbind(., national1) %>%
  arrange(domain, dimension, grp, indCode, date)

rm(national, trans, national1, myData6)
#-------------------------------------------------------------------------------------------------
placeList <- national2 %>%
  count(grp, grpCode) %>%
  select(-n)

ecoMinmax <- national2 %>%
  filter(domain == "ecological") %>%
  group_by(grp, grpCode) %>%
  summarise(min = min(ratio, na.rm=T),
	max = max(ratio, na.rm=T)) %>%
  ungroup()

socMinmax <- national2 %>%
  filter(domain == "social") %>%
  group_by(grp, grpCode) %>%
  summarise(min = min(ratio, na.rm=T),
	max = max(ratio, na.rm=T)) %>%
  ungroup()

#-------------------------------------------------------------------------------------------------
#					PREP ECOLOGICAL VARIABLES FOR NESTING
#-------------------------------------------------------------------------------------------------
#climate change - CO2 footprint
cc1Range <- rangeRatio(national2, indCode == "CC3")
cc1Ratio1 <- blankRatioGrp(national2, indCode == "CC3") 
cc1Ratio2 <- spreadRatio(national2, indCode == "CC3") 

#ocean acidification (Missing, replace [-Inf, Inf] range later)
oa1Range <- rangeRatio(national2, indCode == "OA3")
oa1Ratio1 <- blankRatioGrp(national2, indCode == "OA3") 
oa1Ratio2 <- spreadRatio(national2, indCode == "OA3") 

#chemical pollution (Missing, replace [-Inf, Inf] range later)
cp1Range <- rangeRatio(national2, indCode == "CP3")
cp1Ratio1 <- blankRatioGrp(national2, indCode == "CP3")
cp1Ratio2 <- spreadRatio(national2, indCode == "CP3")

#nutrient pollution - phosphorus
np1Range <- rangeRatio(national2, indCode == "NP3")
np1Ratio1 <- spreadRatio(national2, indCode == "NP3") 
np1Ratio2 <- blankRatioGrp(national2, indCode == "NP3")

#nutrient pollution - nitrogen 
np2Range <- rangeRatio(national2, indCode == "NP4")
np2Ratio1 <- spreadRatio(national2, indCode == "NP4") 
np2Ratio2 <- blankRatioGrp(national2, indCode == "NP4")

#air pollution (Missing, replace [-Inf, Inf] range later)
ap1Range <- rangeRatio(national2, indCode == "AP3")
ap1Ratio1 <- blankRatioGrp(national2, indCode == "AP3") 
ap1Ratio2 <- spreadRatio(national2, indCode == "AP3") 

#freshwater use - blue water
fd1Range <- rangeRatio(national2, indCode == "FD3")
fd1Ratio1 <- blankRatioGrp(national2, indCode == "FD3") 
fd1Ratio2 <- spreadRatio(national2, indCode == "FD3")

#land conversion (Missing, replace [-Inf, Inf] range later)
lc1Range <- rangeRatio(national2, indCode == "LC3")
lc1Ratio1 <- blankRatioGrp(national2, indCode == "LC3") 
lc1Ratio2 <- spreadRatio(national2, indCode == "LC3") 

#biodiversity breakdown
bb1Range <- rangeRatio(national2, indCode == "BB3")
bb1Ratio1 <- spreadRatio(national2, indCode == "BB3") 
bb1Ratio2 <- blankRatioGrp(national2, indCode == "BB3") 

#biodiversity breakdown
bb2Range <- rangeRatio(national2, indCode == "BB4")
bb2Ratio1 <- spreadRatio(national2, indCode == "BB4") 
bb2Ratio2 <- blankRatioGrp(national2, indCode == "BB4") 

#ozone depletion (Missing, replace [-Inf, Inf] range later)
od1Range <- rangeRatio(national2, indCode == "OD3")
od1Ratio1 <- blankRatioGrp(national2, indCode == "OD3") 
od1Ratio2 <- spreadRatio(national2, indCode == "OD3") 

#-------------------------------------------------------------------------------------------------
#					PREP SOCIAL VARIABLES FOR NESTING
#-------------------------------------------------------------------------------------------------
#food - undernourishment
nu1Range <- rangeRatio(national2, indCode == "NU1")
nu1Ratio1 <- spreadRatio(national2, indCode == "NU1") 
nu1Ratio2 <- blankRatioGrp(national2, indCode == "NU1")

#food - food insecurity
nu2Range <- rangeRatio(national2, indCode == "NU2")
nu2Ratio1 <- spreadRatio(national2, indCode == "NU2") 
nu2Ratio2 <- blankRatioGrp(national2, indCode == "NU2")

#health - under-5 mortality
he1Range <- rangeRatio(national2, indCode == "HE1")
he1Ratio1 <- spreadRatio(national2, indCode == "HE1") 
he1Ratio2 <- blankRatioGrp(national2, indCode == "HE1")

#health - UHC index
he2Range <- rangeRatio(national2, indCode == "HE2")
he2Ratio1 <- spreadRatio(national2, indCode == "HE2") 
he2Ratio2 <- blankRatioGrp(national2, indCode == "HE2")

#education - literacy
ed1Range <- rangeRatio(national2, indCode == "ED1")
ed1Ratio1 <- spreadRatio(national2, indCode == "ED1") 
ed1Ratio2 <- blankRatioGrp(national2, indCode == "ED1")

#education - secondary school
ed2Range <- rangeRatio(national2, indCode == "ED2")
ed2Ratio1 <- spreadRatio(national2, indCode == "ED2") 
ed2Ratio2 <- blankRatioGrp(national2, indCode == "ED2")

#income & work - societal poverty
iw1Range <- rangeRatio(national2, indCode == "IW1")
iw1Ratio1 <- spreadRatio(national2, indCode == "IW1") 
iw1Ratio2 <- blankRatioGrp(national2, indCode == "IW1")

#income & work - youth NEET
iw2Range <- rangeRatio(national2, indCode == "IW2")
iw2Ratio1 <- spreadRatio(national2, indCode == "IW2") 
iw2Ratio2 <- blankRatioGrp(national2, indCode == "IW2")

#water - drinking
wa1Range <- rangeRatio(national2, indCode == "WA1")
wa1Ratio1 <- spreadRatio(national2, indCode == "WA1") 
wa1Ratio2 <- blankRatioGrp(national2, indCode == "WA1")
 
#water - sanitation
wa2Range <- rangeRatio(national2, indCode == "WA2")
wa2Ratio1 <- spreadRatio(national2, indCode == "WA2") 
wa2Ratio2 <- blankRatioGrp(national2, indCode == "WA2")

#energy - electricity
en1Range <- rangeRatio(national2, indCode == "EN1")
en1Ratio1 <- spreadRatio(national2, indCode == "EN1") 
en1Ratio2 <- blankRatioGrp(national2, indCode == "EN1")

#energy - indoor fuels
en2Range <- rangeRatio(national2, indCode == "EN2")
en2Ratio1 <- spreadRatio(national2, indCode == "EN2") 
en2Ratio2 <- blankRatioGrp(national2, indCode == "EN2")

#connectivity - public transport
co1Range <- rangeRatio(national2, indCode == "CO1")
co1Ratio1 <- spreadRatio(national2, indCode == "CO1") 
co1Ratio2 <- blankRatioGrp(national2, indCode == "CO1")

#connectivity - internet
co2Range <- rangeRatio(national2, indCode == "CO2")
co2Ratio1 <- spreadRatio(national2, indCode == "CO2") 
co2Ratio2 <- blankRatioGrp(national2, indCode == "CO2")

#housing - urban slums
ho1Range <- rangeRatio(national2, indCode == "HO1")
ho1Ratio1 <- blankRatioGrp(national2, indCode == "HO1") 
ho1Ratio2 <- spreadRatio(national2, indCode == "HO1")

#equality - gender inequality
eq1Range <- rangeRatio(national2, indCode == "EQ1")
eq1Ratio1 <- spreadRatio(national2, indCode == "EQ1") 
eq1Ratio2 <- blankRatioGrp(national2, indCode == "EQ1")

#equality - racial inequality  (replace missings [-Inf, Inf]) 
eq2Range <- rangeRatio(national2, indCode == "EQ2")
eq2Ratio1 <- spreadRatio(national2, indCode == "EQ2") 
eq2Ratio2 <- blankRatioGrp(national2, indCode == "EQ2")

#social cohesion - social support
sc1Range <- rangeRatio(national2, indCode == "SC1")
sc1Ratio1 <- spreadRatio(national2, indCode == "SC1") 
sc1Ratio2 <- blankRatioGrp(national2, indCode == "SC1")

#social cohesion - palma
sc2Range <- rangeRatio(national2, indCode == "SC2")
sc2Ratio1 <- spreadRatio(national2, indCode == "SC2") 
sc2Ratio2 <- blankRatioGrp(national2, indCode == "SC2")

#political voice
pv1Range <- rangeRatio(national2, indCode == "PV1")
pv1Ratio1 <- blankRatioGrp(national2, indCode == "PV1") 
pv1Ratio2 <- spreadRatio(national2, indCode == "PV1")

#peace & justice - corruption
pj1Range <- rangeRatio(national2, indCode == "PJ1")
pj1Ratio1 <- spreadRatio(national2, indCode == "PJ1") 
pj1Ratio2 <- blankRatioGrp(national2, indCode == "PJ1")

#peace & justice - homicides
pj2Range <- rangeRatio(national2, indCode == "PJ2")
pj2Ratio1 <- spreadRatio(national2, indCode == "PJ2") 
pj2Ratio2 <- blankRatioGrp(national2, indCode == "PJ2")


#----------------------------------------------------------------------------------------------------------------
doughnutNest <- list()
myList <- list()

for(i in 1:length(placeList$grp)){
  doughnutNest[[i]] <- list(
	place = placeList[[1]][i],
	placeCode = placeList[[2]][i],
	ecological = list(
		min = ecoMinmax[[3]][i],
		max = ecoMinmax[[4]][i],
		range = list(
			cc1 = list(cc1Range[[3]][i], cc1Range[[4]][i]),
			cc2 = list(cc1Range[[3]][i], cc1Range[[4]][i]),
			oa1 = list(oa1Range[[3]][i], oa1Range[[4]][i]),
			oa2 = list(oa1Range[[3]][i], oa1Range[[4]][i]),
			cp1 = list(cp1Range[[3]][i], cp1Range[[4]][i]),
			cp2 = list(cp1Range[[3]][i], cp1Range[[4]][i]),
			np1 = list(np1Range[[3]][i], np1Range[[4]][i]),
			np2 = list(np2Range[[3]][i], np2Range[[4]][i]),
			ap1 = list(ap1Range[[3]][i], ap1Range[[4]][i]),
			ap2 = list(ap1Range[[3]][i], ap1Range[[4]][i]),
			fd1 = list(fd1Range[[3]][i], fd1Range[[4]][i]),
			fd2 = list(fd1Range[[3]][i], fd1Range[[4]][i]),
			lc1 = list(lc1Range[[3]][i], lc1Range[[4]][i]),
			lc2 = list(lc1Range[[3]][i], lc1Range[[4]][i]),
			bb1 = list(bb1Range[[3]][i], bb1Range[[4]][i]),
			bb2 = list(bb2Range[[3]][i], bb2Range[[4]][i]),
			od1 = list(od1Range[[3]][i], od1Range[[4]][i]),
			od2 = list(od1Range[[3]][i], od1Range[[4]][i])
		),
		series1 = list(
			cc1 = pullVars(cc1Ratio1, i),
			cc2 = pullVars(cc1Ratio1, i),
			oa1 = pullVars(oa1Ratio1, i),
			oa2 = pullVars(oa1Ratio1, i),
			cp1 = pullVars(cp1Ratio1, i),
			cp2 = pullVars(cp1Ratio1, i),
			np1 = pullVars(np1Ratio1, i),
			np2 = pullVars(np2Ratio1, i),
			ap1 = pullVars(ap1Ratio1, i),
			ap2 = pullVars(ap1Ratio1, i),
			fd1 = pullVars(fd1Ratio1, i),
			fd2 = pullVars(fd1Ratio1, i),
			lc1 = pullVars(lc1Ratio1, i),
			lc2 = pullVars(lc1Ratio1, i),
			bb1 = pullVars(bb1Ratio1, i),
			bb2 = pullVars(bb2Ratio1, i),
			od1 = pullVars(od1Ratio1, i),
			od2 = pullVars(od1Ratio1, i)
		),
		series2 = list(
			cc = pullVars(cc1Ratio2, i),
			oa = pullVars(oa1Ratio2, i),
			cp = pullVars(cp1Ratio2, i),
			np = pullVars(np1Ratio2, i),
			ap = pullVars(ap1Ratio2, i),
			fd = pullVars(fd1Ratio2, i),
			lc = pullVars(lc1Ratio2, i),
			bb = pullVars(bb1Ratio2, i),
			od = pullVars(od1Ratio2, i)
		)
	),
	social = list(
		min = socMinmax[[3]][i],
		max = socMinmax[[4]][i],
		range = list(
			co1 = list(co1Range[[3]][i], co1Range[[4]][i]),
			co2 = list(co2Range[[3]][i], co2Range[[4]][i]),
			en1 = list(en1Range[[3]][i], en1Range[[4]][i]),
			en2 = list(en2Range[[3]][i], en2Range[[4]][i]),
			wa1 = list(wa1Range[[3]][i], wa1Range[[4]][i]),
			wa2 = list(wa2Range[[3]][i], wa2Range[[4]][i]),
			nu1 = list(nu1Range[[3]][i], nu1Range[[4]][i]),
			nu2 = list(nu2Range[[3]][i], nu2Range[[4]][i]),
			he1 = list(he1Range[[3]][i], he1Range[[4]][i]),
			he2 = list(he2Range[[3]][i], he2Range[[4]][i]),
			ed1 = list(ed1Range[[3]][i], ed1Range[[4]][i]),
			ed2 = list(ed2Range[[3]][i], ed2Range[[4]][i]),
			iw1 = list(iw1Range[[3]][i], iw1Range[[4]][i]),
			iw2 = list(iw2Range[[3]][i], iw2Range[[4]][i]),
			pj1 = list(pj1Range[[3]][i], pj1Range[[4]][i]),
			pj2 = list(pj2Range[[3]][i], pj2Range[[4]][i]),
			pv1 = list(pv1Range[[3]][i], pv1Range[[4]][i]),
			pv2 = list(pv1Range[[3]][i], pv1Range[[4]][i]),
			sc1 = list(sc1Range[[3]][i], sc1Range[[4]][i]),
			sc2 = list(sc2Range[[3]][i], sc2Range[[4]][i]),
			eq1 = list(eq1Range[[3]][i], eq1Range[[4]][i]),
			eq2 = list(eq2Range[[3]][i], eq2Range[[4]][i]),
			ho1 = list(ho1Range[[3]][i], ho1Range[[4]][i]),
			ho2 = list(ho1Range[[3]][i], ho1Range[[4]][i])
		),
		series1 = list(
			co1 = pullVars(co1Ratio1, i),
			co2 = pullVars(co2Ratio1, i),
			en1 = pullVars(en1Ratio1, i),
			en2 = pullVars(en2Ratio1, i),
			wa1 = pullVars(wa1Ratio1, i),
			wa2 = pullVars(wa2Ratio1, i),
			nu1 = pullVars(nu1Ratio1, i),
			nu2 = pullVars(nu2Ratio1, i),
			he1 = pullVars(he1Ratio1, i),
			he2 = pullVars(he2Ratio1, i),
			ed1 = pullVars(ed1Ratio1, i),
			ed2 = pullVars(ed2Ratio1, i),
			iw1 = pullVars(iw1Ratio1, i),
			iw2 = pullVars(iw2Ratio1, i),
			pj1 = pullVars(pj1Ratio1, i),
			pj2 = pullVars(pj2Ratio1, i),
			pv1 = pullVars(pv1Ratio1, i),
			pv2 = pullVars(pv1Ratio1, i),
			sc1 = pullVars(sc1Ratio1, i),
			sc2 = pullVars(sc2Ratio1, i),
			eq1 = pullVars(eq1Ratio1, i),
			eq2 = pullVars(eq2Ratio1, i),
			ho1 = pullVars(ho1Ratio1, i),
			ho2 = pullVars(ho1Ratio1, i)
		),
		series2 = list(
			co = pullVars(co1Ratio2, i),
			en = pullVars(en1Ratio2, i),
			wa = pullVars(wa1Ratio2, i),
			nu = pullVars(nu1Ratio2, i),
			he = pullVars(he1Ratio2, i),
			ed = pullVars(ed1Ratio2, i),
			iw = pullVars(iw1Ratio2, i),
			pj = pullVars(pj1Ratio2, i),
			pv = pullVars(pv1Ratio2, i),
			sc = pullVars(sc1Ratio2, i),
			eq = pullVars(eq1Ratio2, i),
			ho = pullVars(ho1Ratio2, i)
		)
	)
  )
}

#-------------------------------------------------------------------------------------
grpJSON <- toJSON(doughnutNest, pretty = TRUE, auto_unbox=TRUE, digits=2)  #
#write(grpJSON, "./myData/6_20250109_incomeGrpDoughnuts.json")
#-------------------------------------------------------------------------------------

#NOTE, USE VISUAL STUDIO CODE TO CLEAN UP JSON FILE BEFORE LOADING ON OBSERVABLE PLATFORM
# (1) REPLACE NAs with 1.00001
# (2) REPLACE OA3, CP3, AP3, LC3, OD3, AND EQ2[INF,-INF] RANGES WITH [0,1]
#  






