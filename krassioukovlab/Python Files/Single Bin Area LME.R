# Load required libraries
library(lme4)       # For mixed models
library(lmerTest)   # Adds p-values to lmer output
library(emmeans)    # For estimated marginal means and post hoc tests
library(readr)      # For CSV I/O
library(dplyr)      # For clean data manipulation

# ---- STEP 1: Read the CSV file ----
# (make sure you provide the correct path to your CSV)
df <- read_csv("All FFT Areas 1 Bins 0.1 Range.csv")

# ---- STEP 2: Fit the Linear Mixed Effects Model ----
# "Area Under FFT" = dependent variable
# "Data Group" = fixed effect (repeated-measure condition)
# "Animal Name" = random effect (since each animal has repeated measures)
model <- lmer(`Area Under FFT` ~ `Data Group` + (1 | `Animal Name`), data = df)

# ---- STEP 3: Extract Estimated Marginal Means ----
emm <- emmeans(model, specs = ~ `Data Group`)
emm_df <- as.data.frame(emm)  # Model-adjusted means

# ---- STEP 4: Pairwise comparisons (post-hoc test) ----
pw <- pairs(emm, adjust = "tukey")
pw_df <- as.data.frame(pw)

# ---- STEP 5: Save both to CSV so Python can read them ----
write_csv(emm_df, "All FFT Areas 1 Bins 0.1 Range emm_df.csv")
write_csv(pw_df, "All FFT Areas 1 Bins 0.1 Range pw_df.csv")
