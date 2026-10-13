#This script converts the global doughnut data into JSON format for visualising

#Read in data file if needed.
#myData6 <- read_csv("./myData/5_20250108_doughnutDat-boundariesRatios.csv") %>%
  rename(grp = group)

#-------------------------------------------------------------------------------------------------
#					PREP GLOBAL VARIABLES FOR NESTING
global <- myData6 %>%
  filter(type == "global doughnut") 
#-------------------------------------------------------------------------------------------------

placeList <- global %>%
  count(grp, grpCode) %>%
  select(-n)

ecoMinmax <- global %>%
  filter(domain == "ecological") %>%
  group_by(grp, grpCode) %>%
  summarise(min = min(ratio, na.rm=T),
	max = max(ratio, na.rm=T)) %>%
  ungroup()

socMinmax <- global %>%
  filter(domain == "social") %>%
  group_by(grp, grpCode) %>%
  summarise(min = min(ratio, na.rm=T),
	max = max(ratio, na.rm=T)) %>%
  ungroup()

#-------------------------------------------------------------------------------------------------
#					PREP ECOLOGICAL VARIABLES FOR NESTING
#-------------------------------------------------------------------------------------------------
#climate change - CO2
cc1Range <- rangeRatio(global, indCode == "CC1")
cc1Ratio1 <- spreadRatio(global, indCode == "CC1") 
cc1Ratio2 <- blankRatio() 

#climate change - ERF
cc2Range <- rangeRatio(global, indCode == "CC2")
cc2Ratio1 <- spreadRatio(global, indCode == "CC2") 
cc2Ratio2 <- blankRatio() 
 

#ocean acidification
oa1Range <- rangeRatio(global, indCode == "OA1")
oa1Ratio1 <- blankRatio() 
oa1Ratio2 <- spreadRatio(global, indCode == "OA1") 

#chemical pollution
cp1Range <- rangeRatio(global, indCode == "CP1")
cp1Ratio1 <- blankRatio()
cp1Ratio2 <- spreadRatio(global, indCode == "CP1")

#nutrient pollution - phosphorus
np1Range <- rangeRatio(global, indCode == "NP1")
np1Ratio1 <- spreadRatio(global, indCode == "NP1") 
np1Ratio2 <- blankRatio()

#nutrient pollution - nitrogen 
np2Range <- rangeRatio(global, indCode == "NP2")
np2Ratio1 <- spreadRatio(global, indCode == "NP2") 
np2Ratio2 <- blankRatio()

#air pollution
ap1Range <- rangeRatio(global, indCode == "AP1")
ap1Ratio1 <- blankRatio() 
ap1Ratio2 <- spreadRatio(global, indCode == "AP1") 

#freshwater use - blue water
fd1Range <- rangeRatio(global, indCode == "FD1")
fd1Ratio1 <- spreadRatio(global, indCode == "FD1") 
fd1Ratio2 <- blankRatio()

#freshwater use - green water
fd2Range <- rangeRatio(global, indCode == "FD2")
fd2Ratio1 <- spreadRatio(global, indCode == "FD2") 
fd2Ratio2 <- blankRatio()

#land conversion
lc1Range <- rangeRatio(global, indCode == "LC1")
lc1Ratio1 <- blankRatio() 
lc1Ratio2 <- spreadRatio(global, indCode == "LC1") 

#biodiversity breakdown
bb1Range <- rangeRatio(global, indCode == "BB1")
bb1Ratio1 <- spreadRatio(global, indCode == "BB1") 
bb1Ratio2 <- blankRatio() 

#biodiversity breakdown
bb2Range <- rangeRatio(global, indCode == "BB2")
bb2Ratio1 <- spreadRatio(global, indCode == "BB2") 
bb2Ratio2 <- blankRatio() 

#ozone depletion
od1Range <- rangeRatio(global, indCode == "OD1")
od1Ratio1 <- blankRatio() 
od1Ratio2 <- spreadRatio(global, indCode == "OD1") 

#-------------------------------------------------------------------------------------------------
#					PREP SOCIAL VARIABLES FOR NESTING
#-------------------------------------------------------------------------------------------------
#food - undernourishment
nu1Range <- rangeRatio(global, indCode == "NU1")
nu1Ratio1 <- spreadRatio(global, indCode == "NU1") 
nu1Ratio2 <- blankRatio()

#food - food insecurity
nu2Range <- rangeRatio(global, indCode == "NU2")
nu2Ratio1 <- spreadRatio(global, indCode == "NU2") 
nu2Ratio2 <- blankRatio()

#health - under-5 mortality
he1Range <- rangeRatio(global, indCode == "HE1")
he1Ratio1 <- spreadRatio(global, indCode == "HE1") 
he1Ratio2 <- blankRatio()


#health - UHC index
he2Range <- rangeRatio(global, indCode == "HE2")
he2Ratio1 <- spreadRatio(global, indCode == "HE2") 
he2Ratio2 <- blankRatio()

#education - literacy
ed1Range <- rangeRatio(global, indCode == "ED1")
ed1Ratio1 <- spreadRatio(global, indCode == "ED1") 
ed1Ratio2 <- blankRatio()

#education - secondary school
ed2Range <- rangeRatio(global, indCode == "ED2")
ed2Ratio1 <- spreadRatio(global, indCode == "ED2") 
ed2Ratio2 <- blankRatio()

#income & work - societal poverty
iw1Range <- rangeRatio(global, indCode == "IW1")
iw1Ratio1 <- spreadRatio(global, indCode == "IW1") 
iw1Ratio2 <- blankRatio()

#income & work - youth NEET
iw2Range <- rangeRatio(global, indCode == "IW2")
iw2Ratio1 <- spreadRatio(global, indCode == "IW2") 
iw2Ratio2 <- blankRatio()

#water - drinking
wa1Range <- rangeRatio(global, indCode == "WA1")
wa1Ratio1 <- spreadRatio(global, indCode == "WA1") 
wa1Ratio2 <- blankRatio()
 
#water - sanitation
wa2Range <- rangeRatio(global, indCode == "WA2")
wa2Ratio1 <- spreadRatio(global, indCode == "WA2") 
wa2Ratio2 <- blankRatio()

#energy - electricity
en1Range <- rangeRatio(global, indCode == "EN1")
en1Ratio1 <- spreadRatio(global, indCode == "EN1") 
en1Ratio2 <- blankRatio()

#energy - indoor fuels
en2Range <- rangeRatio(global, indCode == "EN2")
en2Ratio1 <- spreadRatio(global, indCode == "EN2") 
en2Ratio2 <- blankRatio()

#connectivity - public transport
co1Range <- rangeRatio(global, indCode == "CO1")
co1Ratio1 <- spreadRatio(global, indCode == "CO1") 
co1Ratio2 <- blankRatio()

#connectivity - internet
co2Range <- rangeRatio(global, indCode == "CO2")
co2Ratio1 <- spreadRatio(global, indCode == "CO2") 
co2Ratio2 <- blankRatio()

#housing - urban slums
ho1Range <- rangeRatio(global, indCode == "HO1")
ho1Ratio1 <- blankRatio() 
ho1Ratio2 <- spreadRatio(global, indCode == "HO1")

#equality - gender inequality
eq1Range <- rangeRatio(global, indCode == "EQ1")
eq1Ratio1 <- spreadRatio(global, indCode == "EQ1") 
eq1Ratio2 <- blankRatio()

#equality - racial inequality
eq2Range <- rangeRatio(global, indCode == "EQ2")
eq2Ratio1 <- spreadRatio(global, indCode == "EQ2") 
eq2Ratio2 <- blankRatio()

#social cohesion - social support
sc1Range <- rangeRatio(global, indCode == "SC1")
sc1Ratio1 <- spreadRatio(global, indCode == "SC1") 
sc1Ratio2 <- blankRatio()

#social cohesion - palma
sc2Range <- rangeRatio(global, indCode == "SC2")
sc2Ratio1 <- spreadRatio(global, indCode == "SC2") 
sc2Ratio2 <- blankRatio()

#political voice
pv1Range <- rangeRatio(global, indCode == "PV1")
pv1Ratio1 <- blankRatio() 
pv1Ratio2 <- spreadRatio(global, indCode == "PV1")

#peace & justice - corruption
pj1Range <- rangeRatio(global, indCode == "PJ1")
pj1Ratio1 <- spreadRatio(global, indCode == "PJ1") 
pj1Ratio2 <- blankRatio()

#peace & justice - homicides
pj2Range <- rangeRatio(global, indCode == "PJ2")
pj2Ratio1 <- spreadRatio(global, indCode == "PJ2") 
pj2Ratio2 <- blankRatio()


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
			cc2 = list(cc2Range[[3]][i], cc2Range[[4]][i]),
			oa1 = list(oa1Range[[3]][i], oa1Range[[4]][i]),
			oa2 = list(oa1Range[[3]][i], oa1Range[[4]][i]),
			cp1 = list(cp1Range[[3]][i], cp1Range[[4]][i]),
			cp2 = list(cp1Range[[3]][i], cp1Range[[4]][i]),
			np1 = list(np1Range[[3]][i], np1Range[[4]][i]),
			np2 = list(np2Range[[3]][i], np2Range[[4]][i]),
			ap1 = list(ap1Range[[3]][i], ap1Range[[4]][i]),
			ap2 = list(ap1Range[[3]][i], ap1Range[[4]][i]),
			fd1 = list(fd1Range[[3]][i], fd1Range[[4]][i]),
			fd2 = list(fd2Range[[3]][i], fd2Range[[4]][i]),
			lc1 = list(lc1Range[[3]][i], lc1Range[[4]][i]),
			lc2 = list(lc1Range[[3]][i], lc1Range[[4]][i]),
			bb1 = list(bb1Range[[3]][i], bb1Range[[4]][i]),
			bb2 = list(bb2Range[[3]][i], bb2Range[[4]][i]),
			od1 = list(od1Range[[3]][i], od1Range[[4]][i]),
			od2 = list(od1Range[[3]][i], od1Range[[4]][i])
		),
		series1 = list(
			cc1 = pullVars(cc1Ratio1, i),
			cc2 = pullVars(cc2Ratio1, i),
			oa1 = pullVars(oa1Ratio1, i),
			oa2 = pullVars(oa1Ratio1, i),
			cp1 = pullVars(cp1Ratio1, i),
			cp2 = pullVars(cp1Ratio1, i),
			np1 = pullVars(np1Ratio1, i),
			np2 = pullVars(np2Ratio1, i),
			ap1 = pullVars(ap1Ratio1, i),
			ap2 = pullVars(ap1Ratio1, i),
			fd1 = pullVars(fd1Ratio1, i),
			fd2 = pullVars(fd2Ratio1, i),
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
wldJSON <- toJSON(doughnutNest, pretty = TRUE, auto_unbox=TRUE, digits=2)  #
#write(wldJSON, "./myData/6_20250108_globalDoughnut.json")
#-------------------------------------------------------------------------------------

#NOTE, USE VISUAL STUDIO CODE TO CLEAN UP JSON FILE BEFORE LOADING ON OBSERVABLE PLATFORM
# (1) REPLACE NAs with 1.00001
# (2) REPLACE EQ2 AND HO2 [INF,-INF] RANGES WITH [0,1]



