# --- R CODE ---

library(lme4)
library(lmerTest)  # p-values for fixed effects
library(emmeans)
library(dplyr)
library(purrr)
library(tidyr)
library(broom)


# Load your FFT area data
df <- read.csv("All FFT Areas 5 Bins 0.5 Range.csv", stringsAsFactors = FALSE)



# Pick one bin to debug
single_bin_df <- df %>% filter(Frequency.Bin == "1")

# Fit the model for that bin
single_bin_model <- lmer(Area.Under.FFT ~ Data.Group + (1 | Animal.Name), data = single_bin_df)

# Get the emmeans object
single_bin_emm <- emmeans(single_bin_model, ~ Data.Group)

# Now, inspect the output of pairs() directly
# This output should be a special 'emmeans' object
pairs_output <- pairs(single_bin_emm, adjust = "holm")

# Print the output to see the p-values directly
print(pairs_output)

tidy_output <- broom::tidy(pairs_output)
print(tidy_output)

View(tidy_output)















# Filter out rows with NA FrequencyBins (if any)
df <- df %>%
  filter(!is.na(Frequency.Bin))

# Factor setup
df <- df %>%
  mutate(
    DataGroup    = factor(Data.Group), # Levels are now determined alphabetically
    FrequencyBin = factor(Frequency.Bin),
    AnimalName.  = factor(Animal.Name)
  )

# Per-bin modeling
pairwise_results <- df %>%
  group_by(Frequency.Bin) %>%
  nest() %>%
  mutate(
    model = map(data, ~ lmer(Area.Under.FFT ~ Data.Group + (1 | Animal.Name), data = .x)),
    emm  = map(model, ~ emmeans(.x, ~ Data.Group)),
    pw   = map(emm, ~ broom::tidy(pairs(.x, adjust = "holm")))
  ) %>%
  select(Frequency.Bin, pw) %>%
  unnest(pw)

# Save results for Python
write.csv(pairwise_results, "pairwise_results.csv", row.names = FALSE)