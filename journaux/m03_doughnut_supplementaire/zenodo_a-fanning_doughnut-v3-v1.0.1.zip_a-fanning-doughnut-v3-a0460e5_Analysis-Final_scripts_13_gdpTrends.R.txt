#This script calculates trends in GDP growth rates (total and per capita) for the world and country clusters

#create chart of country groups by average GNI per capita over the 2000-2022 period
myDat1 <- read_csv("./cleanData/001_nationalGNIperCap-Population_2000-2022_n193.csv") %>%
  select(-b40m40t20)

#global
wld <- myDat1 %>%
  rowwise() %>%
  mutate(GNI = GNIperCap*population) %>%
  ungroup() %>%
  group_by(date) %>%
  summarise(population = sum(population),
    GNI = sum(GNI)) %>%
  ungroup() %>%
  rowwise() %>%
  mutate(GNIperCap = GNI/population) %>%
  ungroup() %>%
  add_column(group = "World", grpCode = "WLD") %>%
  relocate(group, grpCode)

#groups
grp <- myDat1 %>%
  rowwise() %>%
  mutate(GNI = GNIperCap*population) %>%
  ungroup() %>%
  group_by(b40m40t20_ts, date) %>%
  summarise(population = sum(population),
    GNI = sum(GNI)) %>%
  ungroup() %>%
  rowwise() %>%
  mutate(GNIperCap = GNI/population,
    group = ifelse(b40m40t20_ts == 1, "Poorest 40% of countries", ifelse(
      b40m40t20_ts == 2, "Middle 40% of countries", "Richest 20% of countries")),
    grpCode = ifelse(b40m40t20_ts == 1, "B40", ifelse(
      b40m40t20_ts == 2, "M40", "T20"))) %>%
  ungroup() %>%
  relocate(group, grpCode) %>%
  select(-b40m40t20_ts)

#join
dat <- rbind(wld, grp) %>%
  mutate(group = factor(group, levels=c("World", "Richest 20% of countries", "Middle 40% of countries", "Poorest 40% of countries")),
    grpCode = factor(grpCode, levels=c("WLD", "T20", "M40", "B40")))

rm(wld,grp, myDat1)
#----------------------------------------------------------------------------
#quick visualise
ggplot(dat %>% filter(grpCode != "WLD"), aes(x=date, y=GNIperCap)) +
  geom_line(size=1) +
  geom_smooth(method="lm") +
  facet_wrap(~group) +
  theme_bw()

ggplot(dat %>% filter(grpCode != "WLD"), aes(x=date, y=GNI, fill=grpCode)) +
  geom_area() +
  theme_bw()
#----------------------------------------------------------------------------
#calculate GNI per Cap exponential growth rates statistically
#little functions to fit lm models by year
mod_GNI <- function(data){
  lm(log(GNI) ~ date, data=data)
}

mod_GNIperCap <- function(data){
  lm(log(GNIperCap) ~ date, data=data)
}

#estimate lm models by group and extract coefficients and fitted values
mods_GNI <- dat %>%
  group_nest(group, grpCode) %>%
  mutate(model = map(data, mod_GNI), 
    glance = map(model, broom::glance),
    tidy = map(model, broom::tidy),
    augment = map(model, broom::augment))

mods_GNIperCap <- dat %>%
  group_nest(group, grpCode) %>%
  mutate(model = map(data, mod_GNIperCap), 
    glance = map(model, broom::glance),
    tidy = map(model, broom::tidy),
    augment = map(model, broom::augment))

mods_GNI %>% unnest(tidy) %>% filter(term=="date")
mods_GNIperCap %>% unnest(tidy) %>% filter(term=="date")

rm(mod_GNIperCap, mod_GNI, mods_GNI, mods_GNIperCap)
#----------------------------------------------------------------------------
#calculate total % growth over the period
tot_GNI <- dat %>% 
  select(-population, -GNIperCap) %>%
  filter(date %in% c(2000, 2022)) %>%
  pivot_wider(names_from=date, values_from=GNI) %>% 
  rowwise() %>%
  mutate(pctChange = (`2022`-`2000`)/`2000`) %>%
  ungroup()
  
tot_GNIperCap <- dat %>% 
  select(-population, -GNI) %>%
  filter(date %in% c(2000, 2022)) %>%
  pivot_wider(names_from=date, values_from=GNIperCap) %>% 
  rowwise() %>%
  mutate(pctChange = (`2022`-`2000`)/`2000`) %>%
  ungroup()
