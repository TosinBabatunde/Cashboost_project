#import sys
#print("PYTHON VERSION:", sys.version)
#print("PYTHON PATH:", sys.executable)

import pandas as pd
import numpy as np
from scipy import stats
import duckdb
import matplotlib.pyplot as plt #Python plotting library"
import seaborn as sns #on top of matplotlib, produces better charts - stat viz#
import warnings
warnings.filterwarnings("ignore")

#Load data from staging for analysis#
import os #this is to get the path of the current script and join it with the database file name to create the full path to the database file

script_dir = os.path.dirname(os.path.abspath(__file__)) #os.path.dirname(os.path.abspath(__file__)) gets the directory of the current script file. os.path.abspath(__file__) gives the absolute path of the current script file
# and os.path.dirname() extracts the directory part of that path. This is useful for constructing paths to other files relative to the script's location.    
db_path = os.path.join(script_dir, "cashboost.duckdb") # this is to create the full path to the database file by joining the script directory with the database file name. This ensures that the code can find the database file regardless of where the script is run from.


con = duckdb.connect(db_path) # This is to connect to the DuckDB database using the full path to the database file. The connection object con is used to execute SQL queries and retrieve data from the database.
#print(con.execute("SHOW ALL TABLES").df())
df = con.execute("SELECT * FROM stg_cashboost_farmers").df()
con.close() # close the connection to the DuckDB database after retrieving the data. This is important to free up resources and avoid potential issues with too many open connections.

# print(df.head())

# DEFINING TREATMENT AND CONTROL GROUPS
# filtering: first filter the dataframe to include only rows where the treatment or control columns (is equal to 1 , and select their "income_change_usd" column as well. 
treatment = df[df["treatment"] == 1]["income_change_usd"] 
control = df[df["treatment"] == 0]["income_change_usd"]

# print (f"Treatment farmers: {len(treatment)}")
# print (f"Control farmers: {len(control)}") 
# print (f"\nTreatment avg income change: ${treatment.mean():.2f}")
# print (f"Control avg income change: ${control.mean():.2f}")
# print (f"Raw difference: ${treatment.mean() - control.mean():.2f}")

# T - TEST & P - VALUE : Is the test result statistically significant? (p < 0.05)
# this is to perform a two-sample t-test to compare the means of the treatment and control groups. 

t_stat, p_value = stats.ttest_ind(treatment, control) #running and independent t-test because the two groups are independent of each other.

print("T-TEST RESULTS")
print("=" * 40)
print(f"T-statistic: {t_stat:.4f}")
print(f"P-value: {p_value:.4f}")

if p_value < 0.05:
    print("\n Result is statistically significant (p < 0.05)")
    print(" The income difference is unlikely to be due to random chance, suggesting that the treatment had an effect.")
    print(f"Treatment farmers experienced a statistically significant increase in monthly income compared to control farmers (t={t_stat:.4f}, p={p_value:.4f}).")
else:
    print("\n Result is NOT statistically significant (p >= 0.05)")
    print(" The income difference could be due to random chance, suggesting that the treatment may not have had a significant effect.")

# EFFECT SIZE (COHEN'S D): Is the effect meaningful?
# this is to calculate the effect size using Cohen's d, which measures the standardized difference between two groups
def cohens_d(group1, group2):
    diff = group1.mean() - group2.mean()
    pooled_std = np.sqrt((group1.std() ** 2 + group2.std() ** 2) / 2) # sqrt of (group1 std.^2 + group2 std.^2) / 2
    return diff / pooled_std

# Calculate Cohen's d
d = cohens_d(treatment, control)

print("\nEffect Size")
print("=" * 40)
print(f"Cohen's d: {d:.4f}")

if abs(d) < 0.2:
    print("Negligible effect size")
elif abs(d) < 0.5:
    print("Small effect size")
elif abs(d) < 0.8:
    print("Medium effect size")
else:
    print("Large effect size")

print(f"\nThe program produced a medium-sized effect (Cohen's d = {d: .4f}), indicating a practically meaningful improvemnet in household income beyond what we would expect by chnace.")

# Confidence Intervals: How precise is the estimate of the effect?
# this is to calculate the 95% confidence intervals for the treatment and control groups, 
# Which provides a range of values within which we can be 95% confident that the true mean lies. This helps to understand the precision of the estimated effect.

from scipy.stats import t as t_dist

def confidence_interval(group1, group2, confidence=0.95):
    diff = group1.mean() - group2.mean() #observed difference in means
    se =np.sqrt(group1.var()/len(group1) + group2.var()/len(group2)) # standard error of the difference in means, this is calculating how much variability we can expect in the difference between the two group means due to sampling error. It takes into account the variance of each group and their respective sample sizes.
    df = len(group1) + len(group2) - 2 # degrees of freedom 

   # margin of error, finds the t_value that captures 95% of the distribution. 
   # ppf is the percent point function (inverse of p-value) for the t-distribution. 
   # 1 + confidence (0.05) / 2 gives the cumulative probability for the two-tailed test.
   # we multiply by the standard error to get the margin of error for the confidence interval.
    margin = t_dist.ppf((1 + confidence) / 2, df) * se 

    return diff - margin, diff + margin # returns the lower and upper bounds of the confidence interval for the difference in means between the two groups.

lower, upper = confidence_interval(treatment, control)

print("\n CONFIDENCE INTERVAL (95%)")
print("=" * 40 )
print(f"Observed difference: ${treatment.mean() - control.mean():.2f}")
print(f"95% Confidence Interval: (${lower:.2f}, ${upper:.2f})") 
print(f"\n We are 95% confident the true program effect")
print(f"   is between ${lower:.2f} and ${upper:.2f} per month.")

print(f"\n The CashBooost program produced an estimated monthly income increase of ${treatment.mean() - control.mean():.2f}")
print(f"      95% CI: ${lower:.2f} - ${upper:.2f}, a statistically significant and practically meaningful result")

# VISUALIZATION: Distribution of Income Change

sns.set_theme(style="whitegrid") #sets a clean visual style for all charts, whitegrid just gives a white background
fig, axes = plt.subplots(1,2, figsize=(12, 5)) #creates a figure with 1 row and 2 columns of subplots, with a total size of 12 inches by 5 inches
fig.suptitle("CashBoost Program - Income Change Analysis", fontsize=16, fontweight="bold") #adds a Title to the entire figure, with a font size of 16

# First chart is a boxplot

sns.boxplot(
    data = df,
    x = "treatment_group",
    y = "income_change_usd",
    hue = "treatment_group", # Changes the color of the boxplot based on the group (treatment or control)
    palette = {"Treatment": "#2ecc71", "Control": "#e74c3c"}, #Treatment group is green, control group is red
    ax=axes[0] # First subplot (left side) of the figure, which is the boxplot
)
axes[0].set_title("Distribution of Income Change") #sets the title for the first subplot (boxplot)
axes[0].set_xlabel("Treatment Group") #sets the x-axis label for the first subplot (boxplot)
axes[0].set_ylabel("Income Change (USD)") #sets the y-axis label for the first subplot (boxplot)
axes[0].axhline(y=0, color="black", linestyle="--", linewidth=0.8) #adds a horizontal dashed line at y=0 to indicate no change in income

# Second chart is a barchart

means = [treatment.mean(), control.mean()]
errors = [treatment.std() / np.sqrt(len(treatment)),
          control.std() / np.sqrt(len(control))] # this is calculating the standard error of the mean for each group, which is the standard deviation divided by the square root of the sample size. This gives an estimate of how much the sample mean is expected to vary from the true population mean.
colors = ["#2ecc71", "#e74c3c"] #green for treatment, red for control
labels = ["Treatment", "Control"]

axes[1].bar(labels, means, color = colors, width=0.5, alpha=0.8)
axes[1].errorbar(labels, means, yerr=errors, fmt="none", color="black", capsize=5, linewidth=2) #adds error bars to the bar chart, representing the standard error of the mean for each group. fmt="none" means no marker is used for the error bars, ecolor="black" sets the color of the error bars to black, and capsize=5 adds caps to the ends of the error bars for better visibility.
axes[1].set_title("Average Income Change by Group") #sets the title for the second subplot (bar chart)
axes[1].set_xlabel("Treatment Group") #sets the x-axis label for the second subplot (bar chart)
axes[1].set_ylabel("Average Income Change (USD)") #sets the y-axis label for the second subplot (bar chart)
axes[1].axhline(y=0, color="black", linestyle="--", linewidth=0.8) #adds a horizontal dashed line at y=0 to indicate no change in income for the bar chart

plt.tight_layout() #adjusts the spacing between subplots to prevent overlap and ensure that all elements are clearly visible
plt.savefig(os.path.join(script_dir, "phase3_income_change_analysis.png"), dpi=150, bbox_inches='tight') #saves the figure as a PNG file with a resolution of 300 dots per inch (DPI), which is suitable for high-quality printing and presentations
plt.show() #displays the figure in a window
print("\n✓ Chart saved as phase3_income_change_analysis.png")