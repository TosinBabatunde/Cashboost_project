import numpy as np # python library for working with numbers#
import pandas as pd # python library for working with dataframes (tables)#
from scipy import stats # python library for statistics#
from statsmodels.stats.power import TTestIndPower # python library for power analysis#
import warnings # python library for handling warnings#
warnings.filterwarnings('ignore') # ignore warnings#    

np.random.seed(91) # set the random seed for reproducibility    


# Step 1: Power Analysis to Determine Sample Size

# Learning Notes:
# COHEN'S D calculates how big a change we expect to see given the s.d of the data.#
# e.g. if the s.d of the data is 1, and we expect to see a change of 0.5, then the effect size (Cohen's d) would be 0.5.#
# POWER is the probablity of detecting if there is a real effect # 
# A power of 0.8 means that we have an 80% chance of detecting an effect if there is one.#
# In stats terms, we want to have a power of at least 0.8 to be confident that we can detect an effect if there is one.#
# The significance level (ALPHA) is the threshold for determining statistical significance.#
# A common alpha level is 0.05, which means that we are willing to accept a 5% chance of incorrectly rejecting the null hypothesis# 
# (i.e., finding a false positive).#
# Doing a two-sided test means that we are looking for an effect in either direction (positive or negative).#

#average monthly income of farmers in USD before program starts
baseline_mean = 120
expected_effect = 0.1666 # we expect a 16.66% increase in income due to the program (increase of $20 on a baseline of $120)#
std_dev = 60 # standard deviation of income in the population; spread of income data ($60 means that most farmers' income will be within $60 of the mean )

effect_size = expected_effect * baseline_mean / std_dev # calculate Cohen's d (effect size) effect size here is 0.333#
alpha = 0.05 # significance level
power = 0.8 # desired power

N = 1200 # total sample size (number of farmers) available for the A/B test#

# print(f"Effect Size (Cohen's d): {effect_size:.3f}") # print the calculated effect size#

analysis = TTestIndPower() # create an instance of the TTestIndPower class for power analysis#
sample_size = analysis.solve_power(
    effect_size=effect_size, 
    alpha=alpha, 
    power=power,
    alternative='two-sided'
) # calculate the required sample size for the A/B test#    

# print the required sample size per group (control and treatment)#
# print (f"Minimum Sample Size per Group: {int(np.ceil(sample_size))}") 
#prints minimum sample size per group, rounded up to the nearest whole number#
# print (f"Total Minimum Sample Size: {int(np.ceil(sample_size) * 2)}") 
#prints total minimum sample size for both groups (control and treatment), rounded up to the nearest whole number#

# Creating the Farmer profiles

regions = ['North', 'Central', 'South'] # define the regions where the farmers are located#
farm_sizes = ['Small (<1 ha)', 'Medium (1-3 ha)', 'Large (>3 ha)'] # define the farm sizes (small, medium, large)#  
enrollment_cohorts = ["2023-Q1", "2023-Q3", "2024-Q1", "2024-Q3"] # define the enrollment cohorts based on the quarter of enrollment#
farmer_ids = [f"FRM-{str(i).zfill(4)}" for i in range(1, N + 1)] # create a range of farmer IDs from 1 to N(1200) formatting as FRM-0001, FRM-0002, etc.#
# str(i) converts the integer i to a string #
# zfill(4) pads the string with zeros on the left to ensure it is 4 characters long.#
# range(1, N + 1) generates numbers from 1 to N (inclusive) for the farmer IDs#
# for i in range(1, N + 1) iterates through the numbers from 1 to N to create the farmer IDs#
# [] creates a list of farmer IDs#

# print(farmer_ids[:5]) # print the first 5 farmer IDs to verify the format#

region_col = np.random.choice(regions, size=N, p=[0.35, 0.40, 0.25]) 
# randomly assign regions to farmers based on specified probabilities 35% North, 40% Central, 25% South #

farm_size_col = np.random.choice(farm_sizes, size=N, p=[0.50, 0.35, 0.15])
# randomly assign farm sizes to farmers based on specified probabilities 50% Small, 35% Medium, 15% Large #

enrollment_cohort_col = np.random.choice(enrollment_cohorts, size=N, p=[0.30, 0.25, 0.25, 0.20])
# randomly assign enrollment cohorts to farmers based on specified probabilities 30% 2023-Q1, 25% 2023-Q3, 25% 2024-Q1, 20% 2024-Q3 #

age_col = np.random.randint(22, 65, size=N)
# randomly assign ages to farmers between 22 and 64 (inclusive) #

female_col = np.random.binomial(1, 0.42, size=N)
# randomly assign gender to farmers (1 for female, 0 for male) based on a 42% probability of being female #

household_size_col = np.random.randint(2, 9, size=N)
# randomly assign household sizes to farmers between 2 and 8 (inclusive) #

# Create a DataFrame to hold the farmer profiles

df = pd.DataFrame({
    'farmer_id': farmer_ids,
    'region': region_col,
    'farm_size': farm_size_col,
    'enrollment_cohort': enrollment_cohort_col,
    'age': age_col,
    'female': female_col,
    'household_size': household_size_col
})

# Display the first few rows of the DataFrame to verify the farmer profiles
# print(df.head())
# print(f"\nShape: {df.shape}") # print the shape of the DataFrame to verify the number of rows and columns#

# Baseline Income

farm_income_boost = {
    'Small (<1 ha)': 0, # 0 increase in income
    'Medium (1-3 ha)': 25, # income increase by 25 USD
    'Large (>3 ha)': 55 # income increase by 55 USD
}   

region_income_boost = {
    'North': -10, # income decrease by 10 USD as North is more Arid and less productive#
    'Central': 0, # income remains the same in the Central region#
    'South': 15 # income increase by 15 USD as South is more fertile (better soil) and closer to markets
}

baseline_income = (
    100
    + df['farm_size'].map(farm_income_boost) # add income boost based on farm size#
    + df['region'].map(region_income_boost) # add income boost based on region  
    + np.random.normal(0, 40, size=N) # add random noise to the baseline income based on the standard deviation#
).clip(20, 400) # ensure that the baseline income is between 20 and 400 USD#

df["baseline_income_usd"] = baseline_income.round(2) # add the baseline income column to the DataFrame#

df["baseline_food_security_score"] = (
    np.random.uniform(2.0, 7.0, size=N) # generate random baseline food security scores between 2 and 7 (on a scale of 1 to 10)
).clip(1, 10).round(2) # add a baseline food security score between 1 and 10, rounded to 2 decimal places#

df["baseline_farm_output_kg"] = (
    200
    + df['farm_size'].map({'Small (<1 ha)': 0, 'Medium (1-3 ha)': 150, 'Large (>3 ha)': 400}) # add farm output boost based on farm size#
    + np.random.normal(0, 80, size=N) # add random noise to the baseline farm output based on the standard deviation#
).clip(50, 1500).round(1) # ensure that the baseline farm output is between 50 and 1500 kg#

# print the first few rows of the DataFrame with selected columns to verify the baseline data#

#print(df[['farmer_id', 'region', 'farm_size', 'baseline_income_usd', 
          #'baseline_food_security_score', 'baseline_farm_output_kg']].head(20)) 

# print(df[['farmer_id', 'region', 'farm_size', 'baseline_income_usd', 
          #'baseline_food_security_score', 'baseline_farm_output_kg']][df['region'] == 'Large (>3 ha)'].head(20)) 

# RANDOMIZATION
# Using stratified random sampling to assign farmers to control and treatment groups while ensuring balance across regions and farm sizes#

treatment_col = np.zeros(N, dtype=int) 
# initialize a column of zeros to represent the treatment assignment (0 for control, 1 for treatment)#

# We will loop through each combination of region and farm size to assign farmers to treatment and control groups within each stratum (combination of region and farm size)#
# This ensures that we have a balanced representation of farmers from different regions and farm sizes in both the treatment and control groups#

for (reg, size), group in df.groupby(['region', 'farm_size']): 
    idx = group.index.tolist() # get the indices of the farmers in the current stratum (combination of region and farm size)#

    # e.g. where region = North and farm size = Small (<1 ha), we get the indices of all farmers in that stratum to assign them to treatment and control groups#
    # print(idx) # print the indices of the farmers in the current stratum to verify the grouping#

# We will assign 50% of the farmers in each stratum to the treatment group and 50% to the control group#

    n_treat = round(len(idx)*0.5) # calculate the number of farmers to assign to the treatment group (50% of the stratum)#
# round() is used to round the number to the nearest integer#

# This goes into the idx list that contains the indices (row numbers) of the farmers in each stratum (region, farm size)#
# Calculates the number of indices in each stratum and then divides by 2 (* 0.5) to get the number of farmers to assign to treatment

    chosen_idx = np.random.choice(idx, size=n_treat, replace=False)
# this is randomly selecting indices from the stratum (region, farm size) to assign to the treatment group without replacement (replace=False)#
# it is assigning the number of farmers calculated in n_treat#
#replace=False ensures that we do not select the same farmer more than once for the treatment group#
# e.g. from the indices of farmers in the North and Small (<1 ha) stratum, we randomly select 50% of them to be in the treatment group#

    treatment_col[chosen_idx] = 1 # assign the selected indices to the treatment group (set to 1)#
# e.g. the randomly selected farmers in the North and Small (<1 ha) stratum will have their treatment_col value set to 1, indicating they are in the treatment group#
# This takes those indices assigned in chosen_idx and then sets the corresponding rows in the treatment column to 1#

df['treatment'] = treatment_col # add the treatment assignment column to the DataFrame#

df['group'] = df['treatment'].map({1: 'Treatment', 0: 'Control'}) # create a new column to label the groups as 'Treatment' or 'Control' based on the treatment assignment#

# print(df['group'].value_counts()) # print the count of farmers in each group to verify the randomization#'])
# value_counts() counts the number of occurrences of each unique value in the 'group' column, which should show a roughly equal number of farmers in the Treatment and Control groups due to the randomization process#

# print(df.groupby(['region', 'farm_size', 'group']).size().unstack())
# print the count of farmers in each group (Treatment and Control) for each combination of region and farm size to verify the stratified randomization#
# Used size() to count the number of farmers in each group for each combination of region and farm size, and unstack() to reshape the output for better readability#
# Did not use value_counts() here because we want to see the counts for each combination of region and farm size, which is better achieved with groupby() and size() rather than value_counts()#

# BALANCE CHECK
# We will check the balance of key baseline characteristics
# This is important to ensure that the randomization process has successfully created comparable groups (Treatment and Control) in terms of important variables such as age
# comparable groups just means that each group has a similar distribution of each key variables at baseline, age is not skewed in one group compared to the other, etc.#
# We will calculate the t-test for each variable to compare the means between the Treatment and Control groups and check for any significant differences at baseline#

print('BALANCE CHECK')
print('=' * 60) # print a separator for better readability#

# Key baseline characteristics to check for balance between Treatment and Control groups

balance_vars = [
    'age',
    'female',
    'household_size',
    'baseline_income_usd',
    'baseline_food_security_score',
    'baseline_farm_output_kg'
]

for var in balance_vars:
    treat = df[df['treatment'] == 1] [var]
    control = df[df['treatment'] == 0] [var]
    _, p_value = stats.ttest_ind(treat, control) # perform an independent t-test to compare the means of the variable between the Treatment and Control groups#
    # _, p_value captures the t-statistic and p-value from the t-test, but we only need the p-value for the balance check#
    # _, tells python to ignore the t-stat and only capture the p-value#
    status = 'Balanced' if p_value > alpha else 'Not Balanced' # determine if the variable is balanced based on the p-value and the significance level (alpha)#
    # if the p-value is greater than alpha (0.05), we consider the variable to be balanced between the groups; otherwise, it is not balanced#
#     print(f"{var:<35} p= {p_value:.3f} {status}") # print the variable name, p-value, and balance status, formatting the variable name to be left-aligned with a width of 35 characters and the p-value to be rounded to 3 decimal places#

# print("\nALL p > 0.05 means no significant baseline differences - randomization successful.") # print a message to explain the interpretation of the balance check results#
# # \n is used to add a new line for better readability in the output#

#Greenlight project once all key baseline variables are balanced (p > 0.05) between the Treatment and Control groups, indicating that the randomization process was successful in creating comparable groups for the A/B test#

# ENDLINE OUTCOMES

size_multiplier = df['farm_size'].map({
    'Small (<1 ha)': 1.3, 
    'Medium (1-3 ha)': 1.0, 
    'Large (>3 ha)': 0.7
    })

endline_income = (
    df['baseline_income_usd'] 
    + df['treatment'] * 22 * size_multiplier #this is the treatment effect on income, which is $22 increase for the treatment group, adjusted by a multiplier based on farm size (small farms get a bigger boost, large farms get a smaller boost)#
    + np.random.normal(0, 35, size=N) # add random noise to the endline income based on the standard deviation#
).clip(20, 500).round(2) # ensure that the endline income is between 20 and 500 USD#

endline_food = (
    df['baseline_food_security_score']
    + df['treatment'] * 0.8 # this is the treatment effect on food security score, which is a 0.8 point increase for the treatment group#
    + np.random.normal(0, 0.6, size=N) # add random noise to the endline food security score based on the standard deviation#
).clip(1, 10).round(2) # ensure that the endline food security score is between 1 and 10, rounded to 2 decimal places#

endline_output = (
    df['baseline_farm_output_kg']
    + df['treatment'] * 85 * size_multiplier # this is the treatment effect on farm output, which is a 180 kg increase for the treatment group#
    + np.random.normal(0, 60, size=N) # add random noise to the endline farm output based on the standard deviation#
).clip(50, 2000).round(1) # ensure that the endline farm output is between 50 and 2000 kg, rounded to 1 decimal place#

df['endline_income_usd'] = endline_income # add the endline income column to the DataFrame#
df['endline_food_security_score'] = endline_food # add the endline food security score column to the DataFrame#
df['endline_farm_output_kg'] = endline_output # add the endline farm output column to the DataFrame#

df['income_change_usd'] = (
    df['endline_income_usd'] - df['baseline_income_usd'] # calculate the change in income from baseline to endline and add it as a new column to the DataFrame#
).round(2) # round the income change to 2 decimal places#

df['sessions_attended'] = np.where(
    df['treatment'] == 1, 
    np.random.binomial(6, 0.78, size=N), # for the treatment group, randomly assign the number of sessions attended based on a binomial distribution with 6 sessions and a 78% attendance rate#
    np.nan # control group does not attend any sessions, so we set it to NaN (not a number)
)

# print(
#     df[['farmer_id', 'region', 'farm_size', 'group', 'baseline_income_usd', 
#         'endline_income_usd', 'income_change_usd', 'sessions_attended']].head(10)
#     ) # print the first few rows of the DataFrame to verify the endline outcomes and the calculated change in income#

# print(
#     df[['farmer_id', 'region', 'farm_size', 'group', 'baseline_income_usd', 
#         'endline_income_usd', 'income_change_usd', 'sessions_attended']][df['group'] == 'Treatment'].head(10)
#     ) # print the first few rows of Treatment group to verify the endline outcomes and the calculated change in income for the Treatment group#

# print(
#     df.groupby('group')['income_change_usd'].mean().round(2)
# )
# print the average change in income for the Treatment and Control groups to verify that the treatment group has a higher average increase in income compared to the control group#

# SAVE DATASET

df.to_csv('cashboost_dataset.csv', index=False) # save the DataFrame to a CSV file without the index column#
# Index column is the first column pandas creates automatically to number your rows, we set index=False to avoid saving this column in the CSV file since we already have a unique farmer_id column that serves as an identifier for each row#

print(f"\nDataset saved as 'cashboost_dataset.csv' with {df.shape[0]} rows and {df.shape[1]} columns.") # print a message to confirm that the dataset has been saved and display the number of rows and columns in the saved dataset#
# df.shape[0] gives the number of rows in the DataFrame, and df.shape[1] gives the number of columns in the DataFrame, which we include in the print statement to confirm the dimensions of the saved dataset#

print(f"Rows: {len(df)} Columns: {len(df.columns)}") # print the number of rows and columns in the DataFrame to verify the dimensions of the dataset#

